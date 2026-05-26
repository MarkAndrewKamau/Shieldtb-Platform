import { StyleSheet, Text, View } from "react-native";

const palette: Record<string, { bg: string; fg: string }> = {
  open: { bg: "#e0f2fe", fg: "#075985" },
  in_progress: { bg: "#dcfce7", fg: "#166534" },
  blocked: { bg: "#fee2e2", fg: "#b91c1c" },
  completed: { bg: "#ecfccb", fg: "#3f6212" },
  cancelled: { bg: "#e2e8f0", fg: "#334155" },
  pending: { bg: "#e0f2fe", fg: "#0c4a6e" },
  screened: { bg: "#dcfce7", fg: "#166534" },
  referred: { bg: "#fef3c7", fg: "#92400e" },
  started_tpt: { bg: "#ede9fe", fg: "#6d28d9" },
  missed_follow_up: { bg: "#fee2e2", fg: "#b91c1c" },
};

type StatusBadgeProps = {
  value: string;
};

export function StatusBadge({ value }: StatusBadgeProps) {
  const colors = palette[value] ?? { bg: "#e2e8f0", fg: "#334155" };

  return (
    <View style={[styles.badge, { backgroundColor: colors.bg }]}>
      <Text style={[styles.text, { color: colors.fg }]}>{formatLabel(value)}</Text>
    </View>
  );
}

function formatLabel(value: string): string {
  return value
    .split("_")
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(" ");
}

const styles = StyleSheet.create({
  badge: {
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 6,
    alignSelf: "flex-start",
  },
  text: {
    fontSize: 12,
    fontWeight: "700",
  },
});
