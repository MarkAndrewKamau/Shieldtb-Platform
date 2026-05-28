import type { WorkflowTask } from "@shieldtb/types";
import { ArrowRight, House } from "lucide-react-native";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { StatusBadge } from "./StatusBadge";
import { dueState, formatLabel } from "../lib/format";

type TaskCardProps = {
  task: WorkflowTask;
  onPress: () => void;
};

export function TaskCard({ task, onPress }: TaskCardProps) {
  const due = dueState(task.due_at);

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
        {due ? (
          <Text
            style={[
              styles.meta,
              due.tone === "overdue" ? styles.overdue : null,
              due.tone === "dueSoon" ? styles.dueSoon : null,
            ]}
          >
            {due.label}
          </Text>
        ) : null}
      </View>
    </Pressable>
  );
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
  dueSoon: {
    color: "#92400e",
    fontWeight: "700",
  },
  overdue: {
    color: "#b91c1c",
    fontWeight: "700",
  },
});
