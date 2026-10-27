from datetime import datetime
from sqlalchemy import CheckConstraint
from app.extensions import db


class Interview(db.Model):
    __tablename__ = 'interviews'

    interview_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(
        db.Integer, db.ForeignKey('applications.application_id', ondelete='CASCADE'), nullable=False, index=True
    )
    round_number = db.Column(db.Integer, nullable=False)
    round_name = db.Column(db.String(100), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False, index=True)
    mode = db.Column(
        db.Enum('In-Person', 'Video Call', 'Phone', name='interview_mode_enum'),
        nullable=False,
    )
    meeting_location_or_link = db.Column(db.String(500), nullable=True)
    interviewer_name = db.Column(db.String(150), nullable=True)
    outcome = db.Column(
        db.Enum('Pending', 'Passed', 'Failed', 'Rescheduled', 'Cancelled', name='interview_outcome_enum'),
        nullable=False,
        default='Pending',
    )
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('round_number >= 1', name='chk_interview_round'),
    )

    # Relationships
    application = db.relationship('Application', back_populates='interviews')

    def to_dict(self):
        return {
            'interview_id': self.interview_id,
            'application_id': self.application_id,
            'round_number': self.round_number,
            'round_name': self.round_name,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'mode': self.mode,
            'meeting_location_or_link': self.meeting_location_or_link,
            'interviewer_name': self.interviewer_name,
            'outcome': self.outcome,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Interview {self.interview_id}: App {self.application_id} Round {self.round_number} ({self.outcome})>"
