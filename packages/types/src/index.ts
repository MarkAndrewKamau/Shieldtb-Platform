export type AuthMode = "cookie" | "token";

export type UserRole =
  | "admin"
  | "clinician"
  | "chw"
  | "facility_officer"
  | "analyst";

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  facility: number | null;
  facility_id: number | null;
  phone: string;
  is_active: boolean;
  must_reset_password: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
  auth_mode?: AuthMode;
}

export interface SignupRequest {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Exclude<UserRole, "admin">;
  facility: number;
  phone: string;
  password: string;
  auth_mode?: AuthMode;
}

export interface RefreshRequest {
  refresh?: string;
  auth_mode?: AuthMode;
}

export interface AuthEnvelope {
  user: User;
  access?: string;
  refresh?: string;
}

export interface FacilitySummary {
  id: number;
  name: string;
  code: string;
  facility_type: string;
  county: string;
  sub_county: string;
  ward: string;
}

export interface RefreshResponse {
  detail: string;
  access?: string;
  refresh?: string;
}

export type PatientSex = "female" | "male" | "intersex" | "unknown";

export interface Patient {
  id: number;
  external_id: string | null;
  given_name: string;
  family_name: string;
  full_name: string;
  date_of_birth: string | null;
  sex: PatientSex;
  phone: string;
  facility: number;
  enrollment_source: string;
  consented_at: string | null;
  consent_recorded_by: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClinicalIntake {
  id: number;
  cough: boolean;
  fever: boolean;
  night_sweats: boolean;
  weight_loss: boolean;
  hiv_positive: boolean;
  pregnant: boolean;
  postpartum: boolean;
  diabetes: boolean;
  sle_or_autoimmune: boolean;
  ckd: boolean;
  on_immunosuppressants: boolean;
  previous_tb: boolean;
  household_tb_contact: boolean;
  crowded_housing: boolean;
  poor_ventilation: boolean;
  medication_history: Record<string, unknown>;
  has_who_tb_symptom: boolean;
  created_at: string;
  updated_at: string;
}

export type RiskTier = "low" | "moderate" | "high" | "critical";

export interface RiskAssessment {
  id: number;
  patient: number;
  patient_name: string;
  encounter: number;
  score: number;
  tier: RiskTier;
  explanation: Record<string, unknown>;
  model_version: string;
  created_at: string;
  updated_at: string;
}

export interface ClinicalEncounter {
  id: number;
  patient: number;
  patient_name: string;
  facility: number;
  encounter_type: string;
  recorded_by: number;
  occurred_at: string;
  notes: string;
  intake?: ClinicalIntake | null;
  risk_assessment?: RiskAssessment | null;
  created_at: string;
  updated_at: string;
}

export type WorkflowTaskStatus =
  | "open"
  | "in_progress"
  | "blocked"
  | "completed"
  | "cancelled";

export type WorkflowTaskType =
  | "household_screening"
  | "patient_follow_up"
  | "postpartum_check_in"
  | "adr_triage"
  | "tpt_eligibility_review";

export interface WorkflowTask {
  id: number;
  task_type: WorkflowTaskType;
  status: WorkflowTaskStatus;
  patient: number | null;
  patient_name: string;
  household: number | null;
  household_id: number | null;
  assigned_to: number | null;
  assigned_to_name: string;
  due_at: string | null;
  completed_at: string | null;
  title: string;
  description: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export type HouseholdContactStatus =
  | "pending"
  | "screened"
  | "referred"
  | "started_tpt"
  | "missed_follow_up"
  | "completed";

export interface HouseholdContact {
  id: number;
  household: number;
  household_id: number;
  patient: number | null;
  patient_name: string;
  full_name: string;
  age_years: number | null;
  phone: string;
  relationship_to_index: string;
  immunocompromised: boolean;
  status: HouseholdContactStatus;
  created_at: string;
  updated_at: string;
}

export interface CreateHouseholdContactRequest {
  household: number;
  patient?: number | null;
  full_name: string;
  age_years?: number | null;
  phone?: string;
  relationship_to_index?: string;
  immunocompromised?: boolean;
  status?: HouseholdContactStatus;
}

export interface Household {
  id: number;
  index_patient: number;
  index_patient_name: string;
  facility: number;
  county: string;
  sub_county: string;
  ward: string;
  village: string;
  address_description: string;
  latitude: string | null;
  longitude: string | null;
  assigned_chw: number | null;
  assigned_chw_name: string;
  contacts: HouseholdContact[];
  created_at: string;
  updated_at: string;
}

export type NotificationStatus = "pending" | "sent" | "delivered" | "failed" | "cancelled";

export interface Notification {
  id: number;
  patient: number | null;
  patient_name: string;
  recipient_user: number | null;
  recipient_user_name: string;
  workflow_task: number | null;
  workflow_task_title: string;
  channel: string;
  status: NotificationStatus;
  recipient: string;
  template_key: string;
  payload: Record<string, unknown>;
  provider_message_id: string;
  failure_reason: string;
  scheduled_for: string | null;
  sent_at: string | null;
  read_at: string | null;
  created_at: string;
  updated_at: string;
}
