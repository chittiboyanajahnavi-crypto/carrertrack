from datetime import datetime
from flask import Blueprint, request, session
from app.extensions import db
from app.models import Interview, Application, ApplicationStatusHistory
from app.utils.responses import success_response, error_response
from app.utils.decorators import role_required, login_required

interview_bp = Blueprint('interviews', __name__, url_prefix='/api/interviews')


@interview_bp.route('', methods=['GET'])
@login_required
def list_interviews():
    """Retrieve interviews based on user role."""
    user_role = session.get('role')
    query = Interview.query.join(Application)

    if user_role == 'student':
        query = query.filter(Application.student_id == session.get('student_id'))
    elif user_role == 'recruiter':
        query = query.join(Application.opportunity).filter(
            Application.opportunity.has(company_id=session.get('company_id'))
        )

    # Filter by application
    app_id = request.args.get('application_id', type=int)
    if app_id:
        query = query.filter(Interview.application_id == app_id)

    interviews = query.order_by(Interview.scheduled_at.asc()).all()
    results = []
    for i in interviews:
        item = i.to_dict()
        if i.application:
            item['student_name'] = i.application.student.full_name if i.application.student else None
            item['student_roll'] = i.application.student.roll_number if i.application.student else None
            item['opportunity_title'] = i.application.opportunity.title if i.application.opportunity else None
            item['company_name'] = i.application.opportunity.company.name if i.application.opportunity and i.application.opportunity.company else None
        results.append(item)

    return success_response(data=results)


@interview_bp.route('', methods=['POST'])
@role_required(['admin', 'recruiter'])
def schedule_interview():
    """Schedule a new interview round."""
    data = request.get_json() or {}
    application_id = data.get('application_id')
    round_name = data.get('round_name', '').strip()
    scheduled_at_str = data.get('scheduled_at', '').strip()
    mode = data.get('mode', 'Video Call')

    if not application_id or not round_name or not scheduled_at_str or not mode:
        return error_response("Application ID, round name, scheduled time, and mode are required.", 400)

    app_record = db.session.get(Application, application_id)
    if not app_record:
        return error_response("Application not found.", 404)

    # Recruiter permission verification
    if session.get('role') == 'recruiter' and app_record.opportunity.company_id != session.get('company_id'):
        return error_response("You are not authorized to schedule interviews for this applicant.", 403)

    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_str.replace('Z', '+00:00'))
    except ValueError:
        return error_response("Invalid ISO datetime format for scheduled_at.", 400)

    # Determine round number
    existing_rounds = len(app_record.interviews)
    round_number = data.get('round_number') or (existing_rounds + 1)

    interview = Interview(
        application_id=application_id,
        round_number=round_number,
        round_name=round_name,
        scheduled_at=scheduled_at,
        mode=mode,
        meeting_location_or_link=data.get('meeting_location_or_link', '').strip() or None,
        interviewer_name=data.get('interviewer_name', '').strip() or None,
        outcome='Pending',
        feedback=data.get('feedback', '').strip() or None,
    )
    db.session.add(interview)

    # Update application status to Interview Scheduled if currently Applied or Shortlisted
    if app_record.status in ['Applied', 'Under Review', 'Shortlisted']:
        old_status = app_record.status
        app_record.status = 'Interview Scheduled'
        history = ApplicationStatusHistory(
            application_id=app_record.application_id,
            old_status=old_status,
            new_status='Interview Scheduled',
            changed_by_user_id=session.get('user_id'),
            notes=f"Scheduled {round_name} (Round {round_number}).",
        )
        db.session.add(history)

    db.session.commit()
    return success_response(data=interview.to_dict(), message="Interview scheduled successfully.", status_code=201)


@interview_bp.route('/<int:interview_id>', methods=['PATCH'])
@role_required(['admin', 'recruiter'])
def update_interview(interview_id):
    """Update interview outcome and feedback."""
    interview = db.session.get(Interview, interview_id)
    if not interview:
        return error_response("Interview record not found.", 404)

    data = request.get_json() or {}
    if 'outcome' in data:
        outcome = data['outcome'].strip()
        if outcome not in ['Pending', 'Passed', 'Failed', 'Rescheduled', 'Cancelled']:
            return error_response(f"Invalid outcome '{outcome}'.", 400)
        interview.outcome = outcome

    if 'feedback' in data:
        interview.feedback = data['feedback'].strip() or None

    if 'scheduled_at' in data:
        try:
            interview.scheduled_at = datetime.fromisoformat(data['scheduled_at'].replace('Z', '+00:00'))
        except ValueError:
            return error_response("Invalid datetime format.", 400)

    db.session.commit()
    return success_response(data=interview.to_dict(), message="Interview updated successfully.")
