-- ============================================================================
-- Student Placement & Internship Management System (CareerTrack)
-- Script 03: Realistic Fictional Seed Data
-- ============================================================================
-- Standard demo credentials created in this script:
--   Admin:     admin@careertrack.edu          / Admin@123
--   Recruiter: priya.sharma@google.com        / Recruiter@123
--   Recruiter: vikas.mehta@microsoft.com      / Recruiter@123
--   Recruiter: sarah.jenkins@amazon.com       / Recruiter@123
--   Recruiter: arun.patel@tcs.com             / Recruiter@123
--   Demo student: aarav.sharma@careertrack.edu (display name: Jahnavi Chittiboyana)
--   Student:   diya.patel@careertrack.edu     / Student@123
--   Student:   rohan.gupta@careertrack.edu    / Student@123
--   Student:   ananya.reddy@careertrack.edu   / Student@123
--   Student:   kavya.nair@careertrack.edu     / Student@123
--   Student:   vikram.singh@careertrack.edu   / Student@123
-- ============================================================================

USE careertrack_db;

-- ----------------------------------------------------------------------------
-- 1. DEPARTMENTS
-- ----------------------------------------------------------------------------
INSERT INTO departments (department_id, code, name) VALUES
(1, 'CSE', 'Computer Science and Engineering'),
(2, 'ISE', 'Information Science and Engineering'),
(3, 'ECE', 'Electronics and Communication Engineering'),
(4, 'EEE', 'Electrical and Electronics Engineering'),
(5, 'MECH', 'Mechanical Engineering')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ----------------------------------------------------------------------------
-- 2. USERS (Pass: Admin@123 / Recruiter@123 / Student@123)
-- ----------------------------------------------------------------------------
INSERT INTO users (user_id, email, password_hash, role, is_active) VALUES
(1, 'admin@careertrack.edu', 'scrypt:32768:8:1$Ks4W0L9jxVJ9J0qZ$363c17393839dfa084e5d5247900dc4c805f05b67dd0448f7e899b8b25df799da52aba180ad1e58c326af017b653075c1c4742b4b8e2e0b4a9fa0be34fb22ca7', 'admin', 1),
(2, 'priya.sharma@google.com', 'scrypt:32768:8:1$DE6EjZdnliwtCsbL$6b30bad8b165fb282bfbd1969d215ccf31177e7627e71eb9531b0553420d1add7debdcbfb3fba9b5fc6ff4ce1a819bd2192fe979ad3668bfb1beab8faca73ed1', 'recruiter', 1),
(3, 'vikas.mehta@microsoft.com', 'scrypt:32768:8:1$DE6EjZdnliwtCsbL$6b30bad8b165fb282bfbd1969d215ccf31177e7627e71eb9531b0553420d1add7debdcbfb3fba9b5fc6ff4ce1a819bd2192fe979ad3668bfb1beab8faca73ed1', 'recruiter', 1),
(4, 'sarah.jenkins@amazon.com', 'scrypt:32768:8:1$DE6EjZdnliwtCsbL$6b30bad8b165fb282bfbd1969d215ccf31177e7627e71eb9531b0553420d1add7debdcbfb3fba9b5fc6ff4ce1a819bd2192fe979ad3668bfb1beab8faca73ed1', 'recruiter', 1),
(5, 'arun.patel@tcs.com', 'scrypt:32768:8:1$DE6EjZdnliwtCsbL$6b30bad8b165fb282bfbd1969d215ccf31177e7627e71eb9531b0553420d1add7debdcbfb3fba9b5fc6ff4ce1a819bd2192fe979ad3668bfb1beab8faca73ed1', 'recruiter', 1),
(6, 'aarav.sharma@careertrack.edu', 'scrypt:32768:8:1$vrjQRJNp8zTC6wyy$f8aa5411d7a389b5df409f3bc5502d9afe72e6cb6822510d3fae68ce35b7ed5c9f77eed2ccd71f1c4dc33ce58e29d4dd4b71d4da602836dacc7575cfcfd631f4', 'student', 1),
(7, 'diya.patel@careertrack.edu', 'scrypt:32768:8:1$vrjQRJNp8zTC6wyy$f8aa5411d7a389b5df409f3bc5502d9afe72e6cb6822510d3fae68ce35b7ed5c9f77eed2ccd71f1c4dc33ce58e29d4dd4b71d4da602836dacc7575cfcfd631f4', 'student', 1),
(8, 'rohan.gupta@careertrack.edu', 'scrypt:32768:8:1$vrjQRJNp8zTC6wyy$f8aa5411d7a389b5df409f3bc5502d9afe72e6cb6822510d3fae68ce35b7ed5c9f77eed2ccd71f1c4dc33ce58e29d4dd4b71d4da602836dacc7575cfcfd631f4', 'student', 1),
(9, 'ananya.reddy@careertrack.edu', 'scrypt:32768:8:1$vrjQRJNp8zTC6wyy$f8aa5411d7a389b5df409f3bc5502d9afe72e6cb6822510d3fae68ce35b7ed5c9f77eed2ccd71f1c4dc33ce58e29d4dd4b71d4da602836dacc7575cfcfd631f4', 'student', 1),
(10, 'kavya.nair@careertrack.edu', 'scrypt:32768:8:1$vrjQRJNp8zTC6wyy$f8aa5411d7a389b5df409f3bc5502d9afe72e6cb6822510d3fae68ce35b7ed5c9f77eed2ccd71f1c4dc33ce58e29d4dd4b71d4da602836dacc7575cfcfd631f4', 'student', 1),
(11, 'vikram.singh@careertrack.edu', 'scrypt:32768:8:1$vrjQRJNp8zTC6wyy$f8aa5411d7a389b5df409f3bc5502d9afe72e6cb6822510d3fae68ce35b7ed5c9f77eed2ccd71f1c4dc33ce58e29d4dd4b71d4da602836dacc7575cfcfd631f4', 'student', 1)
ON DUPLICATE KEY UPDATE email=VALUES(email);

