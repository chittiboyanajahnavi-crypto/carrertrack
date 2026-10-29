from datetime import date, datetime
from flask import Blueprint, request, session
from app.extensions import db
from app.models import Opportunity, Company, OpportunityDepartment, OpportunitySkill, Skill, Department
from app.services.eligibility_service import EligibilityService
from app.utils.responses import success_response, error_response
from app.utils.decorators import role_required, login_required

opportunity_bp = Blueprint('opportunities', __name__, url_prefix='/api/opportunities')


@opportunity_bp.route('', methods=['GET'])
@login_required
def list_opportunities():
    """List opportunities with filters, sorting, and optional student-specific eligibility annotations."""
    query = Opportunity.query

    # Search title, description, or company name
    search = request.args.get('search', '').strip()
    if search:
        query = query.join(Company, Opportunity.company_id == Company.company_id).filter(
            (Opportunity.title.ilike(f"%{search}%")) |
            (Opportunity.description.ilike(f"%{search}%")) |
            (Company.name.ilike(f"%{search}%"))
        )

    # Opportunity type filter
    opp_type = request.args.get('type', '').strip()
    if opp_type:
        query = query.filter(Opportunity.opportunity_type == opp_type)

    # Company filter
    company_id = request.args.get('company_id', type=int)
    if company_id:
        query = query.filter(Opportunity.company_id == company_id)

    # Status filter (default: Active for students)
    user_role = session.get('role')
    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Opportunity.status == status)
    elif user_role == 'student':
        query = query.filter(Opportunity.status == 'Active')

    # Work mode filter
    work_mode = request.args.get('work_mode', '').strip()
    if work_mode:
        query = query.filter(Opportunity.work_mode == work_mode)

    # Location filter
    location = request.args.get('location', '').strip()
    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location}%"))

    # Graduation year filter
    grad_year = request.args.get('graduation_year', type=int)
    if grad_year:
        query = query.filter(Opportunity.graduation_year == grad_year)

    # Student CGPA qualification filter (shows opportunities where min_cgpa <= given cgpa)
    cgpa_filter = request.args.get('max_min_cgpa', type=float)
    if cgpa_filter is not None:
        query = query.filter(Opportunity.min_cgpa <= cgpa_filter)

    # Department filter
    dept_id = request.args.get('department_id', type=int)
    if dept_id:
        query = query.join(OpportunityDepartment).filter(OpportunityDepartment.department_id == dept_id)

    # Skill filter
    skill_id = request.args.get('skill_id', type=int)
    if skill_id:
        query = query.join(OpportunitySkill).filter(OpportunitySkill.skill_id == skill_id)

    # Sorting
    sort_by = request.args.get('sort_by', 'deadline').strip()
    order = request.args.get('order', 'asc').strip().lower()

    if sort_by == 'title':
        sort_col = Opportunity.title
    elif sort_by == 'created_at':
        sort_col = Opportunity.created_at
    elif sort_by == 'min_cgpa':
        sort_col = Opportunity.min_cgpa
    else:
        sort_col = Opportunity.deadline

    if order == 'desc':
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    opportunities = query.all()

    student_id = session.get('student_id') if user_role == 'student' else None
    results = []
    for opp in opportunities:
        opp_data = opp.to_dict(include_details=True)
        if student_id:
            eval_result = EligibilityService.evaluate(student_id, opp.opportunity_id)
            opp_data['is_eligible'] = eval_result['is_eligible']
            opp_data['can_apply'] = eval_result['can_apply']
            opp_data['already_applied'] = eval_result['already_applied']
            opp_data['skills_match_score'] = eval_result.get('skills_match_score', 0)
            opp_data['ineligibility_reasons'] = eval_result['reasons']
        results.append(opp_data)

    return success_response(data=results)


