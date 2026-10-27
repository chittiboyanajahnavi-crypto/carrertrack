from flask import session
from app.models import User, Student, Recruiter


class AuthService:
    @staticmethod
    def authenticate(email: str, password: str):
        """Verify user credentials and set session if valid."""
        # A failed login must not leave a previous user's session active.
        session.clear()
        if not email or not password:
            return None, "Email and password are required."

        user = User.query.filter_by(email=email.strip().lower()).first()
        if not user:
            return None, "Invalid email or password."

        if not user.is_active:
            return None, "Account is deactivated. Please contact the administrator."

        if not user.check_password(password):
            return None, "Invalid email or password."

        # Set session
        session.clear()
        session['user_id'] = user.user_id
        session['email'] = user.email
        session['role'] = user.role
        session.permanent = True

        profile = {
            'user_id': user.user_id,
            'email': user.email,
            'role': user.role,
        }

        if user.role == 'student' and user.student:
            session['student_id'] = user.student.student_id
            profile['student'] = user.student.to_dict()
        elif user.role == 'recruiter' and user.recruiter:
            session['recruiter_id'] = user.recruiter.recruiter_id
            session['company_id'] = user.recruiter.company_id
            profile['recruiter'] = user.recruiter.to_dict()

        return profile, None

    @staticmethod
    def logout():
        """Clear current session."""
        session.clear()
        return True

    @staticmethod
    def get_current_user_profile():
        """Get profile data of the currently logged-in user."""
        user_id = session.get('user_id')
        if not user_id:
            return None

        from app.extensions import db
        user = db.session.get(User, user_id)
        if not user or not user.is_active:
            session.clear()
            return None

        profile = {
            'user_id': user.user_id,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
        }

        if user.role == 'student' and user.student:
            profile['student'] = user.student.to_dict()
        elif user.role == 'recruiter' and user.recruiter:
            profile['recruiter'] = user.recruiter.to_dict()

        return profile

    @staticmethod
    def register_student(data: dict):
        """Validate input and register a new student user."""
        import re
        from app.extensions import db
        from app.models import Department

        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        roll_number = (data.get('roll_number') or '').strip().upper()
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()
        phone = (data.get('phone') or '').strip()
        dept_id = data.get('department_id')
        grad_year = data.get('graduation_year')
        cgpa = data.get('cgpa')

        # 1. Validation
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return None, "A valid email address is required.", 400

        if not password or len(password) < 8:
            return None, "Password must be at least 8 characters long.", 400

        if not roll_number:
            return None, "Roll number is required.", 400

        if not first_name or not last_name:
            return None, "First name and last name are required.", 400

        if not phone:
            return None, "Phone number is required.", 400

        if not dept_id:
            return None, "Department ID is required.", 400

        dept = db.session.get(Department, dept_id)
        if not dept:
            return None, f"Department with ID {dept_id} does not exist.", 400

        try:
            grad_year = int(grad_year)
            if grad_year < 2000 or grad_year > 2100:
                return None, "Graduation year must be between 2000 and 2100.", 400
        except (ValueError, TypeError):
            return None, "Valid graduation year is required.", 400

        try:
            cgpa = float(cgpa)
            if cgpa < 0.0 or cgpa > 10.0:
                return None, "CGPA must be between 0.00 and 10.00.", 400
        except (ValueError, TypeError):
            return None, "Valid CGPA is required.", 400

        # Check existing user email
        if User.query.filter_by(email=email).first():
            return None, "An account with this email already exists.", 409

        # Check existing roll number
        if Student.query.filter_by(roll_number=roll_number).first():
            return None, "A student with this roll number already exists.", 409

        # 2. Persist User and Student profile atomically
        try:
            new_user = User(email=email, role='student', is_active=True)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()

            new_student = Student(
                user_id=new_user.user_id,
                roll_number=roll_number,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                department_id=dept_id,
                graduation_year=grad_year,
                cgpa=cgpa,
                profile_complete=False,
                is_active=True,
            )
            db.session.add(new_student)
            db.session.commit()

            return new_student.to_dict(), None, 201
        except Exception as e:
            db.session.rollback()
            return None, f"Failed to register student: {str(e)}", 500

    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str):
        """Update password for an authenticated user."""
        from app.extensions import db

        if not current_password or not new_password:
            return False, "Current and new passwords are required.", 400

        if len(new_password) < 8:
            return False, "New password must be at least 8 characters long.", 400

        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found.", 404

        if not user.check_password(current_password):
            return False, "Current password is incorrect.", 401

        user.set_password(new_password)
        db.session.commit()
        return True, "Password updated successfully.", 200

