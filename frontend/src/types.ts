export interface User {
  user_id: number;
  email: string;
  role: 'admin' | 'recruiter' | 'student';
  is_active: boolean;
  created_at: string;
}

export interface StudentProfile {
  email?: string;
  student_id: number;
  roll_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  department_id: number;
  department_name?: string;
  department_code?: string;
  graduation_year: number;
  cgpa: number;
  phone?: string;
  resume_url?: string;
  profile_complete?: boolean;
  is_active: boolean;
  skills: Array<{
    skill_id: number;
    name: string;
    category: string;
    proficiency?: string;
    is_verified?: boolean;
  }>;
}

export interface AuthProfile {
  user_id: number;
  email: string;
  role: 'admin' | 'recruiter' | 'student';
  student?: StudentProfile;
  recruiter?: {
    recruiter_id: number;
    company_id: number;
    first_name: string;
    last_name: string;
    company_name?: string;
    designation?: string;
  };
}

export interface Department {
  department_id: number;
  name: string;
  code: string;
  is_active: boolean;
}

export interface Skill {
  skill_id: number;
  name: string;
  category: string;
}

export interface Company {
  company_id: number;
  name: string;
  industry: string;
  website?: string;
  contact_email: string;
  is_active: boolean;
  created_at?: string;
  opportunities?: Opportunity[];
}

export interface Opportunity {
  opportunity_id: number;
  company_id: number;
  company_name?: string;
  company_industry?: string;
  title: string;
  description: string;
  opportunity_type: 'Full-Time' | 'Internship' | 'Part-Time';
  location: string;
  work_mode: 'On-Site' | 'Hybrid' | 'Remote';
  salary_range?: string;
  min_cgpa: number;
  graduation_year?: number;
  deadline: string;
  max_applications?: number;
  status: 'Draft' | 'Active' | 'Closed' | 'Archived';
  created_at: string;
  eligible_departments?: Array<{ department_id: number; name: string; code: string }>;
  required_skills?: Array<{ skill_id: number; name: string; category: string; is_mandatory: boolean }>;
  is_eligible?: boolean;
  eligibility_reasons?: string[];
  skills_match_score?: number;
  has_applied?: boolean;
  applications_count?: number;
}

export interface ApplicationHistory {
  history_id: number;
  old_status?: string;
  new_status: string;
  changed_at: string;
  notes?: string;
}

export interface Application {
  application_id: number;
  student_id: number;
  opportunity_id: number;
  status: 'Applied' | 'Under Review' | 'Shortlisted' | 'Interview Scheduled' | 'Selected' | 'Rejected' | 'Withdrawn';
  applied_at: string;
  student_notes?: string;
  opportunity?: {
    opportunity_id: number;
    title: string;
    opportunity_type: string;
    company_name: string;
    location: string;
    work_mode: string;
    min_cgpa: number;
  };
  student?: {
    student_id: number;
    roll_number: string;
    first_name: string;
    last_name: string;
    full_name: string;
    department_name: string;
    department_code: string;
    cgpa: number;
    graduation_year: number;
    email: string;
  };
  status_history?: ApplicationHistory[];
  interviews?: Interview[];
}

export interface Interview {
  interview_id: number;
  application_id: number;
  round_name: string;
  scheduled_at: string;
  mode: 'Video Call' | 'In-person' | 'Phone';
  meeting_url?: string;
  meeting_location_or_link?: string;
  location?: string;
  status: 'Scheduled' | 'Completed' | 'Cancelled' | 'Rescheduled';
  feedback?: string;
  student_name?: string;
  student_roll?: string;
  opportunity_title?: string;
  company_name?: string;
}

export interface StudentDashboard {
  profile: StudentProfile;
  total_applications: number;
  status_breakdown: Record<string, number>;
  eligible_opportunities_count: number;
  upcoming_interviews: Interview[];
  recommended_opportunities: Opportunity[];
}

export interface AdminMetrics {
  total_students: number;
  active_students: number;
  placed_students: number;
  placement_rate_percent: number;
  total_companies: number;
  total_opportunities: number;
  active_opportunities: number;
  total_applications: number;
  status_counts: Record<string, number>;
  department_stats: Array<{
    department_id: number;
    code: string;
    name: string;
    total_students: number;
    placed_students: number;
    placement_rate: number;
  }>;
  company_offers: Array<{
    company_name: string;
    offers_count: number;
  }>;
}

export interface SystemStatus {
  status: 'healthy' | 'degraded';
  app: string;
  version: string;
  timestamp: string;
  database: {
    status: string;
    dialect?: string;
    tables_count: number;
    table_counts: Record<string, number>;
    error?: string;
  };
}
