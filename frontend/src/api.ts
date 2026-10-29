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

const BASE_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
  error?: string;
  errors?: string[];
}

function normalizeApplication(row: any): Application {
  return {
    ...row,
    opportunity: row.opportunity ?? {
      opportunity_id: row.opportunity_id,
      title: row.opportunity_title,
      opportunity_type: row.opportunity_type,
      company_name: row.company_name,
    },
    student: row.student ?? (row.student_name ? {
      full_name: row.student_name,
      first_name: row.student_name?.split(' ')[0],
      last_name: row.student_name?.split(' ').slice(1).join(' '),
      roll_number: row.student_roll,
      email: row.student_email,
      cgpa: row.student_cgpa,
      department_code: row.student_department,
    } : undefined),
    status_history: row.status_history ?? row.history,
  } as Application;
}

function normalizeStudent<T extends StudentProfile>(student: T): T {
  return student;
}

function normalizeAuth(profile: AuthProfile): AuthProfile {
  return profile;
}

function normalizeInterview(row: any): Interview {
  return { ...row, status: row.status ?? row.outcome, meeting_url: row.meeting_url ?? row.meeting_location_or_link } as Interview;
}

function normalizeOpportunity(row: any): Opportunity {
  return {
    ...row,
    has_applied: row.has_applied ?? row.already_applied,
    is_eligible: row.is_eligible ?? row.eligibility?.is_eligible,
    eligibility_reasons: row.eligibility_reasons ?? row.ineligibility_reasons ?? row.eligibility?.reasons,
  };
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const config: RequestInit = {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...options.headers,
    },
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, config);
  const data: ApiResponse<T> = await response.json().catch(() => ({
    success: false,
    message: 'Invalid response from server',
    data: null as unknown as T,
  }));

  if (!response.ok || !data.success) {
    const errorMsg = data.error || data.message || `Request failed with status ${response.status}`;
    const err = new Error(errorMsg);
    (err as unknown as { errors?: string[] }).errors = data.errors;
    throw err;
  }

  return data.data;
}

export const api = {
  // Auth
  async getCurrentUser(): Promise<AuthProfile> {
    return normalizeAuth(await request<AuthProfile>('/auth/me'));
  },

  async login(email: string, password: string): Promise<AuthProfile> {
    return normalizeAuth(await request<AuthProfile>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }));
  },

  async logout(): Promise<void> {
    await request<void>('/auth/logout', { method: 'POST' });
  },

  async registerStudent(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    roll_number: string;
    department_id: number;
    graduation_year: number;
    cgpa: number;
    phone: string;
  }): Promise<StudentProfile> {
    return request<StudentProfile>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Opportunities
  async getOpportunities(params: Record<string, string | number | undefined> = {}): Promise<Opportunity[]> {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== '') query.append(key, String(val));
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return (await request<Opportunity[]>(`/opportunities${qs}`)).map(normalizeOpportunity);
  },

  async getOpportunity(id: number): Promise<Opportunity> {
    return request<Opportunity>(`/opportunities/${id}`);
  },

  async createOpportunity(data: {
    title: string;
    description: string;
    opportunity_type: string;
    location: string;
    work_mode: string;
    salary_range?: string;
    min_cgpa: number;
    graduation_year?: number;
    deadline: string;
    opening_date: string;
    department_ids?: number[];
    required_skills?: Array<{ skill_id: number; is_mandatory: boolean }>;
  }): Promise<Opportunity> {
    return request<Opportunity>('/opportunities', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Applications
  async applyOpportunity(opportunity_id: number, student_notes?: string): Promise<Application> {
    return request<Application>('/applications', {
      method: 'POST',
      body: JSON.stringify({ opportunity_id, student_notes }),
    });
  },

  async getMyApplications(): Promise<Application[]> {
    return (await request<Application[]>('/applications/my')).map(normalizeApplication);
  },

  async listApplications(params: Record<string, string | number | undefined> = {}): Promise<Application[]> {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== '') query.append(key, String(val));
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return (await request<Application[]>(`/applications${qs}`)).map(normalizeApplication);
  },

  async updateApplicationStatus(
    application_id: number,
    status: string,
    notes?: string
  ): Promise<Application> {
    return request<Application>(`/applications/${application_id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, notes }),
    });
  },

  async withdrawApplication(application_id: number): Promise<Application> {
    return request<Application>(`/applications/${application_id}/withdraw`, {
      method: 'POST',
    });
  },

  // Interviews
  async getInterviews(application_id?: number): Promise<Interview[]> {
    const qs = application_id ? `?application_id=${application_id}` : '';
    return (await request<Interview[]>(`/interviews${qs}`)).map(normalizeInterview);
  },

  async scheduleInterview(data: {
    application_id: number;
    round_name: string;
    scheduled_at: string;
    mode: string;
    meeting_location_or_link?: string;
    location?: string;
  }): Promise<Interview> {
    return request<Interview>('/interviews', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Admin & Reports
  async getAdminMetrics(): Promise<AdminMetrics> {
    const raw = await request<any>('/admin/metrics');
    const k = raw.kpis ?? raw;
    return {
      ...k,
      total_students: k.total_students ?? 0,
      active_students: k.total_students ?? 0,
      placed_students: k.selected_students ?? 0,
      placement_rate_percent: k.placement_rate ?? 0,
      total_companies: k.total_companies ?? 0,
      total_opportunities: k.total_opportunities ?? k.active_opportunities ?? 0,
      active_opportunities: k.active_opportunities ?? 0,
      total_applications: k.total_applications ?? 0,
      status_counts: Object.fromEntries((raw.status_distribution ?? []).map((item: any) => [item.status, item.count])),
      department_stats: raw.department_stats ?? [],
      company_offers: raw.company_offers ?? [],
    };
  },

  async getStudentDashboard(): Promise<StudentDashboard> {
    const dashboard = await request<StudentDashboard>('/students/dashboard');
    return {
      ...dashboard,
      profile: normalizeStudent(dashboard.profile),
      recommended_opportunities: (dashboard.recommended_opportunities ?? []).map(normalizeOpportunity),
    };
  },

  async getMyProfile(): Promise<StudentProfile> {
    return normalizeStudent(await request<StudentProfile>('/students/profile'));
  },

  async updateMyProfile(data: { first_name?: string; last_name?: string; phone?: string; resume_url?: string }): Promise<StudentProfile> {
    return normalizeStudent(await request<StudentProfile>('/students/profile', { method: 'PUT', body: JSON.stringify(data) }));
  },

  async addSkill(skill_id: number, proficiency: string = 'Intermediate'): Promise<any> {
    return request('/students/skills', {
      method: 'POST',
      body: JSON.stringify({ skill_id, proficiency }),
    });
  },

  async deleteSkill(skill_id: number): Promise<any> {
    return request("/students/skills/" + skill_id, {
      method: 'DELETE',
    });
  },

  // Taxonomies
  async getDepartments(): Promise<Department[]> {
    return request<Department[]>('/departments');
  },

  async getSkills(): Promise<Skill[]> {
    return request<Skill[]>('/skills');
  },

  async getCompanies(): Promise<Company[]> {
    return request<Company[]>('/companies');
  },

  async getStudents(params: Record<string, string | number | undefined> = {}): Promise<StudentProfile[]> {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== '') query.append(key, String(val));
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return (await request<StudentProfile[]>(`/students${qs}`)).map(normalizeStudent);
  },

  // System status
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${BASE_URL}/status`, { credentials: 'include' });
    return res.json();
  },
};
