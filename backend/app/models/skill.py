from datetime import datetime
from app.extensions import db


class Skill(db.Model):
    __tablename__ = 'skills'

    skill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    category = db.Column(db.String(60), nullable=False, default='Technical')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_skills = db.relationship('StudentSkill', back_populates='skill', cascade='all, delete-orphan')
    opportunity_skills = db.relationship('OpportunitySkill', back_populates='skill', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'category': self.category,
        }

    def __repr__(self):
        return f"<Skill {self.name} ({self.category})>"


class StudentSkill(db.Model):
    __tablename__ = 'student_skills'

    student_id = db.Column(
        db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), primary_key=True
    )
    skill_id = db.Column(
        db.Integer, db.ForeignKey('skills.skill_id', ondelete='CASCADE'), primary_key=True
    )
    proficiency = db.Column(
        db.Enum('Beginner', 'Intermediate', 'Advanced', name='proficiency_enum'),
        nullable=False,
        default='Intermediate',
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', back_populates='student_skills')
    skill = db.relationship('Skill', back_populates='student_skills')

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'category': self.skill.category if self.skill else None,
            'proficiency': self.proficiency,
        }


class OpportunitySkill(db.Model):
    __tablename__ = 'opportunity_skills'

    opportunity_id = db.Column(
        db.Integer, db.ForeignKey('opportunities.opportunity_id', ondelete='CASCADE'), primary_key=True
    )
    skill_id = db.Column(
        db.Integer, db.ForeignKey('skills.skill_id', ondelete='CASCADE'), primary_key=True
    )
    is_mandatory = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    opportunity = db.relationship('Opportunity', back_populates='opportunity_skills')
    skill = db.relationship('Skill', back_populates='opportunity_skills')

    def to_dict(self):
        return {
            'opportunity_id': self.opportunity_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'is_mandatory': self.is_mandatory,
        }
