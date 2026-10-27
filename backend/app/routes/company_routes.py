from flask import Blueprint, request, session
from app.extensions import db
from app.models import Company, Recruiter
from app.utils.responses import success_response, error_response
from app.utils.decorators import role_required, login_required

company_bp = Blueprint('companies', __name__, url_prefix='/api/companies')


@company_bp.route('', methods=['GET'])
@login_required
def list_companies():
    """List companies with search and industry filtering."""
    query = Company.query

    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(Company.name.ilike(f"%{search}%"))

    industry = request.args.get('industry', '').strip()
    if industry:
        query = query.filter(Company.industry == industry)

    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter(Company.is_active == (is_active.lower() == 'true'))

    companies = query.order_by(Company.name.asc()).all()
    return success_response(data=[c.to_dict() for c in companies])


@company_bp.route('/<int:company_id>', methods=['GET'])
@login_required
def get_company(company_id):
    """Retrieve full company details including opportunities."""
    company = db.session.get(Company, company_id)
    if not company:
        return error_response("Company not found.", 404)

    data = company.to_dict()
    data['opportunities'] = [opp.to_dict() for opp in company.opportunities]
    data['recruiters'] = [r.to_dict() for r in company.recruiters]
    return success_response(data=data)


@company_bp.route('', methods=['POST'])
@role_required(['admin'])
def create_company():
    """Create a new company profile (Admin only)."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    industry = data.get('industry', '').strip()
    contact_email = data.get('contact_email', '').strip()

    if not name or not industry or not contact_email:
        return error_response("Company name, industry, and contact email are required.", 400)

    if Company.query.filter_by(name=name).first():
        return error_response(f"Company '{name}' already exists.", 409)

    company = Company(
        name=name,
        industry=industry,
        website=data.get('website', '').strip() or None,
        contact_email=contact_email,
        contact_phone=data.get('contact_phone', '').strip() or None,
        description=data.get('description', '').strip() or None,
    )
    db.session.add(company)
    db.session.commit()

    return success_response(data=company.to_dict(), message="Company created successfully.", status_code=201)


@company_bp.route('/<int:company_id>', methods=['PUT'])
@role_required(['admin', 'recruiter'])
def update_company(company_id):
    """Update company details (Admin or assigned Recruiter)."""
    company = db.session.get(Company, company_id)
    if not company:
        return error_response("Company not found.", 404)

    # If recruiter, verify assigned company
    if session.get('role') == 'recruiter' and session.get('company_id') != company_id:
        return error_response("You are only permitted to manage your assigned company.", 403)

    data = request.get_json() or {}
    if 'industry' in data:
        company.industry = data['industry'].strip()
    if 'website' in data:
        company.website = data['website'].strip() or None
    if 'contact_email' in data:
        company.contact_email = data['contact_email'].strip()
    if 'contact_phone' in data:
        company.contact_phone = data['contact_phone'].strip() or None
    if 'description' in data:
        company.description = data['description'].strip() or None

    db.session.commit()
    return success_response(data=company.to_dict(), message="Company updated successfully.")
