import os
import sys
import pytest
from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models import (
    User,
    Department,
    Student,
    Company,
    Recruiter,
    Opportunity,
    OpportunityDepartment,
    OpportunitySkill,
    Application,
    ApplicationStatusHistory,
    Interview,
    Skill,
    StudentSkill,
)

# Ensure backend root is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


@pytest.fixture
def app():
    test_app = create_app('testing')
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'CareerTrack' in data['app']


def test_database_status_endpoint(client):
    """Test detailed database status endpoint."""
    response = client.get('/api/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'database' in data
    assert data['database']['status'] == 'connected'
    assert data['database']['tables_count'] >= 10
    assert 'timestamp' in data


def test_auth_flow_and_rbac(client, app):
    """Test login, session profile, RBAC enforcement, and logout."""
    with app.app_context():
        # Setup admin and student users
        admin_user = User(email='admin@test.edu', role='admin')
        admin_user.set_password('AdminPass@123')
        db.session.add(admin_user)

        dept = Department(code='CSE', name='Computer Science')
        student_user = User(email='student@test.edu', role='student')
        student_user.set_password('StudentPass@123')
        db.session.add_all([dept, student_user])
        db.session.commit()

        student = Student(
            user_id=student_user.user_id,
            roll_number='1CT22CS100',
            first_name='John',
            last_name='Doe',
            phone='9999900000',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=8.0,
        )
        db.session.add(student)
        db.session.commit()

    # 1. Accessing protected endpoint without login should return 401
    res = client.get('/api/admin/metrics')
    assert res.status_code == 401

    # 2. Login with incorrect password should return 401
    res = client.post('/api/auth/login', json={'email': 'admin@test.edu', 'password': 'WrongPassword'})
    assert res.status_code == 401

    # 3. Login as student
    res = client.post('/api/auth/login', json={'email': 'student@test.edu', 'password': 'StudentPass@123'})
    assert res.status_code == 200
    assert res.get_json()['data']['role'] == 'student'

    # 4. Student accessing admin metrics should return 403 Forbidden
    res = client.get('/api/admin/metrics')
    assert res.status_code == 403

    # 5. Access /api/auth/me returns student profile
    res = client.get('/api/auth/me')
    assert res.status_code == 200
    assert res.get_json()['data']['email'] == 'student@test.edu'

    # 6. Logout
    res = client.post('/api/auth/logout')
    assert res.status_code == 200

    # 7. Login as Admin
    res = client.post('/api/auth/login', json={'email': 'admin@test.edu', 'password': 'AdminPass@123'})
    assert res.status_code == 200

    # 8. Admin accessing admin metrics succeeds
    res = client.get('/api/admin/metrics')
    assert res.status_code == 200
    assert 'kpis' in res.get_json()['data']


def test_auth_registration_and_password_change(client, app):
    """Test student self-registration, validation, duplicate prevention, and password change."""
    with app.app_context():
        dept = Department(code='CSE', name='Computer Science')
        db.session.add(dept)
        db.session.commit()
        dept_id = dept.department_id

    # 1. Invalid registration data (short password, invalid CGPA)
    res_bad = client.post('/api/auth/register', json={
        'email': 'newstudent@test.edu',
        'password': 'short',
        'roll_number': '1CT22CS555',
        'first_name': 'New',
        'last_name': 'Student',
        'phone': '9876543210',
        'department_id': dept_id,
        'graduation_year': 2026,
        'cgpa': 12.5, # invalid > 10.0
    })
    assert res_bad.status_code == 400

    # 2. Successful student registration
    res_reg = client.post('/api/auth/register', json={
        'email': 'newstudent@test.edu',
        'password': 'StrongPassword@123',
        'roll_number': '1CT22CS555',
        'first_name': 'New',
        'last_name': 'Student',
        'phone': '9876543210',
        'department_id': dept_id,
        'graduation_year': 2026,
        'cgpa': 8.75,
    })
    assert res_reg.status_code == 201
    assert res_reg.get_json()['data']['roll_number'] == '1CT22CS555'

    # 3. Duplicate registration by email rejected
    res_dup_email = client.post('/api/auth/register', json={
        'email': 'newstudent@test.edu',
        'password': 'StrongPassword@123',
        'roll_number': '1CT22CS999',
        'first_name': 'Another',
        'last_name': 'Student',
        'phone': '9876543210',
        'department_id': dept_id,
        'graduation_year': 2026,
        'cgpa': 8.0,
    })
    assert res_dup_email.status_code == 409

    # 4. Duplicate registration by roll number rejected
    res_dup_roll = client.post('/api/auth/register', json={
        'email': 'different@test.edu',
        'password': 'StrongPassword@123',
        'roll_number': '1CT22CS555',
        'first_name': 'Another',
        'last_name': 'Student',
        'phone': '9876543210',
        'department_id': dept_id,
        'graduation_year': 2026,
        'cgpa': 8.0,
    })
    assert res_dup_roll.status_code == 409

    # 5. Login with new account
    res_login = client.post('/api/auth/login', json={
        'email': 'newstudent@test.edu',
        'password': 'StrongPassword@123'
    })
    assert res_login.status_code == 200

    # 6. Change password with incorrect current password fails
    res_cp_fail = client.post('/api/auth/change-password', json={
        'current_password': 'WrongPassword@123',
        'new_password': 'NewPassword@456'
    })
    assert res_cp_fail.status_code == 401

    # 7. Change password succeeds
    res_cp_ok = client.post('/api/auth/change-password', json={
        'current_password': 'StrongPassword@123',
        'new_password': 'NewPassword@456'
    })
    assert res_cp_ok.status_code == 200
    client.post('/api/auth/logout')

    # 8. Verify login with updated password
    res_relogin = client.post('/api/auth/login', json={
        'email': 'newstudent@test.edu',
        'password': 'NewPassword@456'
    })
    assert res_relogin.status_code == 200
    client.post('/api/auth/logout')



def test_application_lifecycle_and_eligibility(client, app):
    """Test eligibility evaluation, application submission, duplicate blocking, and status updates."""
    with app.app_context():
        # Setup Dept, Company, Opportunity
        dept = Department(code='CSE', name='Computer Science')
        company = Company(name='TechCorp', industry='Software', contact_email='hr@techcorp.com')
        db.session.add_all([dept, company])
        db.session.commit()

        opp = Opportunity(
            company_id=company.company_id,
            title='Software Engineer',
            opportunity_type='Full-Time',
            description='SWE Role',
            min_cgpa=8.00,
            graduation_year=2026,
            location='Bengaluru',
            salary_range='15 LPA',
            opening_date=date.today() - timedelta(days=5),
            deadline=date.today() + timedelta(days=20),
            status='Active',
        )
        db.session.add(opp)
        db.session.commit()

        opp_dept = OpportunityDepartment(opportunity_id=opp.opportunity_id, department_id=dept.department_id)
        db.session.add(opp_dept)

        # Setup Eligible Student
        u_eligible = User(email='eligible@test.edu', role='student')
        u_eligible.set_password('Pass@123')
        db.session.add(u_eligible)
        db.session.commit()

        s_eligible = Student(
            user_id=u_eligible.user_id,
            roll_number='1CT22CS001',
            first_name='Eligible',
            last_name='Student',
            phone='9876543210',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=8.50, # Eligible (>= 8.0)
        )
        # Setup Ineligible Student (Low CGPA)
        u_ineligible = User(email='lowcgpa@test.edu', role='student')
        u_ineligible.set_password('Pass@123')
        db.session.add(u_ineligible)
        db.session.commit()

        s_ineligible = Student(
            user_id=u_ineligible.user_id,
            roll_number='1CT22CS002',
            first_name='Low',
            last_name='CGPA',
            phone='9876543211',
            department_id=dept.department_id,
            graduation_year=2026,
            cgpa=7.20, # Ineligible (< 8.0)
        )
        db.session.add_all([s_eligible, s_ineligible])
        db.session.commit()

        opp_id = opp.opportunity_id

    # 1. Login as ineligible student and attempt application
    client.post('/api/auth/login', json={'email': 'lowcgpa@test.edu', 'password': 'Pass@123'})
    res = client.post('/api/applications', json={'opportunity_id': opp_id})
    assert res.status_code == 400
    assert 'not eligible' in res.get_json()['error'].lower()
    client.post('/api/auth/logout')

    # 2. Login as eligible student and submit application
    client.post('/api/auth/login', json={'email': 'eligible@test.edu', 'password': 'Pass@123'})
    res = client.post('/api/applications', json={
        'opportunity_id': opp_id,
        'student_notes': 'Excited to apply'
    })
    assert res.status_code == 201
    app_data = res.get_json()['data']
    app_id = app_data['application_id']
    assert app_data['status'] == 'Applied'

    # 3. Duplicate application attempt should fail
    res_dup = client.post('/api/applications', json={'opportunity_id': opp_id})
    assert res_dup.status_code == 400

    # 3b. Eligible student views own application details
    res_single = client.get(f'/api/applications/{app_id}')
    assert res_single.status_code == 200
    assert res_single.get_json()['data']['status'] == 'Applied'
    client.post('/api/auth/logout')

    # 3c. Another student tries to view app_id -> 403 Forbidden
    client.post('/api/auth/login', json={'email': 'lowcgpa@test.edu', 'password': 'Pass@123'})
    res_other = client.get(f'/api/applications/{app_id}')
    assert res_other.status_code == 403
    client.post('/api/auth/logout')

    # 4. Admin updates status to 'Shortlisted'
    with app.app_context():
        u_admin = User(email='officer@test.edu', role='admin')
        u_admin.set_password('Admin@123')
        db.session.add(u_admin)
        db.session.commit()

    client.post('/api/auth/login', json={'email': 'officer@test.edu', 'password': 'Admin@123'})
    res_status = client.patch(f'/api/applications/{app_id}/status', json={
        'status': 'Shortlisted',
        'notes': 'Profile cleared initial screening'
    })
    assert res_status.status_code == 200
    updated_data = res_status.get_json()['data']
    assert updated_data['status'] == 'Shortlisted'
    assert len(updated_data['history']) >= 1
    client.post('/api/auth/logout')

    # 5. Student withdraws application
    client.post('/api/auth/login', json={'email': 'eligible@test.edu', 'password': 'Pass@123'})
    res_withdraw = client.post(f'/api/applications/{app_id}/withdraw')
    assert res_withdraw.status_code == 200
    assert res_withdraw.get_json()['data']['status'] == 'Withdrawn'

    # Cannot withdraw already withdrawn application
    res_withdraw_again = client.post(f'/api/applications/{app_id}/withdraw')
    assert res_withdraw_again.status_code == 400
    client.post('/api/auth/logout')



def test_student_profile_and_skills_flow(client, app):
    """Test student profile update, skills management, and permissions."""
    with app.app_context():
        dept = Department(code='ISE', name='Information Science')
        u1 = User(email='s1@test.edu', role='student')
        u1.set_password('Pass@123')
        u2 = User(email='s2@test.edu', role='student')
        u2.set_password('Pass@123')
        sk1 = Skill(name='Python', category='Backend')
        sk2 = Skill(name='SQL', category='Database')
        db.session.add_all([dept, u1, u2, sk1, sk2])
        db.session.commit()

        s1 = Student(
            user_id=u1.user_id, roll_number='1CT22IS001', first_name='Alice',
            last_name='Smith', phone='', department_id=dept.department_id,
            graduation_year=2026, cgpa=9.10
        )
        s2 = Student(
            user_id=u2.user_id, roll_number='1CT22IS002', first_name='Bob',
            last_name='Jones', phone='1234567890', department_id=dept.department_id,
            graduation_year=2026, cgpa=8.20
        )
        db.session.add_all([s1, s2])
        db.session.commit()
        s1_id = s1.student_id
        s2_id = s2.student_id
        sk1_id = sk1.skill_id
        sk2_id = sk2.skill_id

    # 1. Login as Alice and update profile
    client.post('/api/auth/login', json={'email': 's1@test.edu', 'password': 'Pass@123'})
    res = client.put('/api/students/profile', json={
        'phone': '9876543210',
        'resume_url': 'https://storage.example.com/resumes/alice.pdf',
        'skills': [
            {'skill_id': sk1_id, 'proficiency': 'Advanced'},
            {'skill_id': sk2_id, 'proficiency': 'Intermediate'}
        ]
    })
    assert res.status_code == 200
    data = res.get_json()['data']
    assert data['phone'] == '9876543210'
    assert data['profile_complete'] is True
    assert len(data['skills']) == 2

    # 2. Alice tries to view Bob's profile -> 403 Forbidden
    res_forbidden = client.get(f'/api/students/{s2_id}')
    assert res_forbidden.status_code == 403

    # 3. Alice views own profile -> 200 OK
    res_own = client.get(f'/api/students/{s1_id}')
    assert res_own.status_code == 200

    # 3b. Alice views own profile via /profile and /me endpoints
    res_me = client.get('/api/students/profile')
    assert res_me.status_code == 200
    assert res_me.get_json()['data']['roll_number'] == '1CT22IS001'

    # 3c. Alice views own skills via /api/students/skills
    res_skills = client.get('/api/students/skills')
    assert res_skills.status_code == 200
    assert len(res_skills.get_json()['data']) == 2

    # 3d. Alice deletes a skill and adds a new one
    res_del_sk = client.delete(f'/api/students/skills/{sk2_id}')
    assert res_del_sk.status_code == 200

    res_add_sk = client.post('/api/students/skills', json={
        'skill_id': sk2_id,
        'proficiency': 'Advanced'
    })
    assert res_add_sk.status_code == 200
    assert res_add_sk.get_json()['data']['proficiency'] == 'Advanced'

    # 4. Student dashboard
    res_dash = client.get('/api/students/dashboard')
    assert res_dash.status_code == 200
    assert 'profile' in res_dash.get_json()['data']
    client.post('/api/auth/logout')

    # 5. Master skills taxonomy & departments endpoints
    res_tax = client.get('/api/skills')
    assert res_tax.status_code == 200
    assert len(res_tax.get_json()['data']) >= 2

    res_depts = client.get('/api/departments')
    assert res_depts.status_code == 200
    assert len(res_depts.get_json()['data']) >= 1



def test_company_and_recruiter_management(client, app):
    """Test company creation by admin and company updates by recruiter."""
    with app.app_context():
        admin = User(email='admin@corp.edu', role='admin')
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()

    # 1. Admin logs in and creates company
    client.post('/api/auth/login', json={'email': 'admin@corp.edu', 'password': 'Admin@123'})
    res_create = client.post('/api/companies', json={
        'name': 'InnovateTech',
        'industry': 'Artificial Intelligence',
        'contact_email': 'contact@innovatetech.com',
        'website': 'https://innovatetech.ai'
    })
    assert res_create.status_code == 201
    comp_id = res_create.get_json()['data']['company_id']

    # 2. Duplicate company creation fails
    res_dup = client.post('/api/companies', json={
        'name': 'InnovateTech',
        'industry': 'AI',
        'contact_email': 'contact@innovatetech.com'
    })
    assert res_dup.status_code == 409

    # 3. Create recruiter associated with company
    with app.app_context():
        rec_user = User(email='recruiter@innovatetech.com', role='recruiter')
        rec_user.set_password('Rec@123')
        db.session.add(rec_user)
        db.session.commit()

        recruiter = Recruiter(
            user_id=rec_user.user_id,
            company_id=comp_id,
            full_name='Samantha Ray',
            designation='Lead Recruiter'
        )
        db.session.add(recruiter)
        db.session.commit()

    client.post('/api/auth/logout')

    # 4. Recruiter updates company
    client.post('/api/auth/login', json={'email': 'recruiter@innovatetech.com', 'password': 'Rec@123'})
    res_update = client.put(f'/api/companies/{comp_id}', json={
        'description': 'Pioneering multimodal AI agents.'
    })
    assert res_update.status_code == 200
    assert res_update.get_json()['data']['description'] == 'Pioneering multimodal AI agents.'

    # 5. Get company details
    res_get = client.get(f'/api/companies/{comp_id}')
    assert res_get.status_code == 200
    assert res_get.get_json()['data']['name'] == 'InnovateTech'
    client.post('/api/auth/logout')


def test_interview_scheduling_and_lifecycle(client, app):
    """Test scheduling interview, updating outcome, and role access."""
    with app.app_context():
        dept = Department(code='ECE', name='Electronics')
        comp = Company(name='ChipCorp', industry='Semiconductors', contact_email='hr@chipcorp.com')
        db.session.add_all([dept, comp])
        db.session.commit()

        rec_u = User(email='hr@chipcorp.com', role='recruiter')
        rec_u.set_password('Rec@123')
        stud_u = User(email='ece_student@test.edu', role='student')
        stud_u.set_password('Student@123')
        db.session.add_all([rec_u, stud_u])
        db.session.commit()

        rec = Recruiter(user_id=rec_u.user_id, company_id=comp.company_id, full_name='John HR', designation='HR')
        stud = Student(
            user_id=stud_u.user_id, roll_number='1CT22EC001', first_name='Rahul',
            last_name='Verma', phone='9876543219', department_id=dept.department_id,
            graduation_year=2026, cgpa=8.80
        )
        opp = Opportunity(
            company_id=comp.company_id, title='Hardware Engineer', opportunity_type='Full-Time',
            description='SoC Verification', min_cgpa=8.0, graduation_year=2026,
            location='Bengaluru', salary_range='18 LPA',
            opening_date=date.today() - timedelta(days=2), deadline=date.today() + timedelta(days=10)
        )
        db.session.add_all([rec, stud, opp])
        db.session.commit()

        application = Application(
            student_id=stud.student_id, opportunity_id=opp.opportunity_id, status='Shortlisted'
        )
        db.session.add(application)
        db.session.commit()
        app_id = application.application_id

    # 1. Recruiter schedules interview
    client.post('/api/auth/login', json={'email': 'hr@chipcorp.com', 'password': 'Rec@123'})
    res_sched = client.post('/api/interviews', json={
        'application_id': app_id,
        'round_name': 'Technical Round 1',
        'scheduled_at': '2026-10-20T10:00:00',
        'mode': 'Video Call',
        'meeting_location_or_link': 'https://meet.google.com/abc-defg-hij',
        'interviewer_name': 'Dr. Sharma'
    })
    assert res_sched.status_code == 201
    intv_data = res_sched.get_json()['data']
    interview_id = intv_data['interview_id']
    assert intv_data['outcome'] == 'Pending'

    # Check that application status was transitioned to 'Interview Scheduled'
    with app.app_context():
        check_app = db.session.get(Application, app_id)
        assert check_app.status == 'Interview Scheduled'

    # 2. Recruiter updates interview outcome
    res_update = client.patch(f'/api/interviews/{interview_id}', json={
        'outcome': 'Passed',
        'feedback': 'Excellent problem solving skills.'
    })
    assert res_update.status_code == 200
    assert res_update.get_json()['data']['outcome'] == 'Passed'
    client.post('/api/auth/logout')

    # 3. Student views their interviews
    client.post('/api/auth/login', json={'email': 'ece_student@test.edu', 'password': 'Student@123'})
    res_list = client.get('/api/interviews')
    assert res_list.status_code == 200
    interviews = res_list.get_json()['data']
    assert len(interviews) >= 1
    assert interviews[0]['round_name'] == 'Technical Round 1'
    client.post('/api/auth/logout')


def test_reports_and_csv_export(client, app):
    """Test analytical placement reports and CSV export."""
    with app.app_context():
        admin = User(email='admin_reports@test.edu', role='admin')
        admin.set_password('Admin@123')
        stud_user = User(email='student_reports@test.edu', role='student')
        stud_user.set_password('Student@123')
        db.session.add_all([admin, stud_user])
        db.session.commit()

    # 1. Student accessing reports is forbidden (403)
    client.post('/api/auth/login', json={'email': 'student_reports@test.edu', 'password': 'Student@123'})
    res_forbidden = client.get('/api/reports/summary')
    assert res_forbidden.status_code == 403
    client.post('/api/auth/logout')

    # 2. Admin accessing reports summary succeeds
    client.post('/api/auth/login', json={'email': 'admin_reports@test.edu', 'password': 'Admin@123'})
    res_summary = client.get('/api/reports/summary')
    assert res_summary.status_code == 200
    assert 'total_applications' in res_summary.get_json()['data']

    # 3. Admin exporting CSV succeeds
    res_csv = client.get('/api/reports/export/csv')
    assert res_csv.status_code == 200
    assert 'text/csv' in res_csv.content_type
    client.post('/api/auth/logout')


def test_opportunity_listing_filtering_and_management(client, app):
    """Test filtering opportunities by type, dept, location, status update, and modification."""
    with app.app_context():
        d1 = Department(code='CSE', name='Computer Science')
        d2 = Department(code='MECH', name='Mechanical')
        comp = Company(name='AcmeCorp', industry='Tech', contact_email='hr@acmecorp.com')
        admin = User(email='opp_admin@test.edu', role='admin')
        admin.set_password('Admin@123')
        db.session.add_all([d1, d2, comp, admin])
        db.session.commit()

        opp1 = Opportunity(
            company_id=comp.company_id,
            title='Backend Software Developer',
            opportunity_type='Full-Time',
            description='Python & Go systems',
            min_cgpa=7.50,
            graduation_year=2026,
            location='Bengaluru',
            work_mode='Hybrid',
            salary_range='16 LPA',
            opening_date=date.today() - timedelta(days=5),
            deadline=date.today() + timedelta(days=20),
            status='Active',
        )
        opp2 = Opportunity(
            company_id=comp.company_id,
            title='Hardware Intern',
            opportunity_type='Internship',
            description='Circuit design',
            min_cgpa=8.50,
            graduation_year=2026,
            location='Hyderabad',
            work_mode='On-Site',
            salary_range='40,000 / month',
            opening_date=date.today() - timedelta(days=2),
            deadline=date.today() + timedelta(days=15),
            status='Active',
        )
        db.session.add_all([opp1, opp2])
        db.session.commit()

        # Link opp1 to CSE only
        db.session.add(OpportunityDepartment(opportunity_id=opp1.opportunity_id, department_id=d1.department_id))
        db.session.commit()
        opp1_id = opp1.opportunity_id
        opp2_id = opp2.opportunity_id
        d1_id = d1.department_id

    # 1. Login as admin
    client.post('/api/auth/login', json={'email': 'opp_admin@test.edu', 'password': 'Admin@123'})

    # 2. Filter by type 'Internship'
    res_intern = client.get('/api/opportunities?type=Internship')
    assert res_intern.status_code == 200
    assert len(res_intern.get_json()['data']) == 1
    assert res_intern.get_json()['data'][0]['title'] == 'Hardware Intern'

    # 3. Filter by location 'Bengaluru'
    res_loc = client.get('/api/opportunities?location=Bengaluru')
    assert res_loc.status_code == 200
    assert len(res_loc.get_json()['data']) == 1
    assert res_loc.get_json()['data'][0]['title'] == 'Backend Software Developer'

    # 4. Filter by department
    res_dept = client.get(f'/api/opportunities?department_id={d1_id}')
    assert res_dept.status_code == 200
    assert len(res_dept.get_json()['data']) == 1

    # 5. Update opportunity via PUT
    res_put = client.put(f'/api/opportunities/{opp1_id}', json={
        'title': 'Senior Backend Software Developer',
        'salary_range': '20 LPA',
        'work_mode': 'Remote'
    })
    assert res_put.status_code == 200
    assert res_put.get_json()['data']['title'] == 'Senior Backend Software Developer'
    assert res_put.get_json()['data']['work_mode'] == 'Remote'

    # 6. Update status via PATCH
    res_patch = client.patch(f'/api/opportunities/{opp1_id}/status', json={'status': 'Closed'})
    assert res_patch.status_code == 200
    assert res_patch.get_json()['data']['status'] == 'Closed'

    # 7. Delete opportunity (opp2 has no applications)
    res_del = client.delete(f'/api/opportunities/{opp2_id}')
    assert res_del.status_code == 200

    client.post('/api/auth/logout')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
