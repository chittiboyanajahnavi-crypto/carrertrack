from datetime import datetime
from app.extensions import db


class Company(db.Model):
    __tablename__ = 'companies'

    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    industry = db.Column(db.String(100), nullable=False, index=True)
    website = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(150), nullable=False)
    contact_phone = db.Column(db.String(25), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recruiters = db.relationship('Recruiter', back_populates='company', cascade='all, delete-orphan')
    opportunities = db.relationship('Opportunity', back_populates='company', lazy='dynamic')

    def to_dict(self):
        return {
            'company_id': self.company_id,
            'name': self.name,
            'industry': self.industry,
            'website': self.website,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'description': self.description,
            'is_active': self.is_active,
            'opportunities_count': self.opportunities.count() if hasattr(self.opportunities, 'count') else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Company {self.company_id}: {self.name}>"


class Recruiter(db.Model):
    __tablename__ = 'recruiters'

    recruiter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False
    )
    company_id = db.Column(
        db.Integer, db.ForeignKey('companies.company_id', ondelete='RESTRICT'), nullable=False, index=True
    )
    full_name = db.Column(db.String(120), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='recruiter')
    company = db.relationship('Company', back_populates='recruiters')

    def to_dict(self):
        return {
            'recruiter_id': self.recruiter_id,
            'user_id': self.user_id,
            'email': self.user.email if self.user else None,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'full_name': self.full_name,
            'designation': self.designation,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Recruiter {self.full_name} ({self.company.name if self.company else self.company_id})>"
