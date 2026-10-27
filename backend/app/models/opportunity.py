from datetime import datetime
from sqlalchemy import CheckConstraint
from app.extensions import db


class Opportunity(db.Model):
    __tablename__ = 'opportunities'

    opportunity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(
        db.Integer, db.ForeignKey('companies.company_id', ondelete='RESTRICT'), nullable=False, index=True
    )
    title = db.Column(db.String(150), nullable=False)
    opportunity_type = db.Column(
        db.Enum('Full-Time', 'Internship', 'Part-Time', name='opp_type_enum'),
        nullable=False,
        index=True,
    )
    description = db.Column(db.Text, nullable=False)
    min_cgpa = db.Column(db.Numeric(4, 2), nullable=False, default=0.00)
    graduation_year = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    work_mode = db.Column(
        db.Enum('On-Site', 'Remote', 'Hybrid', name='work_mode_enum'),
        nullable=False,
        default='On-Site',
    )
    salary_range = db.Column(db.String(80), nullable=False)
    opening_date = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.Enum('Active', 'Closed', 'Draft', name='opp_status_enum'),
        nullable=False,
        default='Active',
        index=True,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('min_cgpa >= 0.00 AND min_cgpa <= 10.00', name='chk_opportunity_cgpa'),
        CheckConstraint('deadline >= opening_date', name='chk_opportunity_dates'),
    )

    # Relationships
    company = db.relationship('Company', back_populates='opportunities')
    opportunity_skills = db.relationship(
        'OpportunitySkill', back_populates='opportunity', cascade='all, delete-orphan'
    )
    opportunity_departments = db.relationship(
        'OpportunityDepartment', back_populates='opportunity', cascade='all, delete-orphan'
    )
    applications = db.relationship(
        'Application', back_populates='opportunity', cascade='all, delete-orphan'
    )

    def to_dict(self, include_details=True):
        data = {
            'opportunity_id': self.opportunity_id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'title': self.title,
            'opportunity_type': self.opportunity_type,
            'description': self.description,
            'min_cgpa': float(self.min_cgpa) if self.min_cgpa is not None else 0.0,
            'graduation_year': self.graduation_year,
            'location': self.location,
            'work_mode': self.work_mode,
            'salary_range': self.salary_range,
            'opening_date': self.opening_date.isoformat() if self.opening_date else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_details:
            data['eligible_departments'] = [
                {
                    'department_id': od.department.department_id,
                    'code': od.department.code,
                    'name': od.department.name,
                }
                for od in self.opportunity_departments
                if od.department
            ]
            data['required_skills'] = [
                {
                    'skill_id': os.skill.skill_id,
                    'name': os.skill.name,
                    'category': os.skill.category,
                    'is_mandatory': os.is_mandatory,
                }
                for os in self.opportunity_skills
                if os.skill
            ]
            data['applications_count'] = len(self.applications) if self.applications else 0
        return data

    def __repr__(self):
        return f"<Opportunity {self.opportunity_id}: {self.title} at {self.company.name if self.company else self.company_id}>"


class OpportunityDepartment(db.Model):
    __tablename__ = 'opportunity_departments'

    opportunity_id = db.Column(
        db.Integer, db.ForeignKey('opportunities.opportunity_id', ondelete='CASCADE'), primary_key=True
    )
    department_id = db.Column(
        db.Integer, db.ForeignKey('departments.department_id', ondelete='CASCADE'), primary_key=True
    )

    # Relationships
    opportunity = db.relationship('Opportunity', back_populates='opportunity_departments')
    department = db.relationship('Department', back_populates='opportunity_departments')

    def to_dict(self):
        return {
            'opportunity_id': self.opportunity_id,
            'department_id': self.department_id,
            'department_code': self.department.code if self.department else None,
            'department_name': self.department.name if self.department else None,
        }