@opportunity_bp.route('/<int:opportunity_id>', methods=['GET'])
@login_required
def get_opportunity(opportunity_id):
    """Retrieve full opportunity profile."""
    opp = db.session.get(Opportunity, opportunity_id)
    if not opp:
        return error_response("Opportunity not found.", 404)

    opp_data = opp.to_dict(include_details=True)

    # If student, attach eligibility report
    if session.get('role') == 'student' and session.get('student_id'):
        opp_data['eligibility'] = EligibilityService.evaluate(session.get('student_id'), opp.opportunity_id)

    return success_response(data=opp_data)


@opportunity_bp.route('/<int:opportunity_id>/eligibility', methods=['GET'])
@role_required(['student'])
def check_eligibility(opportunity_id):
    """Return explicit eligibility report for the current student."""
    student_id = session.get('student_id')
    eval_result = EligibilityService.evaluate(student_id, opportunity_id)
    return success_response(data=eval_result)


@opportunity_bp.route('', methods=['POST'])
@role_required(['admin', 'recruiter'])
def create_opportunity():
    """Create a new job or internship opportunity."""
    data = request.get_json() or {}
    user_role = session.get('role')

    company_id = data.get('company_id')
    if user_role == 'recruiter':
        company_id = session.get('company_id')

    if not company_id:
        return error_response("Company ID is required.", 400)

    title = data.get('title', '').strip()
    opp_type = data.get('opportunity_type', 'Full-Time')
    description = data.get('description', '').strip()
    min_cgpa = data.get('min_cgpa', 0.0)
    grad_year = data.get('graduation_year', datetime.now().year)
    location = data.get('location', '').strip()
    salary_range = data.get('salary_range', '').strip()
    opening_date_str = data.get('opening_date')
    deadline_str = data.get('deadline')

    if not title or not description or not location or not salary_range or not opening_date_str or not deadline_str:
        return error_response("All primary opportunity fields (title, description, location, salary, opening_date, deadline) are required.", 400)

    try:
        opening_date = datetime.strptime(opening_date_str, '%Y-%m-%d').date()
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    except ValueError:
        return error_response("Invalid date format. Use YYYY-MM-DD.", 400)

    if deadline < opening_date:
        return error_response("Application deadline cannot be earlier than opening date.", 400)

    opp = Opportunity(
        company_id=company_id,
        title=title,
        opportunity_type=opp_type,
        description=description,
        min_cgpa=min_cgpa,
        graduation_year=grad_year,
        location=location,
        work_mode=data.get('work_mode', 'On-Site'),
        salary_range=salary_range,
        opening_date=opening_date,
        deadline=deadline,
        status=data.get('status', 'Active'),
    )
    db.session.add(opp)
    db.session.flush()

    # Link eligible departments
    department_ids = data.get('department_ids', [])
    for d_id in department_ids:
        od = OpportunityDepartment(opportunity_id=opp.opportunity_id, department_id=d_id)
        db.session.add(od)

    # Link skills
    skills_data = data.get('skills', [])
    for sk in skills_data:
        sk_id = sk.get('skill_id')
        is_mand = sk.get('is_mandatory', True)
        if sk_id:
            os_rec = OpportunitySkill(opportunity_id=opp.opportunity_id, skill_id=sk_id, is_mandatory=is_mand)
            db.session.add(os_rec)

    db.session.commit()
    return success_response(data=opp.to_dict(include_details=True), message="Opportunity created successfully.", status_code=201)


