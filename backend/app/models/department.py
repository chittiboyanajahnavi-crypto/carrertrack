from datetime import datetime
from app.extensions import db


class Department(db.Model):
    __tablename__ = 'departments'

    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    students = db.relationship('Student', back_populates='department', lazy='select')
    opportunity_departments = db.relationship(
        'OpportunityDepartment', back_populates='department', cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'department_id': self.department_id,
            'code': self.code,
            'name': self.name,
        }

    def __repr__(self):
        return f"<Department {self.code}: {self.name}>"
