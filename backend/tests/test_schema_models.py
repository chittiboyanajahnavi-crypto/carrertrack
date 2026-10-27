import os
import sys
import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.exc import IntegrityError

# Ensure backend directory is in sys.path when running directly or via pytest
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.extensions import db
from app.models import (
    User,
    Department,
    Student,
    Company,
    Recruiter,
    Skill,
    StudentSkill,
    Opportunity,
    OpportunityDepartment,
    OpportunitySkill,
    Application,
    ApplicationStatusHistory,
    Interview,
)


@pytest.fixture
def app():
    """Test application fixture configured with an isolated in-memory SQLite database."""
    test_app = create_app('testing')
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_models_creation_and_relationships(app):
    """Test full relational graph: Dept -> User -> Student -> Company -> Opp -> Skills -> App -> Interview."""
    with app.app_context():
        # 1. Department
        dept = Department(code='CSE', name='Computer Science and Engineering')
        db.session.add(dept)
        db.session.commit()
        assert dept.department_id is not None
        assert dept.to_dict()['code'] == 'CSE'

        # 2. Student User & Profile
        user = User(email='student1@test.com', role='student')
        user.set_password('Secret@123')
        db.session.add(user)
        db.session.commit()
        assert user.check_password('Secret@123') is True
        assert user.check_password('WrongPass') is False

        student = Student(
            user_id=user.user_id,
            roll_number='1CT22CS999',
            first_name='Aarav',
            last_name='Sharma',
            phone='+91 99999 88888',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=8.50,
        )
        db.session.add(student)
        db.session.commit()
        assert student.student_id is not None
        assert student.user.email == 'student1@test.com'
        assert student.department.code == 'CSE'
        assert student.full_name == 'Aarav Sharma'

        # 3. Skills & Student Skills (Many-to-Many)
        skill_python = Skill(name='Python', category='Technical')
        skill_dsa = Skill(name='Data Structures', category='Core CS')
        db.session.add_all([skill_python, skill_dsa])
        db.session.commit()

        student_skill = StudentSkill(
            student_id=student.student_id,
            skill_id=skill_python.skill_id,
            proficiency='Advanced',
        )
        db.session.add(student_skill)
        db.session.commit()
        assert len(student.student_skills) == 1
        assert student.student_skills[0].skill.name == 'Python'

        # 4. Company & Recruiter
        company = Company(
            name='Google India',
            industry='Cloud & AI',
            contact_email='recruiting@google.com',
        )
        db.session.add(company)
        db.session.commit()

        recruiter_user = User(email='recruiter@google.com', role='recruiter')
        recruiter_user.set_password('Recruiter@123')
        db.session.add(recruiter_user)
        db.session.commit()

        recruiter = Recruiter(
            user_id=recruiter_user.user_id,
            company_id=company.company_id,
            full_name='Priya Sharma',
            designation='University Recruiter',
        )
        db.session.add(recruiter)
        db.session.commit()
        assert recruiter.company.name == 'Google India'

        # 5. Opportunity with Department & Skill requirements
        opp = Opportunity(
            company_id=company.company_id,
            title='Software Engineering Intern',
            opportunity_type='Internship',
            description='Core distributed systems internship',
            min_cgpa=8.00,
            graduation_year=2026,
            location='Bengaluru',
            work_mode='Hybrid',
            salary_range='1,25,000/month',
            opening_date=date.today(),
            deadline=date.today() + timedelta(days=30),
            status='Active',
        )
        db.session.add(opp)
        db.session.commit()

        # Link eligible department & required skill
        opp_dept = OpportunityDepartment(opportunity_id=opp.opportunity_id, department_id=dept.department_id)
        opp_skill = OpportunitySkill(opportunity_id=opp.opportunity_id, skill_id=skill_python.skill_id, is_mandatory=True)
        db.session.add_all([opp_dept, opp_skill])
        db.session.commit()

        assert len(opp.opportunity_departments) == 1
        assert len(opp.opportunity_skills) == 1

        # 6. Application Submission
        app_record = Application(
            student_id=student.student_id,
            opportunity_id=opp.opportunity_id,
            status='Applied',
            student_notes='Passionate about scalable systems',
        )
        db.session.add(app_record)
        db.session.commit()
        assert app_record.application_id is not None

        # 7. Lifecycle Audit History & Interview Round
        history = ApplicationStatusHistory(
            application_id=app_record.application_id,
            old_status='Applied',
            new_status='Interview Scheduled',
            changed_by_user_id=recruiter_user.user_id,
            notes='Candidate passed automated screening',
        )
        interview = Interview(
            application_id=app_record.application_id,
            round_number=1,
            round_name='Technical Round 1',
            scheduled_at=datetime.utcnow() + timedelta(days=3),
            mode='Video Call',
            meeting_location_or_link='https://meet.google.com/test-room',
            interviewer_name='Senior Staff Engineer',
            outcome='Pending',
        )
        db.session.add_all([history, interview])
        db.session.commit()

        # Reload and verify child collections
        reloaded_app = db.session.get(Application, app_record.application_id)
        assert len(reloaded_app.status_history) == 1
        assert len(reloaded_app.interviews) == 1
        assert reloaded_app.status_history[0].new_status == 'Interview Scheduled'
        assert reloaded_app.interviews[0].round_name == 'Technical Round 1'


