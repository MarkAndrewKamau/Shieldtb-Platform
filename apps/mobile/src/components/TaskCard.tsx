import type { WorkflowTask } from "@shieldtb/types";
import { ArrowRight, House } from "lucide-react-native";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { StatusBadge } from "./StatusBadge";

type TaskCardProps = {
  task: WorkflowTask;
  onPress: () => void;
};

export function TaskCard({ task, onPress }: TaskCardProps) {
  return (
    <Pressable onPress={onPress} style={styles.card}>
      <View style={styles.header}>
        <View style={styles.iconWrap}>
          <House color="#0f766e" size={18} />
        </View>
        <View style={styles.copy}>
          <Text style={styles.title}>{task.title}</Text>
          <Text style={styles.subtitle}>
            {task.patient_name || "Facility workflow task"} • {formatLabel(task.task_type)}
          </Text>
        </View>
        <ArrowRight color="#64748b" size={18} />
      </View>

      <View style={styles.footer}>
        <StatusBadge value={task.status} />
        {task.due_at ? <Text style={styles.meta}>Due {formatDate(task.due_at)}</Text> : null}
      </View>
    </Pressable>
  );
}

function formatLabel(value: string): string {
  return value
    .split("_")
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(" ");
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-KE", {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
    padding: 16,
    gap: 14,
  },
  header: {
    flexDirection: "row",
    gap: 12,
    alignItems: "center",
  },
  iconWrap: {
    width: 38,
    height: 38,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ecfeff",
  },
  copy: {
    flex: 1,
    gap: 4,
  },
  title: {
    fontSize: 15,
    fontWeight: "700",
    color: "#0f172a",
  },
  subtitle: {
    fontSize: 13,
    lineHeight: 18,
    color: "#475569",
  },
  footer: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
    alignItems: "center",
  },
  meta: {
    fontSize: 12,
    color: "#64748b",
  },
});