-- ----------------------------------------------------------------------------
-- 3. STUDENTS
-- ----------------------------------------------------------------------------
INSERT INTO students (student_id, user_id, roll_number, first_name, last_name, phone, department_id, graduation_year, cgpa, profile_complete, is_active) VALUES
(1, 6, '1CT22CS001', 'Jahnavi', 'Chittiboyana', '+91 98765 43210', 1, 2026, 8.85, 1, 1),
(2, 7, '1CT22CS002', 'Diya', 'Patel', '+91 98765 43211', 1, 2026, 9.40, 1, 1),
(3, 8, '1CT22IS015', 'Rohan', 'Gupta', '+91 98765 43212', 2, 2026, 7.95, 1, 1),
(4, 9, '1CT22EC030', 'Ananya', 'Reddy', '+91 98765 43213', 3, 2026, 8.45, 1, 1),
(5, 10, '1CT22EE045', 'Kavya', 'Nair', '+91 98765 43214', 4, 2026, 7.30, 1, 1),
(6, 11, '1CT22ME060', 'Vikram', 'Singh', '+91 98765 43215', 5, 2026, 8.10, 1, 1)
ON DUPLICATE KEY UPDATE roll_number=VALUES(roll_number);

-- ----------------------------------------------------------------------------
-- 4. COMPANIES
-- ----------------------------------------------------------------------------
INSERT INTO companies (company_id, name, industry, website, contact_email, contact_phone, description, is_active) VALUES
(1, 'Google India', 'Cloud & Internet Services', 'https://careers.google.com', 'campus-in@google.com', '+91 80 6721 8000', 'Global technology leader specializing in search, cloud computing, and AI innovations.', 1),
(2, 'Microsoft IDC', 'Enterprise Software & Cloud', 'https://careers.microsoft.com', 'university-recruiting@microsoft.com', '+91 40 6696 0000', 'Microsoft India Development Center building world-class platforms including Azure and M365.', 1),
(3, 'Amazon Web Services', 'Cloud Infrastructure & Systems', 'https://amazon.jobs', 'aws-campus-india@amazon.com', '+91 80 4103 2000', 'World leading cloud provider delivering scalable computing infrastructure to millions of customers.', 1),
(4, 'Tata Consultancy Services', 'IT Consulting & Digital Solutions', 'https://www.tcs.com/careers', 'campus.relations@tcs.com', '+91 22 6778 9999', 'Global IT services and consulting enterprise partnering with leading worldwide corporations.', 1),
(5, 'Qualcomm Technologies', 'Semiconductors & Wireless', 'https://www.qualcomm.com/careers', 'campus-india@qualcomm.com', '+91 80 4350 4000', 'World leader in 5G, next-generation wireless technology, SoC design, and edge computing.', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ----------------------------------------------------------------------------
-- 5. RECRUITERS
-- ----------------------------------------------------------------------------
INSERT INTO recruiters (recruiter_id, user_id, company_id, full_name, designation, phone) VALUES
(1, 2, 1, 'Priya Sharma', 'University Talent Lead', '+91 98111 22334'),
(2, 3, 2, 'Vikas Mehta', 'Senior Technical Recruiter', '+91 98222 33445'),
(3, 4, 3, 'Sarah Jenkins', 'Campus Talent Acquisition Manager', '+91 98333 44556'),
(4, 5, 4, 'Arun Patel', 'HR Regional Head - Campus', '+91 98444 55667')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

-- ----------------------------------------------------------------------------
-- 6. SKILLS
-- ----------------------------------------------------------------------------
INSERT INTO skills (skill_id, name, category) VALUES
(1, 'Python', 'Technical'),
(2, 'Java', 'Technical'),
(3, 'C++', 'Technical'),
(4, 'React', 'Frontend'),
(5, 'TypeScript', 'Frontend'),
(6, 'SQL & Relational DBs', 'Database'),
(7, 'Node.js', 'Backend'),
(8, 'Data Structures & Algorithms', 'Core CS'),
(9, 'Cloud Computing (AWS/Azure)', 'DevOps & Cloud'),
(10, 'Docker & Containers', 'DevOps & Cloud'),
(11, 'Embedded Systems', 'Core Hardware'),
(12, 'VLSI Design', 'Core Hardware'),
(13, 'System Design', 'Architecture'),
(14, 'Communication & Leadership', 'Soft Skills')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ----------------------------------------------------------------------------
-- 7. STUDENT_SKILLS
-- ----------------------------------------------------------------------------
INSERT INTO student_skills (student_id, skill_id, proficiency) VALUES
(1, 1, 'Advanced'),     -- Jahnavi: Python
(1, 4, 'Intermediate'), -- Jahnavi: React
(1, 6, 'Advanced'),     -- Jahnavi: SQL
(1, 8, 'Advanced'),     -- Jahnavi: DSA
(2, 2, 'Advanced'),     -- Diya: Java
(2, 3, 'Advanced'),     -- Diya: C++
(2, 8, 'Advanced'),     -- Diya: DSA
(2, 13, 'Intermediate'),-- Diya: System Design
(3, 1, 'Intermediate'), -- Rohan: Python
(3, 4, 'Advanced'),     -- Rohan: React
(3, 5, 'Intermediate'), -- Rohan: TypeScript
(3, 7, 'Advanced'),     -- Rohan: Node.js
(4, 3, 'Advanced'),     -- Ananya: C++
(4, 11, 'Advanced'),    -- Ananya: Embedded Systems
(4, 12, 'Intermediate'),-- Ananya: VLSI Design
(5, 1, 'Beginner'),     -- Kavya: Python
(5, 6, 'Intermediate'), -- Kavya: SQL
(6, 1, 'Intermediate'), -- Vikram: Python
(6, 14, 'Advanced')     -- Vikram: Communication
ON DUPLICATE KEY UPDATE proficiency=VALUES(proficiency);

-- ----------------------------------------------------------------------------
-- 8. OPPORTUNITIES
-- ----------------------------------------------------------------------------
INSERT INTO opportunities (opportunity_id, company_id, title, opportunity_type, description, min_cgpa, graduation_year, location, work_mode, salary_range, opening_date, deadline, status) VALUES
(1, 1, 'Software Engineering Intern (Summer 2026)', 'Internship', 'Join Google engineering teams to design large-scale distributed systems, collaborate on modern developer tooling, and work directly with senior staff engineers.', 8.00, 2026, 'Bengaluru', 'Hybrid', '₹1,25,000 / month', '2026-08-01', '2026-11-30', 'Active'),
(2, 2, 'Associate Software Engineer', 'Full-Time', 'Build cloud-scale web services and distributed microservices inside Microsoft Azure Core Engineering and Microsoft 365 divisions.', 7.50, 2026, 'Hyderabad', 'Hybrid', '₹22,00,000 - ₹26,00,000 LPA', '2026-08-15', '2026-11-20', 'Active'),
(3, 3, 'Cloud Support Associate', 'Full-Time', 'Help enterprise customers deploy, optimize, and troubleshoot cloud infrastructure workloads on Amazon Web Services.', 7.00, 2026, 'Hyderabad', 'On-Site', '₹16,50,000 LPA', '2026-09-01', '2026-12-15', 'Active'),
(4, 4, 'Digital Systems Engineer', 'Full-Time', 'Participate in cutting-edge digital transformation projects across banking, healthcare, retail, and automated systems.', 6.50, 2026, 'Pune', 'On-Site', '₹7,50,000 - ₹9,00,000 LPA', '2026-07-01', '2026-10-31', 'Active'),
(5, 5, 'Embedded Firmware Engineering Intern', 'Internship', 'Design firmware, device drivers, and power-optimization algorithms for high-performance Snapdragon chipsets.', 7.80, 2026, 'Bengaluru', 'On-Site', '₹85,000 / month', '2026-08-10', '2026-11-15', 'Active')
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- ----------------------------------------------------------------------------
-- 9. OPPORTUNITY_DEPARTMENTS (Eligible Branches)
-- ----------------------------------------------------------------------------
INSERT INTO opportunity_departments (opportunity_id, department_id) VALUES
(1, 1), (1, 2),        -- Google: CSE, ISE
(2, 1), (2, 2), (2, 3),-- Microsoft: CSE, ISE, ECE
(3, 1), (3, 2), (3, 3), (3, 4), -- Amazon: CSE, ISE, ECE, EEE
(4, 1), (4, 2), (4, 3), (4, 4), (4, 5), -- TCS: All branches
(5, 3), (5, 4)         -- Qualcomm: ECE, EEE
ON DUPLICATE KEY UPDATE department_id=VALUES(department_id);

-- ----------------------------------------------------------------------------
-- 10. OPPORTUNITY_SKILLS
-- ----------------------------------------------------------------------------
INSERT INTO opportunity_skills (opportunity_id, skill_id, is_mandatory) VALUES
(1, 8, 1),  -- Google: DSA (Mandatory)
(1, 1, 0),  -- Google: Python (Optional)
(1, 3, 0),  -- Google: C++ (Optional)
(2, 2, 1),  -- Microsoft: Java (Mandatory)
(2, 8, 1),  -- Microsoft: DSA (Mandatory)
(2, 13, 0), -- Microsoft: System Design (Optional)
(3, 9, 1),  -- Amazon: Cloud Computing (Mandatory)
(3, 6, 1),  -- Amazon: SQL (Mandatory)
(4, 1, 0),  -- TCS: Python (Optional)
(4, 6, 1),  -- TCS: SQL (Mandatory)
(5, 3, 1),  -- Qualcomm: C++ (Mandatory)
(5, 11, 1)  -- Qualcomm: Embedded Systems (Mandatory)
ON DUPLICATE KEY UPDATE is_mandatory=VALUES(is_mandatory);

-- ----------------------------------------------------------------------------
-- 11. APPLICATIONS
-- ----------------------------------------------------------------------------
INSERT INTO applications (application_id, student_id, opportunity_id, status, student_notes, applied_at) VALUES
(1, 1, 1, 'Interview Scheduled', 'Strong interest in Google Cloud infrastructure teams.', '2026-08-10 10:15:00'),
(2, 2, 1, 'Selected', 'Experienced with distributed systems algorithms and competitive programming.', '2026-08-11 11:30:00'),
(3, 2, 2, 'Shortlisted', 'Completed several microservices projects with Java and Spring.', '2026-08-20 14:00:00'),
(4, 3, 2, 'Under Review', 'Interested in full stack development roles.', '2026-08-25 09:45:00'),
(5, 3, 4, 'Selected', 'Comfortable working across full lifecycle software engineering.', '2026-07-15 16:20:00'),
(6, 4, 5, 'Interview Scheduled', 'Extensive laboratory projects in ARM microcontrollers and embedded C.', '2026-08-15 12:10:00'),
(7, 5, 4, 'Applied', 'Keen to pursue enterprise systems and digital consulting.', '2026-08-28 15:00:00'),
(8, 6, 4, 'Rejected', 'Applying for mechanical systems digital transformation role.', '2026-07-20 11:00:00')
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- ----------------------------------------------------------------------------
-- 12. APPLICATION_STATUS_HISTORY (Lifecycle Audit Log)
-- ----------------------------------------------------------------------------
INSERT INTO application_status_history (history_id, application_id, old_status, new_status, changed_by_user_id, notes, changed_at) VALUES
(1, 1, 'Applied', 'Under Review', 2, 'Initial resume screening passed.', '2026-08-12 14:00:00'),
(2, 1, 'Under Review', 'Shortlisted', 2, 'Technical screening assessment scored in top 5%.', '2026-08-18 10:30:00'),
(3, 1, 'Shortlisted', 'Interview Scheduled', 2, 'Technical Round 1 scheduled.', '2026-08-25 16:00:00'),
(4, 2, 'Applied', 'Under Review', 2, 'Academic credentials verified (CGPA 9.40).', '2026-08-12 15:00:00'),
(5, 2, 'Under Review', 'Shortlisted', 2, 'Shortlisted directly for interview cycles.', '2026-08-15 11:00:00'),
(6, 2, 'Shortlisted', 'Interview Scheduled', 2, 'Interview rounds completed with top score.', '2026-08-20 10:00:00'),
(7, 2, 'Interview Scheduled', 'Selected', 2, 'Offer letter released. Outstanding performance in DSA and systems.', '2026-09-01 17:00:00'),
(8, 6, 'Applied', 'Shortlisted', 2, 'Profile matched embedded systems criteria.', '2026-08-18 11:00:00'),
(9, 6, 'Shortlisted', 'Interview Scheduled', 2, 'Firmware assessment round scheduled.', '2026-08-22 14:30:00'),
(10, 8, 'Applied', 'Rejected', 5, 'Candidate CGPA meets minimum threshold but skills alignment does not match.', '2026-07-28 16:00:00')
ON DUPLICATE KEY UPDATE new_status=VALUES(new_status);

-- ----------------------------------------------------------------------------
-- 13. INTERVIEWS
-- ----------------------------------------------------------------------------
INSERT INTO interviews (interview_id, application_id, round_number, round_name, scheduled_at, mode, meeting_location_or_link, interviewer_name, outcome, feedback) VALUES
(1, 1, 1, 'Technical Round 1: Algorithms & Data Structures', '2026-10-18 14:00:00', 'Video Call', 'https://meet.google.com/ct-eng-001', 'Kunal Sen (Staff SWE)', 'Pending', 'Candidate invited. Topics: Trees, Dynamic Programming, Complexity analysis.'),
(2, 2, 1, 'Technical Round 1: Coding & Problem Solving', '2026-08-22 11:00:00', 'Video Call', 'https://meet.google.com/ct-eng-002', 'Aditi Verma (Senior SWE)', 'Passed', 'Exceptional code clarity, handled edge cases immediately.'),
(3, 2, 2, 'Technical Round 2: System Architecture & Systems', '2026-08-28 15:30:00', 'Video Call', 'https://meet.google.com/ct-eng-003', 'Rajesh K (Principal SWE)', 'Passed', 'Good understanding of concurrency, caching, and database design.'),
(4, 6, 1, 'Hardware & Firmware Deep Dive', '2026-10-20 11:30:00', 'In-Person', 'Qualcomm Campus, Tower 3, Room 402, Bengaluru', 'Siddharth Rao (Principal Hardware Eng)', 'Pending', 'Scheduled. Covers C pointers, interrupt handlers, and I2C/SPI protocols.')
ON DUPLICATE KEY UPDATE round_name=VALUES(round_name);
