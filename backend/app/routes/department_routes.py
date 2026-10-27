from flask import Blueprint
from app.models import Department
from app.utils.responses import success_response

department_bp = Blueprint('departments', __name__, url_prefix='/api/departments')


@department_bp.route('', methods=['GET'])
def list_departments():
    """List all academic departments."""
    depts = Department.query.order_by(Department.code.asc()).all()
    return success_response(data=[d.to_dict() for d in depts])
