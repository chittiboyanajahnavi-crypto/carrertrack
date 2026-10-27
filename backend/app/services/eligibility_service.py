from datetime import date
from app.models import Student, Opportunity, Application


class EligibilityService:
    @staticmethod
    def evaluate(student_id: int, opportunity_id: int):
        """
        Evaluate if a student is eligible to apply for an opportunity.
        Returns a dict with:
        - is_eligible (bool)
        - can_apply (bool) - eligible and hasn't applied yet
        - reasons (list of reasons if ineligible)
        - already_applied (bool)
        - existing_application (dict or None)
        - criteria_breakdown (dict with detailed status for each criterion)
        """
        from app.extensions import db
        student = db.session.get(Student, student_id)
        opportunity = db.session.get(Opportunity, opportunity_id)

        if not student:
            return {'is_eligible': False, 'can_apply': False, 'reasons': ['Student record not found.']}
        if not opportunity:
            return {'is_eligible': False, 'can_apply': False, 'reasons': ['Opportunity not found.']}

        reasons = []
        breakdown = {}

        # 1. Opportunity Status Check
        status_ok = opportunity.status == 'Active'
        breakdown['status'] = {
            'passed': status_ok,
            'details': f"Status is {opportunity.status} (required: Active)",
        }
        if not status_ok:
            reasons.append(f"Opportunity is currently {opportunity.status}.")

        # 2. Deadline Check
        today = date.today()
        deadline_ok = opportunity.deadline >= today
        breakdown['deadline'] = {
            'passed': deadline_ok,
            'deadline': opportunity.deadline.isoformat(),
            'details': "Application window is open" if deadline_ok else f"Application deadline passed on {opportunity.deadline}",
        }
        if not deadline_ok:
            reasons.append(f"Application deadline expired on {opportunity.deadline}.")

        # 3. CGPA Check
        student_cgpa = float(student.cgpa)
        min_cgpa = float(opportunity.min_cgpa)
        cgpa_ok = student_cgpa >= min_cgpa
        breakdown['cgpa'] = {
            'passed': cgpa_ok,
            'student_cgpa': student_cgpa,
            'min_cgpa': min_cgpa,
            'details': f"Student CGPA {student_cgpa:.2f} >= Minimum {min_cgpa:.2f}" if cgpa_ok else f"Student CGPA {student_cgpa:.2f} is below minimum requirement of {min_cgpa:.2f}",
        }
        if not cgpa_ok:
            reasons.append(f"CGPA {student_cgpa:.2f} does not meet the minimum requirement of {min_cgpa:.2f}.")

        # 4. Graduation Year Check
        grad_year_ok = student.graduation_year == opportunity.graduation_year
        breakdown['graduation_year'] = {
            'passed': grad_year_ok,
            'student_grad_year': student.graduation_year,
            'required_grad_year': opportunity.graduation_year,
            'details': f"Graduation year {student.graduation_year} matches required batch {opportunity.graduation_year}" if grad_year_ok else f"Eligible batch is {opportunity.graduation_year}, but student belongs to {student.graduation_year}",
        }
        if not grad_year_ok:
            reasons.append(f"Graduation year mismatch: Opportunity is open only for the batch of {opportunity.graduation_year}.")

        # 5. Department Eligibility Check
        eligible_dept_ids = [od.department_id for od in opportunity.opportunity_departments]
        if eligible_dept_ids:
            dept_ok = student.department_id in eligible_dept_ids
            eligible_dept_names = [od.department.name for od in opportunity.opportunity_departments if od.department]
            breakdown['department'] = {
                'passed': dept_ok,
                'student_dept': student.department.name if student.department else None,
                'eligible_depts': eligible_dept_names,
                'details': "Student's department is eligible" if dept_ok else f"Student department ({student.department.code if student.department else 'Unknown'}) is not in eligible list",
            }
            if not dept_ok:
                reasons.append(f"Your branch ({student.department.code if student.department else 'N/A'}) is not listed among eligible departments.")
        else:
            dept_ok = True
            breakdown['department'] = {'passed': True, 'details': 'All departments are eligible.'}

        # Overall Academic & Policy Eligibility
        is_eligible = status_ok and deadline_ok and cgpa_ok and grad_year_ok and dept_ok

        # 6. Check Duplicate Application
        existing_app = Application.query.filter_by(
            student_id=student_id, opportunity_id=opportunity_id
        ).first()
        already_applied = existing_app is not None
        can_apply = is_eligible and not already_applied

        if already_applied:
            reasons.append(f"You have already applied for this opportunity (Status: {existing_app.status}).")

        # 7. Skills Matching Breakdown (Informational)
        student_skill_ids = {ss.skill_id for ss in student.student_skills}
        required_skills = []
        for os_req in opportunity.opportunity_skills:
            has_skill = os_req.skill_id in student_skill_ids
            required_skills.append({
                'skill_id': os_req.skill_id,
                'skill_name': os_req.skill.name if os_req.skill else None,
                'is_mandatory': os_req.is_mandatory,
                'matched': has_skill,
            })
        breakdown['skills'] = required_skills

        return {
            'is_eligible': is_eligible,
            'can_apply': can_apply,
            'already_applied': already_applied,
            'reasons': reasons,
            'existing_application': existing_app.to_dict() if existing_app else None,
            'criteria': breakdown,
        }
