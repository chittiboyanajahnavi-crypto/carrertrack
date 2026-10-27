from functools import wraps
from flask import session
from app.utils.responses import error_response


def login_required(f):
    """Decorator to require that a user is logged into the session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return error_response("Authentication required. Please log in.", 401)
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    """Decorator to require that the authenticated user possesses one of the allowed roles."""
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return error_response("Authentication required. Please log in.", 401)
            
            user_role = session.get('role')
            if user_role not in allowed_roles:
                return error_response(
                    f"Access forbidden: requires one of {allowed_roles} roles. Your role is '{user_role}'.",
                    403
                )
            return f(*args, **kwargs)
        return decorated_function
    return decorator
