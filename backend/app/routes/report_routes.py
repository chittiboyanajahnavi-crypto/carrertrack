import csv
from io import StringIO
from flask import Blueprint, request, make_response
from sqlalchemy import func, distinct
from app.extensions import db
from app.models import Student, Company, Opportunity, Application, Department
from app.utils.responses import success_response
from app.utils.decorators import role_required

report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@report_bp.route('/summary', methods=['GET'])
@role_required(['admin'])
def get_reports_summary():
    """Generate detailed placement and internship analytical reports with filters."""
    # Optional filters
    dept_id = request.args.get('department_id', type=int)
    grad_year = request.args.get('graduation_year', type=int)
    company_id = request.args.get('company_id', type=int)
    opp_type = request.args.get('opportunity_type', '').strip()

    # Base query for applications with joins
    app_query = db.session.query(
        Application, Student, Opportunity, Company, Department
    ).join(
        Student, Application.student_id == Student.student_id
    ).join(
        Opportunity, Application.opportunity_id == Opportunity.opportunity_id
    ).join(
        Company, Opportunity.company_id == Company.company_id
    ).join(
        Department, Student.department_id == Department.department_id
    )

    if dept_id:
        app_query = app_query.filter(Student.department_id == dept_id)
    if grad_year:
        app_query = app_query.filter(Student.graduation_year == grad_year)
    if company_id:
        app_query = app_query.filter(Opportunity.company_id == company_id)
    if opp_type:
        app_query = app_query.filter(Opportunity.opportunity_type == opp_type)

    total_filtered_applications = app_query.count()

    # Placed students in this filter scope
    placed_students_count = app_query.filter(Application.status == 'Selected').with_entities(func.count(distinct(Student.student_id))).scalar() or 0

    # Company-wise breakdown
    company_breakdown_raw = db.session.query(
        Company.name,
        func.count(Application.application_id).label('total_apps'),
        func.count(func.nullif(Application.status != 'Selected', True)).label('selections')
    ).join(Opportunity, Opportunity.company_id == Company.company_id)\
     .join(Application, Application.opportunity_id == Opportunity.opportunity_id)\
     .group_by(Company.name).all()

    company_summary = [
        {'company_name': name, 'applications_count': apps, 'selected_count': sel}
        for name, apps, sel in company_breakdown_raw
    ]

    # Opportunity type breakdown
    type_breakdown_raw = db.session.query(
        Opportunity.opportunity_type,
        func.count(Application.application_id),
        func.count(func.nullif(Application.status != 'Selected', True))
    ).join(Application, Application.opportunity_id == Opportunity.opportunity_id)\
     .group_by(Opportunity.opportunity_type).all()

    type_summary = [
        {'type': t, 'applications': apps, 'selections': sel}
        for t, apps, sel in type_breakdown_raw
    ]

    return success_response(data={
        'total_applications': total_filtered_applications,
        'placed_students': placed_students_count,
        'company_summary': company_summary,
        'opportunity_type_summary': type_summary,
    })


@report_bp.route('/export/csv', methods=['GET'])
@role_required(['admin'])
def export_csv():
    """Export complete student placement application dataset as a CSV spreadsheet."""
    records = db.session.query(
        Student.roll_number,
        Student.first_name,
        Student.last_name,
        Department.code.label('dept_code'),
        Student.graduation_year,
        Student.cgpa,
        Company.name.label('company_name'),
        Opportunity.title.label('opp_title'),
        Opportunity.opportunity_type,
        Application.status,
        Application.applied_at
    ).join(
        Application, Application.student_id == Student.student_id
    ).join(
        Opportunity, Application.opportunity_id == Opportunity.opportunity_id
    ).join(
        Company, Opportunity.company_id == Company.company_id
    ).join(
        Department, Student.department_id == Department.department_id
    ).order_by(Student.roll_number.asc(), Application.applied_at.desc()).all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow([
        'Roll Number', 'First Name', 'Last Name', 'Department',
        'Graduation Year', 'CGPA', 'Company', 'Opportunity Title',
        'Opportunity Type', 'Application Status', 'Applied Date'
    ])

    for r in records:
        writer.writerow([
            r.roll_number,
            r.first_name,
            r.last_name,
            r.dept_code,
            r.graduation_year,
            float(r.cgpa) if r.cgpa else '',
            r.company_name,
            r.opp_title,
            r.opportunity_type,
            r.status,
            r.applied_at.strftime('%Y-%m-%d %H:%M:%S') if r.applied_at else '',
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=careertrack_placement_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output
