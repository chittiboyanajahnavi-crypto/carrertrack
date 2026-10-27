from sqlalchemy import func, distinct
from datetime import datetime
from app.extensions import db
from app.models import Student, Company, Opportunity, Application, Interview, Department


class MetricsService:
    @staticmethod
    def get_admin_metrics():
        """Calculate executive KPIs directly from database records."""
        # 1. Total counts
        total_students = db.session.query(func.count(Student.student_id)).filter(Student.is_active == True).scalar() or 0
        total_companies = db.session.query(func.count(Company.company_id)).filter(Company.is_active == True).scalar() or 0
        active_opportunities = db.session.query(func.count(Opportunity.opportunity_id)).filter(
            Opportunity.status == 'Active'
        ).scalar() or 0
        total_applications = db.session.query(func.count(Application.application_id)).scalar() or 0

        # 2. Unique selected students
        selected_students_count = db.session.query(
            func.count(distinct(Application.student_id))
        ).filter(Application.status == 'Selected').scalar() or 0

        # 3. Placement rate calculation (Denominator: Total active registered students)
        placement_rate = (
            round((selected_students_count / total_students) * 100, 2)
            if total_students > 0 else 0.0
        )

        # 4. Status distribution
        status_counts_raw = db.session.query(
            Application.status, func.count(Application.application_id)
        ).group_by(Application.status).all()
        status_distribution = [
            {'status': status, 'count': count}
            for status, count in status_counts_raw
        ]

        # 5. Department-wise placement stats
        departments = Department.query.all()
        department_stats = []
        for d in departments:
            dept_students = db.session.query(func.count(Student.student_id)).filter(
                Student.department_id == d.department_id,
                Student.is_active == True
            ).scalar() or 0

            dept_placed = db.session.query(func.count(distinct(Application.student_id))).join(
                Student, Student.student_id == Application.student_id
            ).filter(
                Student.department_id == d.department_id,
                Application.status == 'Selected'
            ).scalar() or 0

            dept_rate = round((dept_placed / dept_students) * 100, 2) if dept_students > 0 else 0.0

            department_stats.append({
                'department_id': d.department_id,
                'code': d.code,
                'name': d.name,
                'total_students': dept_students,
                'placed_students': dept_placed,
                'placement_rate': dept_rate,
            })

        # 6. Recent applications (latest 5)
        recent_apps = Application.query.order_by(Application.applied_at.desc()).limit(5).all()
        recent_applications = [
            app_item.to_dict()
            for app_item in recent_apps
        ]

        # 7. Upcoming interviews (next 5)
        upcoming_interviews_raw = Interview.query.filter(
            Interview.scheduled_at >= datetime.utcnow(),
            Interview.outcome.in_(['Pending', 'Rescheduled'])
        ).order_by(Interview.scheduled_at.asc()).limit(5).all()

        upcoming_interviews = []
        for i in upcoming_interviews_raw:
            i_dict = i.to_dict()
            if i.application:
                i_dict['student_name'] = i.application.student.full_name if i.application.student else None
                i_dict['opportunity_title'] = i.application.opportunity.title if i.application.opportunity else None
                i_dict['company_name'] = i.application.opportunity.company.name if i.application.opportunity and i.application.opportunity.company else None
            upcoming_interviews.append(i_dict)

        return {
            'kpis': {
                'total_students': total_students,
                'total_companies': total_companies,
                'active_opportunities': active_opportunities,
                'total_applications': total_applications,
                'selected_students': selected_students_count,
                'placement_rate': placement_rate,
                'placement_rate_formula': 'selected_students / total_active_students * 100',
            },
            'status_distribution': status_distribution,
            'department_stats': department_stats,
            'recent_applications': recent_applications,
            'upcoming_interviews': upcoming_interviews,
        }

    @staticmethod
    def get_student_dashboard(student_id: int):
        """Metrics and records for a student's personal portal."""
        student = db.session.get(Student, student_id)
        if not student:
            return None

        # 1. Total applications submitted by student
        my_apps = Application.query.filter_by(student_id=student_id).all()
        total_applied = len(my_apps)

        status_breakdown = {}
        for a in my_apps:
            status_breakdown[a.status] = status_breakdown.get(a.status, 0) + 1

        # 2. Upcoming interviews for this student
        app_ids = [a.application_id for a in my_apps]
        upcoming_interviews = []
        if app_ids:
            interviews_raw = Interview.query.filter(
                Interview.application_id.in_(app_ids),
                Interview.scheduled_at >= datetime.utcnow(),
                Interview.outcome.in_(['Pending', 'Rescheduled'])
            ).order_by(Interview.scheduled_at.asc()).all()

            for i in interviews_raw:
                item = i.to_dict()
                item['opportunity_title'] = i.application.opportunity.title if i.application and i.application.opportunity else None
                item['company_name'] = i.application.opportunity.company.name if i.application and i.application.opportunity and i.application.opportunity.company else None
                upcoming_interviews.append(item)

        # 3. Eligible active opportunities count
        all_active_opps = Opportunity.query.filter_by(status='Active').all()
        from app.services.eligibility_service import EligibilityService
        eligible_opps = []
        for opp in all_active_opps:
            eval_res = EligibilityService.evaluate(student_id, opp.opportunity_id)
            if eval_res['is_eligible']:
                opp_dict = opp.to_dict()
                opp_dict['can_apply'] = eval_res['can_apply']
                opp_dict['already_applied'] = eval_res['already_applied']
                eligible_opps.append(opp_dict)

        return {
            'profile': student.to_dict(),
            'total_applications': total_applied,
            'status_breakdown': status_breakdown,
            'eligible_opportunities_count': len(eligible_opps),
            'upcoming_interviews': upcoming_interviews,
            'recommended_opportunities': eligible_opps[:4],
        }
