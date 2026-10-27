import React, { useState, useEffect } from 'react';
import { api } from './api';
import type {
  AuthProfile,
  Opportunity,
  Application,
  Interview,
  AdminMetrics,
  Department,
  Skill,
  Company,
  StudentProfile,
  SystemStatus,
  StudentDashboard,
} from './types';

export default function App() {
  const [currentUser, setCurrentUser] = useState<AuthProfile | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [activeTab, setActiveTab] = useState<string>('opportunities');
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Data states
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [myApplications, setMyApplications] = useState<Application[]>([]);
  const [companyApplications, setCompanyApplications] = useState<Application[]>([]);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [adminMetrics, setAdminMetrics] = useState<AdminMetrics | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [, setSkills] = useState<Skill[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [studentsList, setStudentsList] = useState<StudentProfile[]>([]);
  const [studentDashboard, setStudentDashboard] = useState<StudentDashboard | null>(null);
  const [profilePhone, setProfilePhone] = useState('');
  const [profileResume, setProfileResume] = useState('');

  // Filter states
  const [oppSearch, setOppSearch] = useState('');
  const [oppType, setOppType] = useState('');
  const [oppMode, setOppMode] = useState('');
  const [studentSearch, setStudentSearch] = useState('');
  const [studentDeptFilter, setStudentDeptFilter] = useState<string>('');

  // Modals
  const [loginModalOpen, setLoginModalOpen] = useState(false);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [registration, setRegistration] = useState({ email: '', password: '', first_name: '', last_name: '', roll_number: '', department_id: '', graduation_year: String(new Date().getFullYear() + 4), cgpa: '', phone: '' });

  const [applyModalOpp, setApplyModalOpp] = useState<Opportunity | null>(null);
  const [applyNotes, setApplyNotes] = useState('');
  const [applyLoading, setApplyLoading] = useState(false);

  const [createOppModalOpen, setCreateOppModalOpen] = useState(false);
  const [newOppTitle, setNewOppTitle] = useState('');
  const [newOppType, setNewOppType] = useState('Full-Time');
  const [newOppDesc, setNewOppDesc] = useState('');
  const [newOppLocation, setNewOppLocation] = useState('Bengaluru, India');
  const [newOppMode, setNewOppMode] = useState('Hybrid');
  const [newOppSalary, setNewOppSalary] = useState('₹18,00,000 - ₹24,00,000');
  const [newOppMinCgpa, setNewOppMinCgpa] = useState('7.5');
  const [newOppDeadline, setNewOppDeadline] = useState('2026-11-30');
  const [selectedDepts, setSelectedDepts] = useState<number[]>([]);

  const [scheduleModalApp, setScheduleModalApp] = useState<Application | null>(null);
  const [schedRoundName, setSchedRoundName] = useState('Technical Interview 1');
  const [schedDate, setSchedDate] = useState('2026-10-25T10:00');
  const [schedMode, setSchedMode] = useState('Video Call');
  const [schedUrl, setSchedUrl] = useState('https://meet.google.com/ct-interview-demo');

  // Load initial context
  useEffect(() => {
    initApp();
  }, []);

  const showNotification = (msg: string, isErr = false) => {
    if (isErr) {
      setErrorMsg(msg);
      setTimeout(() => setErrorMsg(null), 5000);
    } else {
      setSuccessMsg(msg);
      setTimeout(() => setSuccessMsg(null), 4000);
    }
  };

  const initApp = async () => {
    setLoading(true);
    try {
      // 1. Fetch system & DB status
      const status = await api.getSystemStatus().catch(() => null);
      if (status) setSystemStatus(status);

      // 2. Fetch master taxonomies
      const [deptData, skillData] = await Promise.all([
        api.getDepartments().catch(() => []),
        api.getSkills().catch(() => []),
      ]);
      setDepartments(deptData);
      setSkills(skillData);

      // 3. Check current authenticated user session
      try {
        const user = await api.getCurrentUser();
        const seededDemoEmails = ['aarav.sharma@careertrack.edu', 'priya.sharma@google.com', 'admin@careertrack.edu'];
        if (seededDemoEmails.includes(user.email.toLowerCase())) {
          await api.logout();
          setCurrentUser(null);
          setOpportunities([]);
        } else {
          setCurrentUser(user);
          await loadUserData(user);
        }
      } catch {
        // Guest mode
        setCurrentUser(null);
        setOpportunities([]);
      }
    } catch (err: unknown) {
      console.error(err);
      showNotification('Could not initialize the application. Check that the Flask API is running.', true);
    } finally {
      setLoading(false);
    }
  };

  const loadUserData = async (user: AuthProfile) => {
    try {
      if (user.role === 'student') {
        const [opps, apps, ints, dashboard, profile] = await Promise.all([
          api.getOpportunities(),
          api.getMyApplications().catch(() => []),
          api.getInterviews().catch(() => []),
          api.getStudentDashboard().catch(() => null),
          api.getMyProfile().catch(() => user.student ?? null),
        ]);
        setOpportunities(opps);
        setMyApplications(apps);
        setInterviews(ints);
        setStudentDashboard(dashboard);
        if (profile) {
          setProfilePhone(profile.phone ?? '');
          setProfileResume(profile.resume_url ?? '');
          setCurrentUser((current) => current ? { ...current, student: profile } : current);
        }
        setActiveTab('dashboard');
      } else if (user.role === 'recruiter') {
        const [opps, apps, ints] = await Promise.all([
          api.getOpportunities(user.recruiter?.company_id ? { company_id: user.recruiter.company_id } : {}),
          api.listApplications().catch(() => []),
          api.getInterviews().catch(() => []),
        ]);
        setOpportunities(opps);
        setCompanyApplications(apps);
        setInterviews(ints);
        setActiveTab('applicants');
      } else if (user.role === 'admin') {
        const [metrics, opps, stds, comps] = await Promise.all([
          api.getAdminMetrics().catch(() => null),
          api.getOpportunities().catch(() => []),
          api.getStudents().catch(() => []),
          api.getCompanies().catch(() => []),
        ]);
        setAdminMetrics(metrics);
        setOpportunities(opps);
        setStudentsList(stds);
        setCompanies(comps);
        setActiveTab('overview');
      }
    } catch (err: unknown) {
      console.error(err);
      showNotification((err as Error).message || 'Could not load account data.', true);
    }
  };

  // Demo role selection only fills a seeded account email; successful auth still requires the user's password.
  const handleDemoLogin = async (role: 'student' | 'recruiter' | 'admin') => {
    const emails = { student: 'aarav.sharma@careertrack.edu', recruiter: 'priya.sharma@google.com', admin: 'admin@careertrack.edu' };
    setLoginEmail(emails[role]);
    setLoginPassword('');
    setAuthMode('login');
    setLoginModalOpen(true);
  };

  const handleCustomLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    try {
      const user = await api.login(loginEmail, loginPassword);
      setCurrentUser(user);
      setLoginModalOpen(false);
      setLoginEmail('');
      setLoginPassword('');
      await loadUserData(user);
      showNotification(`Welcome back, ${user.email}!`);
    } catch (err: unknown) {
      setCurrentUser(null);
      setActiveTab('opportunities');
      setMyApplications([]);
      setCompanyApplications([]);
      setInterviews([]);
      showNotification((err as Error).message, true);
    } finally {
      setLoginLoading(false);
    }
  };

  const handleRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    try {
      await api.registerStudent({
        ...registration,
        department_id: Number(registration.department_id),
        graduation_year: Number(registration.graduation_year),
        cgpa: Number(registration.cgpa),
      });
      setLoginEmail(registration.email);
      setLoginPassword('');
      setAuthMode('login');
      showNotification('Account created. Sign in with your new credentials.');
    } catch (err) {
      showNotification((err as Error).message, true);
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      setCurrentUser(null);
      setActiveTab('opportunities');
      setOpportunities([]);
      showNotification('Logged out successfully.');
    } catch (err: unknown) {
      showNotification((err as Error).message, true);
    }
  };

  // Student apply
  const handleApply = async () => {
    if (!applyModalOpp) return;
    setApplyLoading(true);
    try {
      await api.applyOpportunity(applyModalOpp.opportunity_id, applyNotes);
      showNotification(`Successfully submitted application for ${applyModalOpp.title}!`);
      setApplyModalOpp(null);
      setApplyNotes('');
      if (currentUser) loadUserData(currentUser);
    } catch (err: unknown) {
      showNotification((err as Error).message, true);
    } finally {
      setApplyLoading(false);
    }
  };

  // Student withdraw
  const handleWithdraw = async (appId: number) => {
    if (!window.confirm('Are you sure you want to withdraw this application?')) return;
    try {
      await api.withdrawApplication(appId);
      showNotification('Application withdrawn successfully.');
      if (currentUser) loadUserData(currentUser);
    } catch (err: unknown) {
      showNotification((err as Error).message, true);
    }
  };

  // Recruiter update applicant status
  const handleUpdateStatus = async (appId: number, status: string) => {
    try {
      await api.updateApplicationStatus(appId, status, `Status changed to ${status} via recruiter portal.`);
      showNotification(`Applicant status updated to: ${status}`);
      if (currentUser) loadUserData(currentUser);
    } catch (err: unknown) {
      showNotification((err as Error).message, true);
    }
  };

  // Recruiter create opportunity
  const handleCreateOpportunity = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createOpportunity({
        title: newOppTitle,
        description: newOppDesc,
        opportunity_type: newOppType,
        location: newOppLocation,
        work_mode: newOppMode,
        salary_range: newOppSalary,
        min_cgpa: parseFloat(newOppMinCgpa) || 7.0,
        opening_date: new Date().toISOString().slice(0, 10),
        deadline: newOppDeadline,
        department_ids: selectedDepts.length > 0 ? selectedDepts : undefined,
      });
      showNotification(`Opportunity "${newOppTitle}" created successfully!`);
      setCreateOppModalOpen(false);
      setNewOppTitle('');
      setNewOppDesc('');
      if (currentUser) loadUserData(currentUser);
    } catch (err: unknown) {
      showNotification((err as Error).message, true);
    }
  };

  // Schedule interview
  const handleScheduleInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scheduleModalApp) return;
    try {
      await api.scheduleInterview({
        application_id: scheduleModalApp.application_id,
        round_name: schedRoundName,
        scheduled_at: schedDate.replace('T', ' ') + ':00',
        mode: schedMode,
        meeting_location_or_link: schedUrl,
      });
      showNotification(`Interview scheduled for ${scheduleModalApp.student?.full_name}!`);
      setScheduleModalApp(null);
      if (currentUser) loadUserData(currentUser);
    } catch (err: unknown) {
      showNotification((err as Error).message, true);
    }
  };

  // Filtered opportunities
  const filteredOpps = opportunities.filter((opp) => {
    const matchesSearch =
      !oppSearch ||
      opp.title.toLowerCase().includes(oppSearch.toLowerCase()) ||
      opp.company_name?.toLowerCase().includes(oppSearch.toLowerCase()) ||
      opp.location.toLowerCase().includes(oppSearch.toLowerCase());
    const matchesType = !oppType || opp.opportunity_type === oppType;
    const matchesMode = !oppMode || opp.work_mode === oppMode;
    return matchesSearch && matchesType && matchesMode;
  });

  // Filtered students
  const filteredStudents = studentsList.filter((s) => {
    const matchesSearch =
      !studentSearch ||
      s.full_name.toLowerCase().includes(studentSearch.toLowerCase()) ||
      s.roll_number.toLowerCase().includes(studentSearch.toLowerCase());
    const matchesDept =
      !studentDeptFilter || String(s.department_id) === studentDeptFilter;
    return matchesSearch && matchesDept;
  });

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {loading && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            height: 3,
            zIndex: 99999,
            background: 'linear-gradient(90deg, #6366f1, #06b6d4, #a855f7)',
            animation: 'pulse 1s infinite',
          }}
        />
      )}
      {/* Toast Notifications */}
      {errorMsg && (
        <div
          style={{
            position: 'fixed',
            top: 20,
            right: 20,
            zIndex: 9999,
            background: '#881337',
            border: '1px solid #f43f5e',
            color: '#fff',
            padding: '0.85rem 1.25rem',
            borderRadius: 12,
            boxShadow: '0 8px 30px rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}
        >
          <span>⚠️ {errorMsg}</span>
          <button
            onClick={() => setErrorMsg(null)}
            style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 'bold' }}
          >
            ✕
          </button>
        </div>
      )}

      {successMsg && (
        <div
          style={{
            position: 'fixed',
            top: 20,
            right: 20,
            zIndex: 9999,
            background: '#064e3b',
            border: '1px solid #10b981',
            color: '#fff',
            padding: '0.85rem 1.25rem',
            borderRadius: 12,
            boxShadow: '0 8px 30px rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}
        >
          <span>✅ {successMsg}</span>
          <button
            onClick={() => setSuccessMsg(null)}
            style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 'bold' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Quick Demo Switcher Bar */}
      <div className="role-switcher-banner">
        <div className="role-switcher-group">
          <span style={{ color: 'var(--text-dim)', fontWeight: 600 }}>DEMO ROLES:</span>
          <button
            className={`switcher-pill ${currentUser?.role === 'student' ? 'active' : ''}`}
            onClick={() => handleDemoLogin('student')}
          >
            <span>🎓</span> Student (Jahnavi - CSE)
          </button>
          <button
            className={`switcher-pill ${currentUser?.role === 'recruiter' ? 'active' : ''}`}
            onClick={() => handleDemoLogin('recruiter')}
          >
            <span>🏢</span> Recruiter (Priya @ Google)
          </button>
          <button
            className={`switcher-pill ${currentUser?.role === 'admin' ? 'active' : ''}`}
            onClick={() => handleDemoLogin('admin')}
          >
            <span>🛡️</span> Placement Admin
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {systemStatus && (
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.8rem', color: '#34d399' }}>
              <span className="pulse-dot" style={{ background: systemStatus.database.status === 'connected' ? '#10b981' : '#f43f5e' }}></span>
              <span style={{ color: systemStatus.database.status === 'connected' ? '#34d399' : '#fda4af' }}>
                MySQL {systemStatus.database.status === 'connected' ? 'Connected' : 'Disconnected'} ({systemStatus.database.tables_count} tables)
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Main Header */}
      <header className="header-container">
        <div className="header-content">
          <div className="logo-group" onClick={() => setActiveTab('opportunities')}>
            <div className="logo-icon-box">CT</div>
            <div className="logo-text">
              <h1>CareerTrack</h1>
              <span>Student Placement & Internship System</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {currentUser ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#fff' }}>
                    {currentUser.student
                      ? currentUser.student.full_name
                      : currentUser.recruiter
                      ? `${currentUser.recruiter.first_name} (${currentUser.recruiter.company_name})`
                      : 'Placement Officer'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>
                    {currentUser.role.toUpperCase()} • {currentUser.email}
                  </div>
                </div>
                <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
                  Log Out
                </button>
              </div>
            ) : (
              <button className="btn btn-primary btn-sm" onClick={() => setLoginModalOpen(true)}>
                Sign In / Demo
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Body Content */}
      <main className="main-content">
        {/* Navigation Tabs based on Role */}
        <nav className="tabs-nav">
          {(!currentUser || currentUser.role === 'student') && (
            <>
              {currentUser?.role === 'student' && (
                <button className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
                  📊 Dashboard
                </button>
              )}
              <button
                className={`tab-btn ${activeTab === 'opportunities' ? 'active' : ''}`}
                onClick={() => setActiveTab('opportunities')}
              >
                💼 Explore Opportunities ({opportunities.length})
              </button>
              {currentUser?.role === 'student' && (
                <>
                  <button
                    className={`tab-btn ${activeTab === 'my_applications' ? 'active' : ''}`}
                    onClick={() => setActiveTab('my_applications')}
                  >
                    📄 My Applications ({myApplications.length})
                  </button>
                  <button
                    className={`tab-btn ${activeTab === 'interviews' ? 'active' : ''}`}
                    onClick={() => setActiveTab('interviews')}
                  >
                    📅 Interviews ({interviews.length})
                  </button>
                  <button
                    className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
                    onClick={() => setActiveTab('profile')}
                  >
                    🎓 My Student Profile
                  </button>
                </>
              )}
            </>
          )}

          {currentUser?.role === 'recruiter' && (
            <>
              <button
                className={`tab-btn ${activeTab === 'applicants' ? 'active' : ''}`}
                onClick={() => setActiveTab('applicants')}
              >
                👥 Candidate Pipeline ({companyApplications.length})
              </button>
              <button
                className={`tab-btn ${activeTab === 'opportunities' ? 'active' : ''}`}
                onClick={() => setActiveTab('opportunities')}
              >
                💼 Job Postings ({opportunities.length})
              </button>
              <button
                className={`tab-btn ${activeTab === 'interviews' ? 'active' : ''}`}
                onClick={() => setActiveTab('interviews')}
              >
                🎙️ Scheduled Interviews ({interviews.length})
              </button>
            </>
          )}

          {currentUser?.role === 'admin' && (
            <>
              <button
                className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                📊 Executive Dashboard
              </button>
              <button
                className={`tab-btn ${activeTab === 'opportunities' ? 'active' : ''}`}
                onClick={() => setActiveTab('opportunities')}
              >
                💼 All Opportunities ({opportunities.length})
              </button>
              <button
                className={`tab-btn ${activeTab === 'students' ? 'active' : ''}`}
                onClick={() => setActiveTab('students')}
              >
                🎓 Students Roster ({studentsList.length})
              </button>
              <button
                className={`tab-btn ${activeTab === 'companies' ? 'active' : ''}`}
                onClick={() => setActiveTab('companies')}
              >
                🏢 Partner Companies ({companies.length})
              </button>
              <button
                className={`tab-btn ${activeTab === 'database' ? 'active' : ''}`}
                onClick={() => setActiveTab('database')}
              >
                ⚙️ Database Health (MySQL)
              </button>
            </>
          )}
        </nav>

        {/* ============================================================== */}
        {/* VIEW: OPPORTUNITIES (Guest, Student, Recruiter, Admin) */}
        {/* ============================================================== */}
        {activeTab === 'dashboard' && currentUser?.role === 'student' && (
          <section>
            <div style={{ marginBottom: '1.25rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>Welcome back, {currentUser.student?.first_name}</h2>
              <p style={{ color: 'var(--text-muted)' }}>Your placement progress and next steps at a glance.</p>
            </div>
            <div className="grid-cards" style={{ marginBottom: '1.5rem' }}>
              {[
                ['Applications', studentDashboard?.total_applications ?? myApplications.length],
                ['Eligible opportunities', studentDashboard?.eligible_opportunities_count ?? 0],
                ['Upcoming interviews', studentDashboard?.upcoming_interviews.length ?? interviews.length],
                ['CGPA', currentUser.student?.cgpa ?? '—'],
              ].map(([label, value]) => <div className="glass-panel" style={{ padding: '1.25rem' }} key={label}>
                <div style={{ color: 'var(--text-muted)', fontSize: '.85rem' }}>{label}</div>
                <strong style={{ display: 'block', fontSize: '1.8rem', marginTop: '.25rem' }}>{value}</strong>
              </div>)}
            </div>
            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <h3>Recommended opportunities</h3>
                <button className="btn btn-secondary btn-sm" onClick={() => setActiveTab('opportunities')}>Browse all</button>
              </div>
              {studentDashboard?.recommended_opportunities?.length ? <div className="grid-cards">
                {studentDashboard.recommended_opportunities.map((opp) => <article className="opp-card" key={opp.opportunity_id}>
                  <span className="badge badge-indigo">{opp.opportunity_type}</span><h3>{opp.title}</h3>
                  <div style={{ color: 'var(--accent-cyan)' }}>{opp.company_name} · {opp.location}</div>
                  <button className="btn btn-primary btn-sm" style={{ marginTop: '1rem' }} onClick={() => setActiveTab('opportunities')}>View opportunities</button>
                </article>)}
              </div> : <p style={{ color: 'var(--text-muted)' }}>Recommendations will appear here when eligible openings are available.</p>}
            </div>
          </section>
        )}

        {activeTab === 'opportunities' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>
                  {currentUser?.role === 'recruiter' ? 'Company Job Openings' : 'Explore Open Opportunities'}
                </h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  {currentUser?.role === 'student'
                    ? 'Opportunities evaluated against your academic CGPA, department, and skills.'
                    : 'Discover internships, full-time engineering and analyst roles.'}
                </p>
              </div>

              {currentUser?.role === 'recruiter' && (
                <button className="btn btn-primary" onClick={() => setCreateOppModalOpen(true)}>
                  + Post New Opportunity
                </button>
              )}
            </div>

            {/* Filter Bar */}
            <div className="filter-bar">
              <input
                type="text"
                placeholder="Search job title, company, or tech stack..."
                className="input-control"
                style={{ flex: '1 1 240px' }}
                value={oppSearch}
                onChange={(e) => setOppSearch(e.target.value)}
              />

              <select
                className="select-control"
                style={{ width: '160px' }}
                value={oppType}
                onChange={(e) => setOppType(e.target.value)}
              >
                <option value="">All Types</option>
                <option value="Full-time">Full-time</option>
                <option value="Internship">Internship</option>
                <option value="Co-op">Co-op</option>
              </select>

              <select
                className="select-control"
                style={{ width: '150px' }}
                value={oppMode}
                onChange={(e) => setOppMode(e.target.value)}
              >
                <option value="">All Modes</option>
                <option value="On-site">On-site</option>
                <option value="Hybrid">Hybrid</option>
                <option value="Remote">Remote</option>
              </select>
            </div>

            {/* Opportunity Cards Grid */}
            {filteredOpps.length === 0 ? (
              <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)' }}>{currentUser ? 'No opportunities match the current filter criteria.' : 'Sign in to view opportunities and submit applications.'}</p>
                {!currentUser && <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => setLoginModalOpen(true)}>Sign in</button>}
              </div>
            ) : (
              <div className="grid-cards">
                {filteredOpps.map((opp) => (
                  <div key={opp.opportunity_id} className="opp-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <span className="badge badge-indigo" style={{ marginBottom: '0.4rem' }}>
                          {opp.opportunity_type}
                        </span>
                        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', marginTop: '0.25rem' }}>
                          {opp.title}
                        </h3>
                        <div style={{ fontSize: '0.9rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                          {opp.company_name}
                        </div>
                      </div>

                      {currentUser?.role === 'student' && (
                        <div>
                          {opp.has_applied ? (
                            <span className="badge badge-emerald">Applied</span>
                          ) : opp.is_eligible ? (
                            <span className="badge badge-emerald">
                              Eligible ({opp.skills_match_score || 0}%)
                            </span>
                          ) : (
                            <span className="badge badge-rose">Not Eligible</span>
                          )}
                        </div>
                      )}
                    </div>

                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineClamp: 2, overflow: 'hidden' }}>
                      {opp.description}
                    </p>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                      <div>📍 {opp.location} ({opp.work_mode})</div>
                      <div>💰 {opp.salary_range || 'Competitive'}</div>
                      <div>🎯 Min CGPA: {opp.min_cgpa}</div>
                      <div>📅 Deadline: {opp.deadline}</div>
                    </div>

                    {/* Required Skills */}
                    {opp.required_skills && opp.required_skills.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                        {opp.required_skills.map((s) => (
                          <span
                            key={s.skill_id}
                            style={{
                              fontSize: '0.75rem',
                              padding: '0.2rem 0.5rem',
                              borderRadius: 4,
                              background: s.is_mandatory ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                              color: s.is_mandatory ? '#a5b4fc' : 'var(--text-muted)',
                              border: '1px solid var(--border-subtle)',
                            }}
                          >
                            {s.name} {s.is_mandatory && '★'}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Action Area */}
                    <div style={{ marginTop: 'auto', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
                      {currentUser?.role === 'student' ? (
                        opp.has_applied ? (
                          <button className="btn btn-secondary btn-sm" disabled style={{ width: '100%', opacity: 0.6 }}>
                            Application Submitted
                          </button>
                        ) : opp.is_eligible ? (
                          <button
                            className="btn btn-emerald btn-sm"
                            style={{ width: '100%' }}
                            onClick={() => setApplyModalOpp(opp)}
                          >
                            Apply Now →
                          </button>
                        ) : (
                          <div style={{ fontSize: '0.78rem', color: '#f87171' }}>
                            Reasons: {opp.eligibility_reasons?.join(', ') || 'Requirements not fulfilled'}
                          </div>
                        )
                      ) : !currentUser ? (
                        <button
                          className="btn btn-primary btn-sm"
                          style={{ width: '100%' }}
                          onClick={() => handleDemoLogin('student')}
                        >
                          Log in as Student to Apply
                        </button>
                      ) : (
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textAlign: 'right' }}>
                          Status: <span style={{ color: '#fff', fontWeight: 600 }}>{opp.status}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW: MY APPLICATIONS (Student) */}
        {/* ============================================================== */}
        {activeTab === 'my_applications' && currentUser?.role === 'student' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
              My Applications & Status Tracker
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              Track lifecycle updates from initial application through interviews and final selection.
            </p>

            {myApplications.length === 0 ? (
              <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)' }}>You have not submitted any applications yet.</p>
                <button
                  className="btn btn-primary"
                  style={{ marginTop: '1rem' }}
                  onClick={() => setActiveTab('opportunities')}
                >
                  Browse Available Opportunities
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {myApplications.map((app) => (
                  <div key={app.application_id} className="glass-panel" style={{ padding: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                      <div>
                        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>
                          {app.opportunity?.title}
                        </h3>
                        <div style={{ color: 'var(--accent-cyan)', fontWeight: 600, fontSize: '0.95rem' }}>
                          {app.opportunity?.company_name} • {app.opportunity?.opportunity_type}
                        </div>
                        <div style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '0.25rem' }}>
                          Applied on: {new Date(app.applied_at).toLocaleDateString()}
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span
                          className={`badge ${
                            app.status === 'Selected'
                              ? 'badge-emerald'
                              : app.status === 'Rejected'
                              ? 'badge-rose'
                              : app.status === 'Interview Scheduled'
                              ? 'badge-cyan'
                              : 'badge-amber'
                          }`}
                        >
                          {app.status}
                        </span>

                        {!['Selected', 'Rejected', 'Withdrawn'].includes(app.status) && (
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => handleWithdraw(app.application_id)}
                          >
                            Withdraw
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Status history timeline */}
                    {app.status_history && app.status_history.length > 0 && (
                      <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.5rem' }}>
                          STATUS TIMELINE:
                        </div>
                        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                          {app.status_history.map((hist, idx) => (
                            <div
                              key={hist.history_id || idx}
                              style={{
                                padding: '0.4rem 0.75rem',
                                background: 'rgba(255,255,255,0.03)',
                                borderRadius: 8,
                                border: '1px solid var(--border-subtle)',
                                fontSize: '0.8rem',
                              }}
                            >
                              <div style={{ fontWeight: 600, color: '#fff' }}>{hist.new_status}</div>
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                                {new Date(hist.changed_at).toLocaleString()}
                              </div>
                              {hist.notes && (
                                <div style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)' }}>{hist.notes}</div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW: RECRUITER APPLICANT PIPELINE */}
        {/* ============================================================== */}
        {activeTab === 'applicants' && currentUser?.role === 'recruiter' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>Candidate Application Pipeline</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  Review student credentials, advance interview rounds, or finalize selection.
                </p>
              </div>
            </div>

            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Roll No</th>
                    <th>Dept & CGPA</th>
                    <th>Applied For</th>
                    <th>Applied Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {companyApplications.length === 0 ? (
                    <tr>
                      <td colSpan={7} style={{ textAlign: 'center', padding: '2rem' }}>
                        No candidate applications found for your company postings yet.
                      </td>
                    </tr>
                  ) : (
                    companyApplications.map((app) => (
                      <tr key={app.application_id}>
                        <td>
                          <div style={{ fontWeight: 600, color: '#fff' }}>{app.student?.full_name}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{app.student?.email}</div>
                        </td>
                        <td>{app.student?.roll_number}</td>
                        <td>
                          <span className="badge badge-indigo">{app.student?.department_code}</span>{' '}
                          <strong>{app.student?.cgpa}</strong>
                        </td>
                        <td>{app.opportunity?.title}</td>
                        <td>{new Date(app.applied_at).toLocaleDateString()}</td>
                        <td>
                          <span
                            className={`badge ${
                              app.status === 'Selected'
                                ? 'badge-emerald'
                                : app.status === 'Rejected'
                                ? 'badge-rose'
                                : app.status === 'Interview Scheduled'
                                ? 'badge-cyan'
                                : 'badge-amber'
                            }`}
                          >
                            {app.status}
                          </span>
                        </td>
                        <td>
                          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                            {app.status === 'Applied' && (
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => handleUpdateStatus(app.application_id, 'Under Review')}
                              >
                                Review
                              </button>
                            )}

                            {['Applied', 'Under Review'].includes(app.status) && (
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => handleUpdateStatus(app.application_id, 'Shortlisted')}
                              >
                                Shortlist
                              </button>
                            )}

                            {['Shortlisted', 'Interview Scheduled'].includes(app.status) && (
                              <button
                                className="btn btn-primary btn-sm"
                                onClick={() => setScheduleModalApp(app)}
                              >
                                🎙️ Interview
                              </button>
                            )}

                            {app.status !== 'Selected' && app.status !== 'Rejected' && (
                              <>
                                <button
                                  className="btn btn-emerald btn-sm"
                                  onClick={() => handleUpdateStatus(app.application_id, 'Selected')}
                                >
                                  Select
                                </button>
                                <button
                                  className="btn btn-danger btn-sm"
                                  onClick={() => handleUpdateStatus(app.application_id, 'Rejected')}
                                >
                                  Reject
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW: INTERVIEWS (Student, Recruiter) */}
        {/* ============================================================== */}
        {activeTab === 'interviews' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
              Scheduled Interview Rounds
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              Real-time video/in-person interview rounds synchronized with MySQL database.
            </p>

            {interviews.length === 0 ? (
              <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-muted)' }}>No interview rounds scheduled yet.</p>
              </div>
            ) : (
              <div className="grid-cards">
                {interviews.map((intv) => (
                  <div key={intv.interview_id} className="glass-panel" style={{ padding: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span className="badge badge-cyan">{intv.mode}</span>
                      <span className="badge badge-emerald">{intv.status}</span>
                    </div>

                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', marginTop: '0.75rem' }}>
                      {intv.round_name}
                    </h3>
                    <div style={{ color: 'var(--accent-cyan)', fontWeight: 600, fontSize: '0.9rem' }}>
                      {intv.company_name} — {intv.opportunity_title}
                    </div>

                    {intv.student_name && (
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                        Candidate: <strong style={{ color: '#fff' }}>{intv.student_name}</strong> ({intv.student_roll})
                      </div>
                    )}

                    <div style={{ fontSize: '0.85rem', color: '#fbbf24', marginTop: '0.5rem' }}>
                      🕒 {new Date(intv.scheduled_at).toLocaleString()}
                    </div>

                    {intv.meeting_url && (
                      <div style={{ marginTop: '1rem' }}>
                        <a
                          href={intv.meeting_url}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-primary btn-sm"
                          style={{ width: '100%' }}
                        >
                          Join Meeting URL 🔗
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW: STUDENT PROFILE (Student) */}
        {/* ============================================================== */}
        {activeTab === 'profile' && currentUser?.student && (
          <div style={{ maxWidth: 840, margin: '0 auto' }}>
            <div className="glass-panel" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '1.5rem' }}>
                <div
                  style={{
                    width: 64,
                    height: 64,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.75rem',
                    fontWeight: 'bold',
                    color: '#fff',
                  }}
                >
                  {currentUser.student.first_name[0]}
                </div>
                <div>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>
                    {currentUser.student.full_name}
                  </h2>
                  <div style={{ color: 'var(--accent-cyan)', fontWeight: 500 }}>
                    {currentUser.student.roll_number} • {currentUser.student.department_name}
                  </div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>ACADEMIC CGPA</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#34d399' }}>{currentUser.student.cgpa}</div>
                </div>

                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>GRADUATION YEAR</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>{currentUser.student.graduation_year}</div>
                </div>

                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>DEPARTMENT CODE</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#818cf8' }}>{currentUser.student.department_code}</div>
                </div>
              </div>

              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '0.75rem' }}>
                Verified Skills & Competencies
              </h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {(currentUser.student.skills ?? []).map((sk) => (
                  <span key={sk.skill_id} className="badge badge-purple" style={{ fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}>
                    {sk.name} • {sk.proficiency || 'Intermediate'}
                  </span>
                ))}
              </div>
              <form onSubmit={async (e) => {
                e.preventDefault();
                try {
                  const profile = await api.updateMyProfile({ phone: profilePhone, resume_url: profileResume });
                  setCurrentUser((current) => current ? { ...current, student: profile } : current);
                  showNotification('Profile updated successfully.');
                } catch (err) { showNotification((err as Error).message, true); }
              }} style={{ display: 'grid', gap: '1rem', marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-subtle)' }}>
                <h3>Contact and resume</h3>
                <label>Phone<input className="input-control" value={profilePhone} onChange={(e) => setProfilePhone(e.target.value)} placeholder="Phone number" /></label>
                <label>Resume URL<input type="url" className="input-control" value={profileResume} onChange={(e) => setProfileResume(e.target.value)} placeholder="https://..." /></label>
                <button className="btn btn-primary" type="submit" style={{ justifySelf: 'start' }}>Save profile</button>
              </form>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW: ADMIN EXECUTIVE OVERVIEW */}
        {/* ============================================================== */}
        {activeTab === 'overview' && currentUser?.role === 'admin' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>Placement Administration & Analytics</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  Real-time Key Performance Indicators computed from relational MySQL tables.
                </p>
              </div>

              <a
                href="/api/reports/export/csv"
                target="_blank"
                download="careertrack_placement_report.csv"
                className="btn btn-emerald"
              >
                📥 Export CSV Placement Report
              </a>
            </div>

            {/* Top Metric KPI Cards */}
            {adminMetrics && (
              <>
                <div className="grid-metrics">
                  <div className="metric-card">
                    <div className="title">Total Enrolled Students</div>
                    <div className="value">{adminMetrics.total_students}</div>
                    <div className="subtitle">{adminMetrics.active_students} actively participating</div>
                  </div>

                  <div className="metric-card">
                    <div className="title">Placement Conversion Rate</div>
                    <div className="value" style={{ color: '#34d399' }}>
                      {adminMetrics.placement_rate_percent}%
                    </div>
                    <div className="subtitle">{adminMetrics.placed_students} students secured offers</div>
                  </div>

                  <div className="metric-card">
                    <div className="title">Job Openings Posted</div>
                    <div className="value">{adminMetrics.total_opportunities}</div>
                    <div className="subtitle">{adminMetrics.active_opportunities} currently active</div>
                  </div>

                  <div className="metric-card">
                    <div className="title">Total Applications</div>
                    <div className="value">{adminMetrics.total_applications}</div>
                    <div className="subtitle">Across {adminMetrics.total_companies} partner firms</div>
                  </div>
                </div>

                {/* Breakdown Grids */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem' }}>
                  {/* Department Stats */}
                  <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', marginBottom: '1rem' }}>
                      Placement Rate by Academic Department
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {adminMetrics.department_stats?.map((dept) => (
                        <div key={dept.department_id}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                            <span style={{ fontWeight: 600, color: '#fff' }}>
                              {dept.name} ({dept.code})
                            </span>
                            <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>
                              {dept.placed_students} / {dept.total_students} ({dept.placement_rate}%)
                            </span>
                          </div>
                          <div style={{ height: 6, borderRadius: 3, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
                            <div
                              style={{
                                width: `${dept.placement_rate}%`,
                                height: '100%',
                                background: 'linear-gradient(90deg, #6366f1, #06b6d4)',
                                borderRadius: 3,
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Company Offers Leaderboard */}
                  <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', marginBottom: '1rem' }}>
                      Top Recruiting Partners (Offers Made)
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {adminMetrics.company_offers?.map((comp, idx) => (
                        <div
                          key={comp.company_name}
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '0.65rem 1rem',
                            background: 'rgba(255,255,255,0.03)',
                            borderRadius: 8,
                            border: '1px solid var(--border-subtle)',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <span style={{ fontWeight: 700, color: 'var(--text-dim)' }}>#{idx + 1}</span>
                            <span style={{ fontWeight: 600, color: '#fff' }}>{comp.company_name}</span>
                          </div>
                          <span className="badge badge-emerald">{comp.offers_count} Selections</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW: STUDENTS ROSTER (Admin) */}
        {/* ============================================================== */}
        {activeTab === 'students' && currentUser?.role === 'admin' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>Student Academic Directory</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  Enrolled candidate database with department mappings and academic performance.
                </p>
              </div>
            </div>

            <div className="filter-bar">
              <input
                type="text"
                placeholder="Search by student name or roll number..."
                className="input-control"
                style={{ flex: '1 1 240px' }}
                value={studentSearch}
                onChange={(e) => setStudentSearch(e.target.value)}
              />

              <select
                className="select-control"
                style={{ width: '200px' }}
                value={studentDeptFilter}
                onChange={(e) => setStudentDeptFilter(e.target.value)}
              >
                <option value="">All Departments</option>
                {departments.map((d) => (
                  <option key={d.department_id} value={d.department_id}>
                    {d.code} - {d.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Roll Number</th>
                    <th>Full Name</th>
                    <th>Department</th>
                    <th>Graduation Year</th>
                    <th>CGPA</th>
                    <th>Skills Count</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.map((std) => (
                    <tr key={std.student_id}>
                      <td style={{ fontWeight: 600, color: '#fff' }}>{std.roll_number}</td>
                      <td>{std.full_name}</td>
                      <td>
                        <span className="badge badge-indigo">{std.department_code || 'Dept'}</span>
                      </td>
                      <td>{std.graduation_year}</td>
                      <td>
                        <strong style={{ color: std.cgpa >= 8.0 ? '#34d399' : '#fff' }}>{std.cgpa}</strong>
                      </td>
                      <td>{std.skills?.length || 0} verified skills</td>
                      <td>
                        <span className={`badge ${std.is_active ? 'badge-emerald' : 'badge-rose'}`}>
                          {std.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW: COMPANIES DIRECTORY (Admin) */}
        {/* ============================================================== */}
        {activeTab === 'companies' && currentUser?.role === 'admin' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
              Partner Recruiting Organizations
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              Corporate partners conducting campus placement and internship drives.
            </p>

            <div className="grid-cards">
              {companies.map((comp) => (
                <div key={comp.company_id} className="glass-panel" style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>{comp.name}</h3>
                    <span className="badge badge-indigo">{comp.industry}</span>
                  </div>

                  <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginTop: '0.5rem' }}>
                    ✉️ {comp.contact_email}
                  </div>
                  {comp.website && (
                    <div style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', marginTop: '0.25rem' }}>
                      🌐 <a href={comp.website} target="_blank" rel="noreferrer" style={{ color: 'inherit' }}>{comp.website}</a>
                    </div>
                  )}

                  <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                    <span style={{ color: 'var(--text-dim)' }}>Recruitment Status</span>
                    <span style={{ color: '#34d399', fontWeight: 600 }}>Active Partner</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* VIEW: DATABASE HEALTH (Admin) */}
        {/* ============================================================== */}
        {activeTab === 'database' && currentUser?.role === 'admin' && systemStatus && (
          <div style={{ maxWidth: 880, margin: '0 auto' }}>
            <div className="glass-panel" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>MySQL Database Schema Integrity</h2>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    Dialect: <strong>{systemStatus.database.dialect}</strong> | Host: <strong>127.0.0.1:3306</strong>
                  </div>
                </div>
                <span className="badge badge-emerald" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
                  ● {systemStatus.database.status.toUpperCase()}
                </span>
              </div>

              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '1rem' }}>
                Relational Tables Record Counts ({systemStatus.database.tables_count} verified tables)
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                {Object.entries(systemStatus.database.table_counts || {}).map(([tbl, cnt]) => (
                  <div
                    key={tbl}
                    style={{
                      padding: '1rem',
                      background: 'rgba(255,255,255,0.03)',
                      borderRadius: 8,
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                      Table: {tbl}
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>{cnt}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ============================================================== */}
      {/* MODAL: Apply to Opportunity (Student) */}
      {/* ============================================================== */}
      {applyModalOpp && (
        <div className="modal-overlay" onClick={() => setApplyModalOpp(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
              Submit Application
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
              Applying for <strong style={{ color: '#fff' }}>{applyModalOpp.title}</strong> at{' '}
              <strong style={{ color: 'var(--accent-cyan)' }}>{applyModalOpp.company_name}</strong>
            </p>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.5rem' }}>
                Cover Statement or Resume Notes (Optional)
              </label>
              <textarea
                rows={4}
                className="textarea-control"
                placeholder="Highlight your relevant course projects, certifications, or passion for this role..."
                value={applyNotes}
                onChange={(e) => setApplyNotes(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button className="btn btn-secondary" onClick={() => setApplyModalOpp(null)}>
                Cancel
              </button>
              <button className="btn btn-emerald" onClick={handleApply} disabled={applyLoading}>
                {applyLoading ? 'Submitting...' : 'Confirm & Apply'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* MODAL: Post Opportunity (Recruiter) */}
      {/* ============================================================== */}
      {createOppModalOpen && (
        <div className="modal-overlay" onClick={() => setCreateOppModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: '#fff', marginBottom: '1rem' }}>
              Create New Job Opportunity
            </h3>

            <form onSubmit={handleCreateOpportunity} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                  Job Title
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Software Engineer - Backend"
                  className="input-control"
                  value={newOppTitle}
                  onChange={(e) => setNewOppTitle(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                    Opportunity Type
                  </label>
                  <select
                    className="select-control"
                    value={newOppType}
                    onChange={(e) => setNewOppType(e.target.value)}
                  >
                <option value="Full-Time">Full-Time</option>
                    <option value="Internship">Internship</option>
                <option value="Part-Time">Part-Time</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                    Work Mode
                  </label>
                  <select
                    className="select-control"
                    value={newOppMode}
                    onChange={(e) => setNewOppMode(e.target.value)}
                  >
                    <option value="Hybrid">Hybrid</option>
                <option value="On-Site">On-Site</option>
                    <option value="Remote">Remote</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                    Minimum CGPA Cutoff
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="10"
                    required
                    className="input-control"
                    value={newOppMinCgpa}
                    onChange={(e) => setNewOppMinCgpa(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                    Application Deadline
                  </label>
                  <input
                    type="date"
                    required
                    className="input-control"
                    value={newOppDeadline}
                    onChange={(e) => setNewOppDeadline(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                  Salary / Compensation
                </label>
                <input
                  type="text"
                  placeholder="e.g. ₹18,00,000 - ₹24,00,000 CTC"
                  className="input-control"
                  value={newOppSalary}
                  onChange={(e) => setNewOppSalary(e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                  Location
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Bengaluru, India"
                  className="input-control"
                  value={newOppLocation}
                  onChange={(e) => setNewOppLocation(e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                  Eligible Departments
                </label>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {departments.map((d) => (
                    <button
                      type="button"
                      key={d.department_id}
                      onClick={() => {
                        setSelectedDepts((prev) =>
                          prev.includes(d.department_id)
                            ? prev.filter((id) => id !== d.department_id)
                            : [...prev, d.department_id]
                        );
                      }}
                      className="btn btn-sm"
                      style={{
                        background: selectedDepts.includes(d.department_id) ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255, 255, 255, 0.05)',
                        border: selectedDepts.includes(d.department_id) ? '1px solid var(--primary)' : '1px solid var(--border-subtle)',
                        color: selectedDepts.includes(d.department_id) ? '#fff' : 'var(--text-muted)',
                      }}
                    >
                      {d.code}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                  Job Description & Qualifications
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="Responsibilities, requirements, technology expectations..."
                  className="textarea-control"
                  value={newOppDesc}
                  onChange={(e) => setNewOppDesc(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setCreateOppModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Publish Opening
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* MODAL: Schedule Interview (Recruiter) */}
      {/* ============================================================== */}
      {scheduleModalApp && (
        <div className="modal-overlay" onClick={() => setScheduleModalApp(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
              Schedule Interview Round
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
              Candidate: <strong style={{ color: '#fff' }}>{scheduleModalApp.student?.full_name}</strong> (
              {scheduleModalApp.student?.roll_number})
            </p>

            <form onSubmit={handleScheduleInterview} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                  Round Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Technical Coding Round 1"
                  className="input-control"
                  value={schedRoundName}
                  onChange={(e) => setSchedRoundName(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                    Scheduled Date & Time
                  </label>
                  <input
                    type="datetime-local"
                    required
                    className="input-control"
                    value={schedDate}
                    onChange={(e) => setSchedDate(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                    Interview Mode
                  </label>
                  <select
                    className="select-control"
                    value={schedMode}
                    onChange={(e) => setSchedMode(e.target.value)}
                  >
                    <option value="Video Call">Video Call</option>
                    <option value="In-Person">In-person</option>
                    <option value="Phone">Phone</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                  Meeting URL
                </label>
                <input
                  type="url"
                  placeholder="https://meet.google.com/..."
                  className="input-control"
                  value={schedUrl}
                  onChange={(e) => setSchedUrl(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setScheduleModalApp(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Confirm Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* MODAL: Sign In */}
      {/* ============================================================== */}
        {loginModalOpen && (
        <div className="modal-overlay" onClick={() => setLoginModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
              {authMode === 'login' ? 'Sign In to CareerTrack' : 'Create a student account'}
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
              {authMode === 'login' ? 'Enter your registered credentials. Demo role buttons select seeded accounts but still require a password.' : 'Register with your details. The backend creates your account and student profile.'}
            </p>

            {authMode === 'login' ? <form onSubmit={handleCustomLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  className="input-control"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.35rem' }}>
                  Password
                </label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="input-control"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setLoginModalOpen(false)}>
                  Cancel
                </button>
                <button type="button" className="btn btn-secondary" onClick={() => setAuthMode('register')}>Create account</button>
                <button type="submit" className="btn btn-primary" disabled={loginLoading}>
                  {loginLoading ? 'Signing In...' : 'Sign In'}
                </button>
              </div>
            </form> : <form onSubmit={handleRegistration} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '.75rem' }}>
              <input className="input-control" type="email" required placeholder="Email" value={registration.email} onChange={(e) => setRegistration({ ...registration, email: e.target.value })} />
              <input className="input-control" type="password" minLength={8} required placeholder="Password (8+ characters)" value={registration.password} onChange={(e) => setRegistration({ ...registration, password: e.target.value })} />
              <input className="input-control" required placeholder="First name" value={registration.first_name} onChange={(e) => setRegistration({ ...registration, first_name: e.target.value })} />
              <input className="input-control" required placeholder="Last name" value={registration.last_name} onChange={(e) => setRegistration({ ...registration, last_name: e.target.value })} />
              <input className="input-control" required placeholder="Roll number" value={registration.roll_number} onChange={(e) => setRegistration({ ...registration, roll_number: e.target.value })} />
              <select className="select-control" required value={registration.department_id} onChange={(e) => setRegistration({ ...registration, department_id: e.target.value })}>
                <option value="">Select department</option>{departments.map((d) => <option key={d.department_id} value={d.department_id}>{d.code} · {d.name}</option>)}
              </select>
              <input className="input-control" type="number" min="2000" max="2100" required placeholder="Graduation year" value={registration.graduation_year} onChange={(e) => setRegistration({ ...registration, graduation_year: e.target.value })} />
              <input className="input-control" type="number" min="0" max="10" step="0.01" required placeholder="CGPA" value={registration.cgpa} onChange={(e) => setRegistration({ ...registration, cgpa: e.target.value })} />
              <input className="input-control" type="tel" required placeholder="Phone" value={registration.phone} onChange={(e) => setRegistration({ ...registration, phone: e.target.value })} />
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '.5rem', gridColumn: '1 / -1' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setAuthMode('login')}>Back to sign in</button>
                <button type="submit" className="btn btn-primary" disabled={loginLoading}>{loginLoading ? 'Creating…' : 'Create account'}</button>
              </div>
            </form>}
          </div>
        </div>
      )}
    </div>
  );
}
