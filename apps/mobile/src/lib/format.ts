export function formatLabel(value: string): string {
  return value
    .split("_")
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(" ");
}

export function formatShortDate(value: string): string {
  return new Intl.DateTimeFormat("en-KE", {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-KE", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function dueState(value: string | null): {
  label: string;
  tone: "default" | "dueSoon" | "overdue";
} | null {
  if (!value) {
    return null;
  }

  const dueAt = new Date(value);
  const now = new Date();
  const diffMs = dueAt.getTime() - now.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  if (diffMs < 0) {
    return { label: `Overdue ${formatShortDate(value)}`, tone: "overdue" };
  }

  if (diffDays <= 1) {
    return { label: "Due today", tone: "dueSoon" };
  }

  if (diffDays <= 3) {
    return { label: `Due in ${diffDays} days`, tone: "dueSoon" };
  }

  return { label: `Due ${formatShortDate(value)}`, tone: "default" };
}

export function compactValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "Not recorded";
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  if (Array.isArray(value)) {
    return value.map(compactValue).join(", ");
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .map(([key, entry]) => `${formatLabel(key)}: ${compactValue(entry)}`)
      .join("; ");
  }
  return String(value);
}