@opportunity_bp.route('/<int:opportunity_id>', methods=['PUT'])
@role_required(['admin', 'recruiter'])
def update_opportunity(opportunity_id):
    """Update opportunity details and requirements."""
    opp = db.session.get(Opportunity, opportunity_id)
    if not opp:
        return error_response("Opportunity not found.", 404)

    # Permission check for recruiter
    if session.get('role') == 'recruiter' and opp.company_id != session.get('company_id'):
        return error_response("You are not authorized to update opportunities for another company.", 403)

    data = request.get_json() or {}

    if 'title' in data and data['title'].strip():
        opp.title = data['title'].strip()
    if 'opportunity_type' in data and data['opportunity_type'] in ['Full-Time', 'Internship', 'Part-Time']:
        opp.opportunity_type = data['opportunity_type']
    if 'description' in data and data['description'].strip():
        opp.description = data['description'].strip()
    if 'min_cgpa' in data:
        try:
            val = float(data['min_cgpa'])
            if 0.0 <= val <= 10.0:
                opp.min_cgpa = val
        except (ValueError, TypeError):
            pass
    if 'graduation_year' in data:
        opp.graduation_year = int(data['graduation_year'])
    if 'location' in data and data['location'].strip():
        opp.location = data['location'].strip()
    if 'work_mode' in data and data['work_mode'] in ['On-Site', 'Remote', 'Hybrid']:
        opp.work_mode = data['work_mode']
    if 'salary_range' in data and data['salary_range'].strip():
        opp.salary_range = data['salary_range'].strip()
    if 'deadline' in data:
        try:
            opp.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
        except ValueError:
            return error_response("Invalid deadline format. Use YYYY-MM-DD.", 400)
    if 'status' in data and data['status'] in ['Active', 'Closed', 'Draft']:
        opp.status = data['status']

    # Update departments if provided
    if 'department_ids' in data and isinstance(data['department_ids'], list):
        OpportunityDepartment.query.filter_by(opportunity_id=opp.opportunity_id).delete()
        for d_id in data['department_ids']:
            db.session.add(OpportunityDepartment(opportunity_id=opp.opportunity_id, department_id=d_id))

    # Update skills if provided
    if 'skills' in data and isinstance(data['skills'], list):
        OpportunitySkill.query.filter_by(opportunity_id=opp.opportunity_id).delete()
        for sk in data['skills']:
            sk_id = sk.get('skill_id')
            is_mand = sk.get('is_mandatory', True)
            if sk_id:
                db.session.add(OpportunitySkill(opportunity_id=opp.opportunity_id, skill_id=sk_id, is_mandatory=is_mand))

    db.session.commit()
    return success_response(data=opp.to_dict(include_details=True), message="Opportunity updated successfully.")


@opportunity_bp.route('/<int:opportunity_id>/status', methods=['PATCH'])
@role_required(['admin', 'recruiter'])
def update_opportunity_status(opportunity_id):
    """Update opportunity status (Active, Closed, Draft)."""
    opp = db.session.get(Opportunity, opportunity_id)
    if not opp:
        return error_response("Opportunity not found.", 404)

    if session.get('role') == 'recruiter' and opp.company_id != session.get('company_id'):
        return error_response("You are not authorized to update opportunities for another company.", 403)

    data = request.get_json() or {}
    new_status = data.get('status', '').strip()
    if new_status not in ['Active', 'Closed', 'Draft']:
        return error_response("Invalid status. Allowed: Active, Closed, Draft.", 400)

    opp.status = new_status
    db.session.commit()
    return success_response(data=opp.to_dict(include_details=True), message=f"Opportunity status changed to '{new_status}'.")


@opportunity_bp.route('/<int:opportunity_id>', methods=['DELETE'])
@role_required(['admin', 'recruiter'])
def delete_opportunity(opportunity_id):
    """Delete an opportunity if no applications exist, or soft-close it."""
    opp = db.session.get(Opportunity, opportunity_id)
    if not opp:
        return error_response("Opportunity not found.", 404)

    if session.get('role') == 'recruiter' and opp.company_id != session.get('company_id'):
        return error_response("You are not authorized to delete opportunities for another company.", 403)

    if opp.applications and len(opp.applications) > 0:
        # Prevent hard deletion when applications exist to preserve student records; close instead
        opp.status = 'Closed'
        db.session.commit()
        return success_response(
            data=opp.to_dict(),
            message="Opportunity has active applications and cannot be deleted. It has been marked as 'Closed' instead."
        )

    db.session.delete(opp)
    db.session.commit()
    return success_response(message="Opportunity deleted successfully.")

