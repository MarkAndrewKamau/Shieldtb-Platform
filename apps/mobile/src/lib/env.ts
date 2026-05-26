function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

const defaultBaseUrl = "http://127.0.0.1:8000";

export const API_BASE_URL = stripTrailingSlash(
  process.env.EXPO_PUBLIC_API_BASE_URL || defaultBaseUrl,
);
