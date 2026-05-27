import { ApiError } from "@shieldtb/api-client";

export function formatLoginError(error: unknown): string {
  if (error instanceof ApiError && error.status === 401) {
    return "The username or password is incorrect.";
  }
  return formatApiError(error, "Could not sign in. Please try again.");
}

export function formatApiError(error: unknown, fallback: string): string {
  if (error instanceof ApiError) {
    if (typeof error.data === "string") {
      return error.data;
    }

    if (error.data && typeof error.data === "object") {
      const entries = Object.entries(error.data as Record<string, unknown>).flatMap(
        ([field, value]) => {
          if (Array.isArray(value)) {
            return value.map((item) => `${humanizeField(field)}: ${String(item)}`);
          }
          return [`${humanizeField(field)}: ${String(value)}`];
        },
      );
      if (entries.length > 0) {
        return entries.join("\n");
      }
    }
  }

  return error instanceof Error ? error.message : fallback;
}

function humanizeField(field: string): string {
  if (field === "non_field_errors") {
    return "Account";
  }
  return field.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}
