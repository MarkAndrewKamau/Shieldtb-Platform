import type {
  AuthEnvelope,
  ClinicalEncounter,
  FacilitySummary,
  Household,
  HouseholdContact,
  HouseholdContactStatus,
  LoginRequest,
  Notification,
  Patient,
  RefreshRequest,
  RefreshResponse,
  RiskAssessment,
  SignupRequest,
  User,
  CreateHouseholdContactRequest,
  WorkflowTask,
  WorkflowTaskStatus,
} from "@shieldtb/types";

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

type JsonPrimitive = string | number | boolean | null;
type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
type JsonBody = Record<string, JsonValue>;

interface RequestOptions {
  method?: "GET" | "POST" | "PATCH";
  body?: JsonBody;
  accessToken?: string;
}

function trimSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

export class ShieldTBApiClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = trimSlash(baseUrl);
  }

  async login(payload: LoginRequest): Promise<AuthEnvelope> {
    return this.request<AuthEnvelope>("/api/v1/auth/login/", {
      method: "POST",
      body: { ...payload, auth_mode: payload.auth_mode ?? "token" },
    });
  }

  async signup(payload: SignupRequest): Promise<AuthEnvelope> {
    return this.request<AuthEnvelope>("/api/v1/auth/signup/", {
      method: "POST",
      body: { ...payload, auth_mode: payload.auth_mode ?? "token" },
    });
  }

  async searchSignupFacilities(query: string): Promise<FacilitySummary[]> {
    return this.request<FacilitySummary[]>(
      `/api/v1/auth/signup/facilities/?q=${encodeURIComponent(query)}`,
    );
  }

  async refresh(payload: RefreshRequest): Promise<RefreshResponse> {
    return this.request<RefreshResponse>("/api/v1/auth/refresh/", {
      method: "POST",
      body: { ...payload, auth_mode: payload.auth_mode ?? "token" },
    });
  }

  async logout(refresh: string | undefined, accessToken: string): Promise<{ detail: string }> {
    return this.request<{ detail: string }>("/api/v1/auth/logout/", {
      method: "POST",
      accessToken,
      body: refresh ? { refresh } : {},
    });
  }

  async me(accessToken: string): Promise<User> {
    return this.request<User>("/api/v1/auth/me/", { accessToken });
  }

  async listFacilities(accessToken: string): Promise<FacilitySummary[]> {
    return this.request<FacilitySummary[]>("/api/v1/facilities/", { accessToken });
  }

  async getPatient(id: number, accessToken: string): Promise<Patient> {
    return this.request<Patient>(`/api/v1/patients/${id}/`, { accessToken });
  }

  async listClinicalEncounters(
    accessToken: string,
    filters: { patient?: number } = {},
  ): Promise<ClinicalEncounter[]> {
    return this.request<ClinicalEncounter[]>(
      `/api/v1/clinical/encounters/${queryString(filters)}`,
      { accessToken },
    );
  }

  async listRiskAssessments(
    accessToken: string,
    filters: { patient?: number } = {},
  ): Promise<RiskAssessment[]> {
    return this.request<RiskAssessment[]>(
      `/api/v1/risk-assessments/${queryString(filters)}`,
      { accessToken },
    );
  }

  async listWorkflowTasks(accessToken: string): Promise<WorkflowTask[]> {
    return this.request<WorkflowTask[]>("/api/v1/workflow-tasks/", { accessToken });
  }

  async getWorkflowTask(id: number, accessToken: string): Promise<WorkflowTask> {
    return this.request<WorkflowTask>(`/api/v1/workflow-tasks/${id}/`, { accessToken });
  }

  async updateWorkflowTaskStatus(
    id: number,
    status: WorkflowTaskStatus,
    accessToken: string,
  ): Promise<WorkflowTask> {
    return this.request<WorkflowTask>(`/api/v1/workflow-tasks/${id}/update_status/`, {
      method: "POST",
      accessToken,
      body: { status },
    });
  }

  async getHousehold(id: number, accessToken: string): Promise<Household> {
    return this.request<Household>(`/api/v1/households/${id}/`, { accessToken });
  }

  async createHouseholdContact(
    payload: CreateHouseholdContactRequest,
    accessToken: string,
  ): Promise<HouseholdContact> {
    return this.request<HouseholdContact>("/api/v1/household-contacts/", {
      method: "POST",
      accessToken,
      body: {
        household: payload.household,
        patient: payload.patient ?? null,
        full_name: payload.full_name,
        age_years: payload.age_years ?? null,
        phone: payload.phone ?? "",
        relationship_to_index: payload.relationship_to_index ?? "",
        immunocompromised: payload.immunocompromised ?? false,
        status: payload.status ?? "pending",
      },
    });
  }

  async updateHouseholdContactStatus(
    id: number,
    status: HouseholdContactStatus,
    accessToken: string,
  ): Promise<HouseholdContact> {
    return this.request<HouseholdContact>(`/api/v1/household-contacts/${id}/`, {
      method: "PATCH",
      accessToken,
      body: { status },
    });
  }

  async listNotifications(accessToken: string): Promise<Notification[]> {
    return this.request<Notification[]>("/api/v1/notifications/", { accessToken });
  }

  private async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const headers: Record<string, string> = {
      Accept: "application/json",
    };

    if (options.body) {
      headers["Content-Type"] = "application/json";
    }

    if (options.accessToken) {
      headers.Authorization = `Bearer ${options.accessToken}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    const rawText = await response.text();
    const data = rawText ? tryParseJson(rawText) : null;

    if (!response.ok) {
      throw new ApiError(
        typeof data === "object" && data && "detail" in data
          ? String((data as { detail?: unknown }).detail ?? "Request failed.")
          : `Request failed with status ${response.status}.`,
        response.status,
        data,
      );
    }

    return data as T;
  }
}

function queryString(filters: Record<string, string | number | undefined>): string {
  const params = Object.entries(filters).filter((entry): entry is [string, string | number] =>
    entry[1] !== undefined,
  );
  if (params.length === 0) {
    return "";
  }
  const search = params
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join("&");
  return `?${search}`;
}

function tryParseJson(rawText: string): unknown {
  try {
    return JSON.parse(rawText);
  } catch {
    return rawText;
  }
}
