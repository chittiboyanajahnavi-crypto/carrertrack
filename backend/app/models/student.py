from datetime import datetime
from sqlalchemy import CheckConstraint
from app.extensions import db


class Student(db.Model):
    __tablename__ = 'students'

    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False
    )
    roll_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department_id = db.Column(
        db.Integer, db.ForeignKey('departments.department_id', ondelete='RESTRICT'), nullable=False, index=True
    )
    graduation_year = db.Column(db.Integer, nullable=False, index=True)
    cgpa = db.Column(db.Numeric(4, 2), nullable=False, index=True)
    resume_url = db.Column(db.String(255), nullable=True)
    profile_complete = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('cgpa >= 0.00 AND cgpa <= 10.00', name='chk_student_cgpa'),
        CheckConstraint('graduation_year >= 2000 AND graduation_year <= 2100', name='chk_student_grad_year'),
    )

    # Relationships
    user = db.relationship('User', back_populates='student')
    department = db.relationship('Department', back_populates='students')
    student_skills = db.relationship(
        'StudentSkill', back_populates='student', cascade='all, delete-orphan'
    )
    applications = db.relationship(
        'Application', back_populates='student', cascade='all, delete-orphan'
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def to_dict(self, include_skills=True):
        data = {
            'student_id': self.student_id,
            'user_id': self.user_id,
            'email': self.user.email if self.user else None,
            'roll_number': self.roll_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'department_id': self.department_id,
            'department_code': self.department.code if self.department else None,
            'department_name': self.department.name if self.department else None,
            'graduation_year': self.graduation_year,
            'cgpa': float(self.cgpa) if self.cgpa is not None else None,
            'resume_url': self.resume_url,
            'profile_complete': self.profile_complete,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_skills and self.student_skills:
            data['skills'] = [
                {
                    'skill_id': ss.skill.skill_id,
                    'name': ss.skill.name,
                    'category': ss.skill.category,
                    'proficiency': ss.proficiency,
                }
                for ss in self.student_skills
                if ss.skill
            ]
        else:
            data['skills'] = []
        return data

    def __repr__(self):
        return f"<Student {self.roll_number}: {self.full_name}>"
