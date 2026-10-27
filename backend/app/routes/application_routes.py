from flask import Blueprint, request, session
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Application, ApplicationStatusHistory, Opportunity, Student
from app.services.eligibility_service import EligibilityService
from app.utils.responses import success_response, error_response
from app.utils.decorators import role_required, login_required

application_bp = Blueprint('applications', __name__, url_prefix='/api/applications')

VALID_STATUSES = [
    'Applied', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected', 'Withdrawn'
]


@application_bp.route('', methods=['POST'])
@role_required(['student'])
def apply_opportunity():
    """Submit an application to an eligible opportunity."""
    student_id = session.get('student_id')
    data = request.get_json() or {}
    opportunity_id = data.get('opportunity_id')

    if not opportunity_id:
        return error_response("Opportunity ID is required.", 400)

    # 1. Server-side Eligibility Verification
    eval_result = EligibilityService.evaluate(student_id, opportunity_id)
    if not eval_result['can_apply']:
        return error_response(
            "Application rejected: you are not eligible or have already applied.",
            400,
            errors=eval_result['reasons']
        )

    # 2. Persist Application
    student_notes = data.get('student_notes', '').strip() or None
    app_record = Application(
        student_id=student_id,
        opportunity_id=opportunity_id,
        status='Applied',
        student_notes=student_notes,
    )
    db.session.add(app_record)

    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        return error_response("You have already submitted an application for this opportunity.", 409)

    # 3. Create Audit Trail Entry
    history = ApplicationStatusHistory(
        application_id=app_record.application_id,
        old_status=None,
        new_status='Applied',
        changed_by_user_id=session.get('user_id'),
        notes='Application submitted by student.',
    )
    db.session.add(history)
    db.session.commit()

    return success_response(
        data=app_record.to_dict(include_history=True),
        message="Application submitted successfully.",
        status_code=201
    )


@application_bp.route('/my', methods=['GET'])
@role_required(['student'])
def get_my_applications():
    """Retrieve all applications submitted by the logged-in student."""
    student_id = session.get('student_id')
    apps = Application.query.filter_by(student_id=student_id).order_by(Application.applied_at.desc()).all()
    return success_response(data=[a.to_dict(include_history=True, include_interviews=True) for a in apps])


@application_bp.route('', methods=['GET'])
@role_required(['admin', 'recruiter'])
def list_applications():
    """List applications for administrator or recruiter review."""
    query = Application.query
    user_role = session.get('role')

    # If recruiter, restrict to recruiter's company
    if user_role == 'recruiter':
        company_id = session.get('company_id')
        query = query.join(Opportunity).filter(Opportunity.company_id == company_id)

    # Filters
    opp_id = request.args.get('opportunity_id', type=int)
    if opp_id:
        query = query.filter(Application.opportunity_id == opp_id)

    student_id_filter = request.args.get('student_id', type=int)
    if student_id_filter and user_role == 'admin':
        query = query.filter(Application.student_id == student_id_filter)

    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Application.status == status)

    search = request.args.get('search', '').strip()
    if search:
        query = query.join(Student).filter(
            (Student.first_name.ilike(f"%{search}%")) |
            (Student.last_name.ilike(f"%{search}%")) |
            (Student.roll_number.ilike(f"%{search}%"))
        )

    apps = query.order_by(Application.applied_at.desc()).all()
    return success_response(data=[a.to_dict(include_history=True, include_interviews=True) for a in apps])


@application_bp.route('/<int:application_id>', methods=['GET'])
@login_required
def get_application(application_id):
    """Retrieve full details of a specific application with status history and interviews."""
    app_record = db.session.get(Application, application_id)
    if not app_record:
        return error_response("Application not found.", 404)

    user_role = session.get('role')
    user_student_id = session.get('student_id')
    user_company_id = session.get('company_id')

    # RBAC Enforcement:
    # 1. Admin can view any application
    # 2. Student can view ONLY their own application
    # 3. Recruiter can view ONLY applications for their company's opportunities
    if user_role == 'student' and user_student_id != app_record.student_id:
        return error_response("You are not authorized to view this application.", 403)
    elif user_role == 'recruiter' and user_company_id != app_record.opportunity.company_id:
        return error_response("You are not authorized to view applications for another company.", 403)

    return success_response(data=app_record.to_dict(include_history=True, include_interviews=True))


@application_bp.route('/<int:application_id>/withdraw', methods=['POST'])
@role_required(['student'])
def withdraw_application(application_id):
    """Student withdraws their active application."""
    student_id = session.get('student_id')
    app_record = db.session.get(Application, application_id)
    if not app_record:
        return error_response("Application not found.", 404)

    if app_record.student_id != student_id:
        return error_response("You can only withdraw your own applications.", 403)

    if app_record.status in ['Selected', 'Rejected']:
        return error_response(f"Cannot withdraw application that has already been {app_record.status.lower()}.", 400)

    if app_record.status == 'Withdrawn':
        return error_response("This application is already withdrawn.", 400)

    old_status = app_record.status
    app_record.status = 'Withdrawn'

    history = ApplicationStatusHistory(
        application_id=app_record.application_id,
        old_status=old_status,
        new_status='Withdrawn',
        changed_by_user_id=session.get('user_id'),
        notes='Application withdrawn by student.',
    )
    db.session.add(history)
    db.session.commit()

    return success_response(
        data=app_record.to_dict(include_history=True),
        message="Application withdrawn successfully."
    )


@application_bp.route('/<int:application_id>/status', methods=['PATCH'])
@role_required(['admin', 'recruiter'])
def update_status(application_id):
    """Update application lifecycle status with audit logging."""
    app_record = db.session.get(Application, application_id)
    if not app_record:
        return error_response("Application not found.", 404)

    # Permission check for recruiter
    if session.get('role') == 'recruiter':
        if app_record.opportunity.company_id != session.get('company_id'):
            return error_response("You are not authorized to manage applicants for this company.", 403)

    data = request.get_json() or {}
    new_status = data.get('status', '').strip()
    notes = data.get('notes', '').strip() or None

    if new_status not in VALID_STATUSES:
        return error_response(f"Invalid status '{new_status}'. Allowed statuses: {VALID_STATUSES}", 400)

    old_status = app_record.status
    if old_status == new_status:
        return success_response(data=app_record.to_dict(), message="Status unchanged.")

    # Apply update & audit record
    app_record.status = new_status
    history = ApplicationStatusHistory(
        application_id=app_record.application_id,
        old_status=old_status,
        new_status=new_status,
        changed_by_user_id=session.get('user_id'),
        notes=notes,
    )
    db.session.add(history)
    db.session.commit()

    return success_response(
        data=app_record.to_dict(include_history=True),
        message=f"Application status updated from '{old_status}' to '{new_status}'."
    )

