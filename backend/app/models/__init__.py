from app.models.user import User
from app.models.department import Department
from app.models.student import Student
from app.models.company import Company, Recruiter
from app.models.skill import Skill, StudentSkill, OpportunitySkill
from app.models.opportunity import Opportunity, OpportunityDepartment
from app.models.application import Application, ApplicationStatusHistory
from app.models.interview import Interview

__all__ = [
    'User',
    'Department',
    'Student',
    'Company',
    'Recruiter',
    'Skill',
    'StudentSkill',
    'OpportunitySkill',
    'Opportunity',
    'OpportunityDepartment',
    'Application',
    'ApplicationStatusHistory',
    'Interview',
]
