from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Skill
from app.utils.responses import success_response, error_response
from app.utils.decorators import role_required, login_required

skill_bp = Blueprint('skills', __name__, url_prefix='/api/skills')


@skill_bp.route('', methods=['GET'])
def list_skills():
    """List master skills taxonomy with optional category and search filters."""
    query = Skill.query

    category = request.args.get('category', '').strip()
    if category:
        query = query.filter(Skill.category.ilike(category))

    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(Skill.name.ilike(f"%{search}%"))

    skills = query.order_by(Skill.category.asc(), Skill.name.asc()).all()
    return success_response(data=[s.to_dict() for s in skills])


@skill_bp.route('/<int:skill_id>', methods=['GET'])
def get_skill(skill_id):
    """Retrieve details of a single skill."""
    skill = db.session.get(Skill, skill_id)
    if not skill:
        return error_response("Skill not found.", 404)
    return success_response(data=skill.to_dict())


@skill_bp.route('', methods=['POST'])
@role_required(['admin'])
def create_skill():
    """Admin-only endpoint to add a new skill to the master taxonomy."""
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    category = (data.get('category') or 'Technical').strip()

    if not name:
        return error_response("Skill name is required.", 400)

    existing = Skill.query.filter_by(name=name).first()
    if existing:
        return error_response(f"Skill '{name}' already exists in taxonomy.", 409)

    skill = Skill(name=name, category=category)
    db.session.add(skill)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error_response("Skill name already exists.", 409)

    return success_response(data=skill.to_dict(), message="Skill created successfully.", status_code=201)
