from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.responses import success_response, error_response
from app.utils.decorators import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user with email and password, establishing an HTTP-only cookie session."""
    data = request.get_json() or {}
    email = data.get('email', '')
    password = data.get('password', '')

    profile, error = AuthService.authenticate(email, password)
    if error:
        return error_response(error, 401)

    return success_response(data=profile, message="Login successful.")


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear session cookie and log user out."""
    AuthService.logout()
    return success_response(message="Logged out successfully.")


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get the active authenticated user profile."""
    profile = AuthService.get_current_user_profile()
    if not profile:
        return error_response("User session expired or invalid.", 401)
    return success_response(data=profile)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new student account."""
    data = request.get_json() or {}
    student_dict, error, status_code = AuthService.register_student(data)
    if error:
        return error_response(error, status_code)

    return success_response(
        data=student_dict,
        message="Student registration successful. You can now log in.",
        status_code=201
    )


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change password for the current authenticated user."""
    from flask import session
    data = request.get_json() or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    user_id = session.get('user_id')

    success, msg, status_code = AuthService.change_password(user_id, current_password, new_password)
    if not success:
        return error_response(msg, status_code)

    return success_response(message=msg)

