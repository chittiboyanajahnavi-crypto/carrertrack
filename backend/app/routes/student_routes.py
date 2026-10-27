from flask import Blueprint, request, session
from app.extensions import db
from app.models import Student, User, Department, Skill, StudentSkill
from app.services.metrics_service import MetricsService
from app.utils.responses import success_response, error_response
from app.utils.decorators import role_required, login_required

student_bp = Blueprint('students', __name__, url_prefix='/api/students')


@student_bp.route('', methods=['GET'])
@role_required(['admin', 'recruiter'])
def list_students():
    """List students with search, department, graduation year, and CGPA filters."""
    query = Student.query

    # Search by name, roll number, or email
    search = request.args.get('search', '').strip()
    if search:
        search_pattern = f"%{search}%"
        query = query.join(User, Student.user_id == User.user_id).filter(
            (Student.first_name.ilike(search_pattern)) |
            (Student.last_name.ilike(search_pattern)) |
            (Student.roll_number.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )

    # Department filter
    dept_id = request.args.get('department_id', type=int)
    if dept_id:
        query = query.filter(Student.department_id == dept_id)

    # Graduation year filter
    grad_year = request.args.get('graduation_year', type=int)
    if grad_year:
        query = query.filter(Student.graduation_year == grad_year)

    # Minimum CGPA filter
    min_cgpa = request.args.get('min_cgpa', type=float)
    if min_cgpa is not None:
        query = query.filter(Student.cgpa >= min_cgpa)

    # Active status filter
    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter(Student.is_active == (is_active.lower() == 'true'))

    students = query.order_by(Student.roll_number.asc()).all()
    return success_response(data=[s.to_dict() for s in students])


@student_bp.route('/<int:student_id>', methods=['GET'])
@login_required
def get_student(student_id):
    """Retrieve full details of a specific student."""
    # Students can only view their own full profile; Admins & Recruiters can view any
    user_role = session.get('role')
    user_student_id = session.get('student_id')
    if user_role == 'student' and user_student_id != student_id:
        return error_response("You are not authorized to view another student's profile.", 403)

    student = db.session.get(Student, student_id)
    if not student:
        return error_response("Student not found.", 404)

    return success_response(data=student.to_dict(include_skills=True))


@student_bp.route('/dashboard', methods=['GET'])
@role_required(['student'])
def student_dashboard():
    """Retrieve student portal metrics, eligible jobs, and upcoming interviews."""
    student_id = session.get('student_id')
    if not student_id:
        return error_response("Student profile not found in current session.", 404)

    data = MetricsService.get_student_dashboard(student_id)
    if not data:
        return error_response("Could not load dashboard data.", 404)

    return success_response(data=data)


@student_bp.route('/profile', methods=['GET'])
@student_bp.route('/me', methods=['GET'])
@role_required(['student'])
def get_own_profile():
    """Retrieve full profile of the logged-in student."""
    student_id = session.get('student_id')
    student = db.session.get(Student, student_id)
    if not student:
        return error_response("Student profile not found.", 404)
    return success_response(data=student.to_dict(include_skills=True))


@student_bp.route('/profile', methods=['PUT'])
@role_required(['student'])
def update_profile():
    """Students can update permitted fields: phone, resume_url, and technical skills."""
    student_id = session.get('student_id')
    student = db.session.get(Student, student_id)
    if not student:
        return error_response("Student not found.", 404)

    data = request.get_json() or {}

    # Permitted contact updates
    if 'phone' in data:
        phone_val = str(data['phone']).strip()
        if phone_val:
            student.phone = phone_val

    if 'resume_url' in data:
        student.resume_url = str(data['resume_url']).strip() if data['resume_url'] else None

    # Update skills if provided
    if 'skills' in data and isinstance(data['skills'], list):
        # Remove existing and replace with new skill ratings
        StudentSkill.query.filter_by(student_id=student.student_id).delete()
        for item in data['skills']:
            skill_id = item.get('skill_id')
            proficiency = item.get('proficiency', 'Intermediate')
            if skill_id and proficiency in ['Beginner', 'Intermediate', 'Advanced']:
                ss = StudentSkill(
                    student_id=student.student_id,
                    skill_id=skill_id,
                    proficiency=proficiency,
                )
                db.session.add(ss)

    student.profile_complete = bool(student.phone and (student.resume_url or student.student_skills))
    db.session.commit()

    return success_response(
        data=student.to_dict(include_skills=True),
        message="Profile updated successfully."
    )


@student_bp.route('/skills', methods=['GET'])
@role_required(['student'])
def get_my_skills():
    """Retrieve all skills tagged by the logged-in student."""
    student_id = session.get('student_id')
    student = db.session.get(Student, student_id)
    if not student:
        return error_response("Student profile not found.", 404)

    skills_data = [ss.to_dict() for ss in student.student_skills]
    return success_response(data=skills_data)


@student_bp.route('/skills', methods=['POST'])
@role_required(['student'])
def add_or_update_skill():
    """Add or update proficiency for a single skill."""
    student_id = session.get('student_id')
    student = db.session.get(Student, student_id)
    if not student:
        return error_response("Student profile not found.", 404)

    data = request.get_json() or {}
    skill_id = data.get('skill_id')
    proficiency = data.get('proficiency', 'Intermediate')

    if not skill_id:
        return error_response("Skill ID is required.", 400)

    if proficiency not in ['Beginner', 'Intermediate', 'Advanced']:
        return error_response("Invalid proficiency. Allowed: Beginner, Intermediate, Advanced.", 400)

    skill = db.session.get(Skill, skill_id)
    if not skill:
        return error_response(f"Skill with ID {skill_id} does not exist.", 404)

    student_skill = StudentSkill.query.filter_by(student_id=student_id, skill_id=skill_id).first()
    if student_skill:
        student_skill.proficiency = proficiency
    else:
        student_skill = StudentSkill(
            student_id=student_id,
            skill_id=skill_id,
            proficiency=proficiency
        )
        db.session.add(student_skill)

    student.profile_complete = bool(student.phone and (student.resume_url or student.student_skills))
    db.session.commit()

    return success_response(
        data=student_skill.to_dict(),
        message=f"Skill '{skill.name}' set to '{proficiency}' successfully."
    )


@student_bp.route('/skills/<int:skill_id>', methods=['DELETE'])
@role_required(['student'])
def delete_student_skill(skill_id):
    """Remove a specific skill from the student profile."""
    student_id = session.get('student_id')
    student_skill = StudentSkill.query.filter_by(student_id=student_id, skill_id=skill_id).first()
    if not student_skill:
        return error_response("Skill not found on student profile.", 404)

    db.session.delete(student_skill)
    student = db.session.get(Student, student_id)
    student.profile_complete = bool(student.phone and (student.resume_url or student.student_skills))
    db.session.commit()

    return success_response(message="Skill removed successfully.")

