import type {
  AuthEnvelope,
  FacilitySummary,
  Household,
  HouseholdContact,
  HouseholdContactStatus,
  LoginRequest,
  Notification,
  RefreshRequest,
  RefreshResponse,
  SignupRequest,
  User,
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

function tryParseJson(rawText: string): unknown {
  try {
    return JSON.parse(rawText);
  } catch {
    return rawText;
  }
}
