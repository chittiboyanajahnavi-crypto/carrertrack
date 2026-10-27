from datetime import datetime
from sqlalchemy import UniqueConstraint
from app.extensions import db


class Application(db.Model):
    __tablename__ = 'applications'

    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey('students.student_id', ondelete='RESTRICT'), nullable=False, index=True
    )
    opportunity_id = db.Column(
        db.Integer, db.ForeignKey('opportunities.opportunity_id', ondelete='RESTRICT'), nullable=False, index=True
    )
    status = db.Column(
        db.Enum(
            'Applied',
            'Under Review',
            'Shortlisted',
            'Interview Scheduled',
            'Selected',
            'Rejected',
            'Withdrawn',
            name='app_status_enum',
        ),
        nullable=False,
        default='Applied',
        index=True,
    )
    student_notes = db.Column(db.Text, nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('student_id', 'opportunity_id', name='uq_student_opportunity'),
    )

    # Relationships
    student = db.relationship('Student', back_populates='applications')
    opportunity = db.relationship('Opportunity', back_populates='applications')
    status_history = db.relationship(
        'ApplicationStatusHistory',
        back_populates='application',
        cascade='all, delete-orphan',
        order_by='ApplicationStatusHistory.changed_at.desc()',
    )
    interviews = db.relationship(
        'Interview',
        back_populates='application',
        cascade='all, delete-orphan',
        order_by='Interview.round_number.asc()',
    )

    def to_dict(self, include_history=False, include_interviews=False):
        data = {
            'application_id': self.application_id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'student_roll': self.student.roll_number if self.student else None,
            'student_email': self.student.user.email if self.student and self.student.user else None,
            'student_cgpa': float(self.student.cgpa) if self.student and self.student.cgpa is not None else None,
            'student_department': self.student.department.code if self.student and self.student.department else None,
            'opportunity_id': self.opportunity_id,
            'opportunity_title': self.opportunity.title if self.opportunity else None,
            'opportunity_type': self.opportunity.opportunity_type if self.opportunity else None,
            'company_name': self.opportunity.company.name if self.opportunity and self.opportunity.company else None,
            'status': self.status,
            'student_notes': self.student_notes,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_history and self.status_history:
            data['history'] = [h.to_dict() for h in self.status_history]
        if include_interviews and self.interviews:
            data['interviews'] = [i.to_dict() for i in self.interviews]
        return data

    def __repr__(self):
        return f"<Application {self.application_id}: Student {self.student_id} -> Opp {self.opportunity_id} [{self.status}]>"


class ApplicationStatusHistory(db.Model):
    __tablename__ = 'application_status_history'

    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(
        db.Integer, db.ForeignKey('applications.application_id', ondelete='CASCADE'), nullable=False, index=True
    )
    old_status = db.Column(db.String(30), nullable=True)
    new_status = db.Column(db.String(30), nullable=False)
    changed_by_user_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True
    )
    notes = db.Column(db.Text, nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    application = db.relationship('Application', back_populates='status_history')
    changed_by = db.relationship('User', foreign_keys=[changed_by_user_id])

    def to_dict(self):
        return {
            'history_id': self.history_id,
            'application_id': self.application_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_by_user_id': self.changed_by_user_id,
            'changed_by_email': self.changed_by.email if self.changed_by else 'System',
            'notes': self.notes,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
        }

    def __repr__(self):
        return f"<StatusHistory App {self.application_id}: {self.old_status} -> {self.new_status}>"