def test_duplicate_application_prevention(app):
    """Verify database unique constraint prevents duplicate applications for same student and opportunity."""
    with app.app_context():
        dept = Department(code='ISE', name='Information Science')
        user = User(email='diya@test.com', role='student')
        user.set_password('Pass@123')
        company = Company(name='Amazon', industry='Cloud', contact_email='jobs@amazon.com')
        db.session.add_all([dept, user, company])
        db.session.commit()

        student = Student(
            user_id=user.user_id,
            roll_number='1CT22IS002',
            first_name='Diya',
            last_name='Patel',
            phone='+91 99999 11111',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=9.10,
        )
        opp = Opportunity(
            company_id=company.company_id,
            title='Cloud Associate',
            opportunity_type='Full-Time',
            description='Cloud support',
            min_cgpa=7.50,
            graduation_year=2026,
            location='Hyderabad',
            work_mode='On-Site',
            salary_range='16 LPA',
            opening_date=date.today(),
            deadline=date.today() + timedelta(days=20),
            status='Active',
        )
        db.session.add_all([student, opp])
        db.session.commit()

        # First application succeeds
        app1 = Application(student_id=student.student_id, opportunity_id=opp.opportunity_id)
        db.session.add(app1)
        db.session.commit()
        assert app1.application_id is not None

        # Second duplicate application MUST trigger IntegrityError
        app2 = Application(student_id=student.student_id, opportunity_id=opp.opportunity_id)
        db.session.add(app2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_unique_constraints(app):
    """Verify unique constraints on user email and student roll number."""
    with app.app_context():
        # Duplicate user email must fail
        u1 = User(email='admin@test.com', role='admin')
        u1.set_password('Pass@123')
        db.session.add(u1)
        db.session.commit()

        u2 = User(email='admin@test.com', role='student')
        u2.set_password('Pass@123')
        db.session.add(u2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Duplicate student roll number must fail
        dept = Department(code='ECE', name='Electronics')
        u3 = User(email='student3@test.com', role='student')
        u3.set_password('Pass@123')
        u4 = User(email='student4@test.com', role='student')
        u4.set_password('Pass@123')
        db.session.add_all([dept, u3, u4])
        db.session.commit()

        s1 = Student(
            user_id=u3.user_id,
            roll_number='1CT22EC001',
            first_name='Ananya',
            last_name='R',
            phone='+91 99999 22222',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=8.20,
        )
        db.session.add(s1)
        db.session.commit()

        s2 = Student(
            user_id=u4.user_id,
            roll_number='1CT22EC001',  # Same roll number
            first_name='Another',
            last_name='Student',
            phone='+91 99999 33333',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=7.50,
        )
        db.session.add(s2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_cgpa_validation_constraints(app):
    """Verify CGPA boundaries: values below 0.00 or above 10.00 must be rejected by CHECK constraint."""
    with app.app_context():
        dept = Department(code='EEE', name='Electrical and Electronics')
        user = User(email='cgpa_test@test.com', role='student')
        user.set_password('Pass@123')
        db.session.add_all([dept, user])
        db.session.commit()

        # 1. CGPA above 10.00 must trigger IntegrityError
        student_too_high = Student(
            user_id=user.user_id,
            roll_number='1CT22EE991',
            first_name='Invalid',
            last_name='High',
            phone='+91 99999 00001',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=10.50,
        )
        db.session.add(student_too_high)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # 2. CGPA below 0.00 must trigger IntegrityError
        student_negative = Student(
            user_id=user.user_id,
            roll_number='1CT22EE992',
            first_name='Invalid',
            last_name='Negative',
            phone='+91 99999 00002',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=-1.50,
        )
        db.session.add(student_negative)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # 3. Valid boundary CGPA (0.00 and 10.00) must succeed
        student_valid = Student(
            user_id=user.user_id,
            roll_number='1CT22EE993',
            first_name='Valid',
            last_name='Boundary',
            phone='+91 99999 00003',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=10.00,
        )
        db.session.add(student_valid)
        db.session.commit()
        assert float(student_valid.cgpa) == 10.00


def test_cascade_delete_application(app):
    """Verify that deleting an application cleanly cascades to its status history and interviews."""
    with app.app_context():
        dept = Department(code='MECH', name='Mechanical Engineering')
        u_student = User(email='mech_student@test.com', role='student')
        u_student.set_password('Pass@123')
        company = Company(name='Qualcomm', industry='Semiconductors', contact_email='hr@qualcomm.com')
        db.session.add_all([dept, u_student, company])
        db.session.commit()

        student = Student(
            user_id=u_student.user_id,
            roll_number='1CT22ME001',
            first_name='Vikram',
            last_name='Singh',
            phone='+91 99999 44444',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=8.10,
        )
        opp = Opportunity(
            company_id=company.company_id,
            title='Firmware Engineer',
            opportunity_type='Full-Time',
            description='Firmware development',
            min_cgpa=7.50,
            graduation_year=2026,
            location='Bengaluru',
            work_mode='On-Site',
            salary_range='18 LPA',
            opening_date=date.today(),
            deadline=date.today() + timedelta(days=15),
            status='Active',
        )
        db.session.add_all([student, opp])
        db.session.commit()

        app_record = Application(student_id=student.student_id, opportunity_id=opp.opportunity_id)
        db.session.add(app_record)
        db.session.commit()

        history = ApplicationStatusHistory(
            application_id=app_record.application_id,
            old_status='Applied',
            new_status='Shortlisted',
            notes='Review passed',
        )
        interview = Interview(
            application_id=app_record.application_id,
            round_number=1,
            round_name='Technical 1',
            scheduled_at=datetime.utcnow() + timedelta(days=2),
            mode='In-Person',
            outcome='Pending',
        )
        db.session.add_all([history, interview])
        db.session.commit()

        app_id = app_record.application_id
        # Delete application
        db.session.delete(app_record)
        db.session.commit()

        # Verify child records were cascaded
        assert db.session.query(ApplicationStatusHistory).filter_by(application_id=app_id).count() == 0
        assert db.session.query(Interview).filter_by(application_id=app_id).count() == 0


if __name__ == '__main__':
    # Enables direct execution with: python backend/tests/test_schema_models.py
    pytest.main([__file__, '-v'])
