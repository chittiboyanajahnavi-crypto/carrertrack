-- ============================================================================
-- Student Placement & Internship Management System (CareerTrack)
-- Script 02: Relational Schema DDL (MySQL 8.0, 3NF Normalized)
-- ============================================================================

USE careertrack_db;

-- Disable foreign key checks during schema drops/rebuilds
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS interviews;
DROP TABLE IF EXISTS application_status_history;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS opportunity_departments;
DROP TABLE IF EXISTS opportunity_skills;
DROP TABLE IF EXISTS opportunities;
DROP TABLE IF EXISTS student_skills;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS recruiters;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- 1. DEPARTMENTS
-- ----------------------------------------------------------------------------
CREATE TABLE departments (
    department_id INT NOT NULL AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_departments PRIMARY KEY (department_id),
    CONSTRAINT uq_department_code UNIQUE (code),
    CONSTRAINT uq_department_name UNIQUE (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. USERS (Authentication & Role Base)
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'student', 'recruiter') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uq_users_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. STUDENTS (Student Academic Profile)
-- ----------------------------------------------------------------------------
CREATE TABLE students (
    student_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    roll_number VARCHAR(30) NOT NULL,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    department_id INT NOT NULL,
    graduation_year INT NOT NULL,
    cgpa DECIMAL(4,2) NOT NULL,
    resume_url VARCHAR(255) DEFAULT NULL,
    profile_complete BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_students PRIMARY KEY (student_id),
    CONSTRAINT uq_students_user_id UNIQUE (user_id),
    CONSTRAINT uq_students_roll_number UNIQUE (roll_number),
    CONSTRAINT fk_students_user FOREIGN KEY (user_id) 
        REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_students_department FOREIGN KEY (department_id) 
        REFERENCES departments (department_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_student_cgpa CHECK (cgpa >= 0.00 AND cgpa <= 10.00),
    CONSTRAINT chk_student_grad_year CHECK (graduation_year >= 2000 AND graduation_year <= 2100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_students_department ON students (department_id);
CREATE INDEX idx_students_cgpa ON students (cgpa);
CREATE INDEX idx_students_grad_year ON students (graduation_year);

-- ----------------------------------------------------------------------------
-- 4. COMPANIES (Recruiting Organizations)
-- ----------------------------------------------------------------------------
CREATE TABLE companies (
    company_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    website VARCHAR(255) DEFAULT NULL,
    contact_email VARCHAR(150) NOT NULL,
    contact_phone VARCHAR(25) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_companies PRIMARY KEY (company_id),
    CONSTRAINT uq_companies_name UNIQUE (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_companies_industry ON companies (industry);

-- ----------------------------------------------------------------------------
-- 5. RECRUITERS (Company HR Representatives)
-- ----------------------------------------------------------------------------
CREATE TABLE recruiters (
    recruiter_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_recruiters PRIMARY KEY (recruiter_id),
    CONSTRAINT uq_recruiters_user_id UNIQUE (user_id),
    CONSTRAINT fk_recruiters_user FOREIGN KEY (user_id) 
        REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_recruiters_company FOREIGN KEY (company_id) 
        REFERENCES companies (company_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_recruiters_company ON recruiters (company_id);

-- ----------------------------------------------------------------------------
-- 6. SKILLS (Master Taxonomy)
-- ----------------------------------------------------------------------------
CREATE TABLE skills (
    skill_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(80) NOT NULL,
    category VARCHAR(60) NOT NULL DEFAULT 'Technical',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_skills PRIMARY KEY (skill_id),
    CONSTRAINT uq_skills_name UNIQUE (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 7. STUDENT_SKILLS (Student Technical Profile)
-- ----------------------------------------------------------------------------
CREATE TABLE student_skills (
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency ENUM('Beginner', 'Intermediate', 'Advanced') NOT NULL DEFAULT 'Intermediate',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_student_skills PRIMARY KEY (student_id, skill_id),
    CONSTRAINT fk_student_skills_student FOREIGN KEY (student_id) 
        REFERENCES students (student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_student_skills_skill FOREIGN KEY (skill_id) 
        REFERENCES skills (skill_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 8. OPPORTUNITIES (Jobs & Internships)
-- ----------------------------------------------------------------------------
CREATE TABLE opportunities (
    opportunity_id INT NOT NULL AUTO_INCREMENT,
    company_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    opportunity_type ENUM('Full-Time', 'Internship', 'Part-Time') NOT NULL,
    description TEXT NOT NULL,
    min_cgpa DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    graduation_year INT NOT NULL,
    location VARCHAR(120) NOT NULL,
    work_mode ENUM('On-Site', 'Remote', 'Hybrid') NOT NULL DEFAULT 'On-Site',
    salary_range VARCHAR(80) NOT NULL,
    opening_date DATE NOT NULL,
    deadline DATE NOT NULL,
    status ENUM('Active', 'Closed', 'Draft') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_opportunities PRIMARY KEY (opportunity_id),
    CONSTRAINT fk_opportunities_company FOREIGN KEY (company_id) 
        REFERENCES companies (company_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_opportunity_cgpa CHECK (min_cgpa >= 0.00 AND min_cgpa <= 10.00),
    CONSTRAINT chk_opportunity_dates CHECK (deadline >= opening_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_opportunities_company ON opportunities (company_id);
CREATE INDEX idx_opportunities_status_deadline ON opportunities (status, deadline);
CREATE INDEX idx_opportunities_type ON opportunities (opportunity_type);

-- ----------------------------------------------------------------------------
-- 9. OPPORTUNITY_SKILLS (Required Qualifications)
-- ----------------------------------------------------------------------------
CREATE TABLE opportunity_skills (
    opportunity_id INT NOT NULL,
    skill_id INT NOT NULL,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_opportunity_skills PRIMARY KEY (opportunity_id, skill_id),
    CONSTRAINT fk_opportunity_skills_opp FOREIGN KEY (opportunity_id) 
        REFERENCES opportunities (opportunity_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_opportunity_skills_skill FOREIGN KEY (skill_id) 
        REFERENCES skills (skill_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 10. OPPORTUNITY_DEPARTMENTS (Department-Wise Eligibility)
-- ----------------------------------------------------------------------------
CREATE TABLE opportunity_departments (
    opportunity_id INT NOT NULL,
    department_id INT NOT NULL,
    CONSTRAINT pk_opportunity_departments PRIMARY KEY (opportunity_id, department_id),
    CONSTRAINT fk_opportunity_dept_opp FOREIGN KEY (opportunity_id) 
        REFERENCES opportunities (opportunity_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_opportunity_dept_dept FOREIGN KEY (department_id) 
        REFERENCES departments (department_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 11. APPLICATIONS (Student Submissions)
-- ----------------------------------------------------------------------------
CREATE TABLE applications (
    application_id INT NOT NULL AUTO_INCREMENT,
    student_id INT NOT NULL,
    opportunity_id INT NOT NULL,
    status ENUM('Applied', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected', 'Withdrawn') NOT NULL DEFAULT 'Applied',
    student_notes TEXT DEFAULT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_applications PRIMARY KEY (application_id),
    -- CRITICAL INTEGRITY RULE: Prevent duplicate applications per student and opportunity
    CONSTRAINT uq_student_opportunity UNIQUE (student_id, opportunity_id),
    CONSTRAINT fk_applications_student FOREIGN KEY (student_id) 
        REFERENCES students (student_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_applications_opportunity FOREIGN KEY (opportunity_id) 
        REFERENCES opportunities (opportunity_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_applications_student ON applications (student_id);
CREATE INDEX idx_applications_opportunity ON applications (opportunity_id);
CREATE INDEX idx_applications_status ON applications (status);

-- ----------------------------------------------------------------------------
-- 12. APPLICATION_STATUS_HISTORY (Lifecycle Audit Trail)
-- ----------------------------------------------------------------------------
CREATE TABLE application_status_history (
    history_id INT NOT NULL AUTO_INCREMENT,
    application_id INT NOT NULL,
    old_status VARCHAR(30) DEFAULT NULL,
    new_status VARCHAR(30) NOT NULL,
    changed_by_user_id INT DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_app_status_history PRIMARY KEY (history_id),
    CONSTRAINT fk_app_history_app FOREIGN KEY (application_id) 
        REFERENCES applications (application_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_app_history_user FOREIGN KEY (changed_by_user_id) 
        REFERENCES users (user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_history_application ON application_status_history (application_id);

-- ----------------------------------------------------------------------------
-- 13. INTERVIEWS (Interview Schedules & Rounds)
-- ----------------------------------------------------------------------------
CREATE TABLE interviews (
    interview_id INT NOT NULL AUTO_INCREMENT,
    application_id INT NOT NULL,
    round_number INT NOT NULL,
    round_name VARCHAR(100) NOT NULL,
    scheduled_at DATETIME NOT NULL,
    mode ENUM('In-Person', 'Video Call', 'Phone') NOT NULL,
    meeting_location_or_link VARCHAR(500) DEFAULT NULL,
    interviewer_name VARCHAR(150) DEFAULT NULL,
    outcome ENUM('Pending', 'Passed', 'Failed', 'Rescheduled', 'Cancelled') NOT NULL DEFAULT 'Pending',
    feedback TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_interviews PRIMARY KEY (interview_id),
    CONSTRAINT fk_interviews_application FOREIGN KEY (application_id) 
        REFERENCES applications (application_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_interview_round CHECK (round_number >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_interviews_application ON interviews (application_id);
CREATE INDEX idx_interviews_scheduled ON interviews (scheduled_at);
