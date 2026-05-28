import type { WorkflowTaskStatus } from "@shieldtb/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Redirect, useLocalSearchParams, useRouter } from "expo-router";
import { ArrowRight, CalendarClock, FileJson, House, RefreshCcw, UserRound } from "lucide-react-native";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { EmptyState } from "../../src/components/EmptyState";
import { LoadingBlock } from "../../src/components/LoadingBlock";
import { ScreenHeader } from "../../src/components/ScreenHeader";
import { StatusBadge } from "../../src/components/StatusBadge";
import { apiClient } from "../../src/lib/api";
import { compactValue, dueState, formatDateTime, formatLabel } from "../../src/lib/format";
import { useAuthStore } from "../../src/stores/auth";

const TASK_STATUS_OPTIONS: WorkflowTaskStatus[] = [
  "open",
  "in_progress",
  "blocked",
  "completed",
  "cancelled",
];

export default function TaskDetailScreen() {
  const params = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const authorizedCall = useAuthStore((state) => state.authorizedCall);
  const taskId = Number(params.id);

  const taskQuery = useQuery({
    queryKey: ["workflow-task", taskId],
    queryFn: () => authorizedCall((accessToken) => apiClient.getWorkflowTask(taskId, accessToken)),
    enabled: isAuthenticated && Number.isFinite(taskId),
  });

  const updateStatusMutation = useMutation({
    mutationFn: (status: WorkflowTaskStatus) =>
      authorizedCall((accessToken) =>
        apiClient.updateWorkflowTaskStatus(taskId, status, accessToken),
      ),
    onSuccess: (task) => {
      void queryClient.setQueryData(["workflow-task", taskId], task);
      void queryClient.invalidateQueries({ queryKey: ["workflow-tasks"] });
    },
  });

  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  if (taskQuery.isLoading) {
    return <LoadingBlock label="Loading task detail..." />;
  }

  if (!taskQuery.data) {
    return (
      <EmptyState
        title="Task not found"
        description="This task may have been reassigned or removed from your queue."
      />
    );
  }

  const task = taskQuery.data;
  const due = dueState(task.due_at);
  const metadataEntries = Object.entries(task.metadata ?? {}).filter(([, value]) => {
    if (value === null || value === undefined || value === "") {
      return false;
    }
    if (Array.isArray(value)) {
      return value.length > 0;
    }
    if (typeof value === "object") {
      return Object.keys(value as Record<string, unknown>).length > 0;
    }
    return true;
  });

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <ScreenHeader
        title={task.title}
        subtitle={task.assigned_to_name || "Assigned workflow task"}
        actions={
          <Pressable
            accessibilityLabel="Refresh task"
            onPress={() => {
              void taskQuery.refetch();
            }}
            style={styles.iconButton}
          >
            <RefreshCcw color="#0f172a" size={18} />
          </Pressable>
        }
      />

      <View style={styles.summaryBlock}>
        <View style={styles.rowBetween}>
          <Text style={styles.label}>Status</Text>
          <StatusBadge value={task.status} />
        </View>
        <View style={styles.rowBetween}>
          <Text style={styles.label}>Task type</Text>
          <Text style={styles.value}>{formatLabel(task.task_type)}</Text>
        </View>
        {task.patient_name ? (
          <View style={styles.rowBetween}>
            <Text style={styles.label}>Index patient</Text>
            <Text style={styles.value}>{task.patient_name}</Text>
          </View>
        ) : null}
        {task.due_at ? (
          <View style={styles.rowBetween}>
            <Text style={styles.label}>Due</Text>
            <Text
              style={[
                styles.value,
                due?.tone === "overdue" ? styles.overdue : null,
                due?.tone === "dueSoon" ? styles.dueSoon : null,
              ]}
            >
              {due?.label ?? formatDateTime(task.due_at)}
            </Text>
          </View>
        ) : null}
        {task.completed_at ? (
          <View style={styles.rowBetween}>
            <Text style={styles.label}>Completed</Text>
            <Text style={styles.value}>{formatDateTime(task.completed_at)}</Text>
          </View>
        ) : null}
        {task.description ? (
          <View style={styles.notesBlock}>
            <Text style={styles.label}>Notes</Text>
            <Text style={styles.notes}>{task.description}</Text>
          </View>
        ) : null}
      </View>

      {task.patient ? (
        <Pressable
          onPress={() =>
            router.push({
              pathname: "/patients/[id]",
              params: {
                id: String(task.patient),
                ...(task.household_id ? { householdId: String(task.household_id) } : {}),
              },
            })
          }
          style={styles.linkRow}
        >
          <View style={styles.linkIcon}>
            <UserRound color="#0f766e" size={18} />
          </View>
          <View style={styles.linkCopy}>
            <Text style={styles.linkTitle}>Open patient summary</Text>
            <Text style={styles.linkSubtitle}>Review risk, clinical context, and household link.</Text>
          </View>
          <ArrowRight color="#64748b" size={18} />
        </Pressable>
      ) : null}

      {task.household_id ? (
        <Pressable
          onPress={() => router.push(`/households/${task.household_id}`)}
          style={styles.linkRow}
        >
          <View style={styles.linkIcon}>
            <House color="#0f766e" size={18} />
          </View>
          <View style={styles.linkCopy}>
            <Text style={styles.linkTitle}>Open household</Text>
            <Text style={styles.linkSubtitle}>Review contacts and update screening state.</Text>
          </View>
          <ArrowRight color="#64748b" size={18} />
        </Pressable>
      ) : null}

      {metadataEntries.length > 0 ? (
        <View style={styles.metadataBlock}>
          <View style={styles.sectionHeader}>
            <FileJson color="#0f766e" size={18} />
            <Text style={styles.sectionTitle}>Task metadata</Text>
          </View>
          {metadataEntries.map(([key, value]) => (
            <View key={key} style={styles.rowBetween}>
              <Text style={styles.label}>{formatLabel(key)}</Text>
              <Text style={styles.value}>{compactValue(value)}</Text>
            </View>
          ))}
        </View>
      ) : null}

      <View style={styles.statusBlock}>
        <View style={styles.sectionHeader}>
          <CalendarClock color="#0f766e" size={18} />
          <Text style={styles.sectionTitle}>Update task status</Text>
        </View>
        <View style={styles.statusGrid}>
          {TASK_STATUS_OPTIONS.map((status) => {
            const selected = status === task.status;
            return (
              <Pressable
                key={status}
                disabled={updateStatusMutation.isPending}
                onPress={() => updateStatusMutation.mutate(status)}
                style={[
                  styles.statusOption,
                  selected ? styles.statusOptionSelected : null,
                ]}
              >
                <Text
                  style={[
                    styles.statusOptionText,
                    selected ? styles.statusOptionTextSelected : null,
                  ]}
                >
                  {formatLabel(status)}
                </Text>
              </Pressable>
            );
          })}
        </View>
        {updateStatusMutation.error ? (
          <Text style={styles.errorText}>
            {updateStatusMutation.error instanceof Error
              ? updateStatusMutation.error.message
              : "Could not update task status."}
          </Text>
        ) : null}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  content: {
    paddingHorizontal: 20,
    paddingVertical: 20,
    gap: 16,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#ffffff",
  },
  summaryBlock: {
    gap: 14,
    padding: 16,
    borderRadius: 8,
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  rowBetween: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
    alignItems: "center",
  },
  label: {
    fontSize: 13,
    fontWeight: "600",
    color: "#64748b",
  },
  value: {
    flexShrink: 1,
    textAlign: "right",
    fontSize: 15,
    color: "#0f172a",
  },
  dueSoon: {
    color: "#92400e",
    fontWeight: "700",
  },
  overdue: {
    color: "#b91c1c",
    fontWeight: "700",
  },
  notesBlock: {
    gap: 8,
  },
  notes: {
    fontSize: 15,
    lineHeight: 22,
    color: "#1e293b",
  },
  linkRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    padding: 16,
    borderRadius: 8,
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#dbeafe",
  },
  linkIcon: {
    width: 38,
    height: 38,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ecfeff",
  },
  linkCopy: {
    flex: 1,
    gap: 4,
  },
  linkTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#0f172a",
  },
  linkSubtitle: {
    fontSize: 13,
    lineHeight: 18,
    color: "#475569",
  },
  statusBlock: {
    gap: 12,
  },
  metadataBlock: {
    gap: 12,
    padding: 16,
    borderRadius: 8,
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0f172a",
  },
  statusGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  statusOption: {
    minWidth: "47%",
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#ffffff",
  },
  statusOptionSelected: {
    borderColor: "#0f766e",
    backgroundColor: "#f0fdfa",
  },
  statusOptionText: {
    textAlign: "center",
    fontWeight: "600",
    color: "#0f172a",
  },
  statusOptionTextSelected: {
    color: "#0f766e",
  },
  errorText: {
    fontSize: 13,
    color: "#b91c1c",
  },
});
