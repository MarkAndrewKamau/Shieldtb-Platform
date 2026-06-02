import type { Notification } from "@shieldtb/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Redirect, useLocalSearchParams, useRouter } from "expo-router";
import { ArrowRight, Bell, Check, House, ListChecks, UserRound } from "lucide-react-native";
import type { ReactNode } from "react";
import { useEffect } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { EmptyState } from "../../src/components/EmptyState";
import { LoadingBlock } from "../../src/components/LoadingBlock";
import { ScreenHeader } from "../../src/components/ScreenHeader";
import { StatusBadge } from "../../src/components/StatusBadge";
import { apiClient } from "../../src/lib/api";
import { compactValue, formatDateTime, formatLabel } from "../../src/lib/format";
import { useAuthStore } from "../../src/stores/auth";

export default function NotificationDetailScreen() {
  const params = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const authorizedCall = useAuthStore((state) => state.authorizedCall);
  const notificationId = Number(params.id);

  const notificationQuery = useQuery({
    queryKey: ["notification", notificationId],
    queryFn: () =>
      authorizedCall((accessToken) => apiClient.getNotification(notificationId, accessToken)),
    enabled: isAuthenticated && Number.isFinite(notificationId),
  });

  const markReadMutation = useMutation({
    mutationFn: () =>
      authorizedCall((accessToken) => apiClient.markNotificationRead(notificationId, accessToken)),
    onSuccess: (notification) => {
      queryClient.setQueryData(["notification", notificationId], notification);
      queryClient.setQueryData<Notification[]>(["notifications"], (items) =>
        items?.map((item) => (item.id === notification.id ? notification : item)),
      );
    },
  });

  useEffect(() => {
    if (notificationQuery.data && !notificationQuery.data.read_at && !markReadMutation.isPending) {
      markReadMutation.mutate();
    }
  }, [markReadMutation, notificationQuery.data]);

  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  if (notificationQuery.isLoading) {
    return <LoadingBlock label="Loading notification..." />;
  }

  if (!notificationQuery.data) {
    return (
      <EmptyState
        title="Notification unavailable"
        description="This notification may no longer be in your inbox."
      />
    );
  }

  const notification = notificationQuery.data;
  const taskId = notification.workflow_task ?? numericPayload(notification.payload, "task_id");
  const householdId = numericPayload(notification.payload, "household_id");
  const patientId = notification.patient ?? numericPayload(notification.payload, "patient_id");

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <ScreenHeader
        title={notificationTitle(notification)}
        subtitle={notificationSubtitle(notification)}
      />

      <View style={styles.summary}>
        <View style={styles.rowBetween}>
          <Text style={styles.label}>Status</Text>
          <StatusBadge value={notification.status} />
        </View>
        <DetailRow label="Channel" value={formatLabel(notification.channel)} />
        <DetailRow label="Created" value={formatDateTime(notification.created_at)} />
        <DetailRow
          label="Read"
          value={notification.read_at ? formatDateTime(notification.read_at) : "Unread"}
        />
        {notification.scheduled_for ? (
          <DetailRow label="Scheduled" value={formatDateTime(notification.scheduled_for)} />
        ) : null}
      </View>

      <View style={styles.actionStack}>
        {taskId ? (
          <ActionRow
            icon={<ListChecks color="#0f766e" size={18} />}
            title="Open task"
            subtitle={notification.workflow_task_title || "Go to linked workflow task"}
            onPress={() => router.push(`/tasks/${taskId}`)}
          />
        ) : null}
        {householdId ? (
          <ActionRow
            icon={<House color="#0f766e" size={18} />}
            title="Open household"
            subtitle="Review contacts and screening status"
            onPress={() => router.push(`/households/${householdId}`)}
          />
        ) : null}
        {patientId ? (
          <ActionRow
            icon={<UserRound color="#0f766e" size={18} />}
            title="Open patient"
            subtitle={notification.patient_name || "Review patient summary"}
            onPress={() =>
              router.push({
                pathname: "/patients/[id]",
                params: {
                  id: String(patientId),
                  ...(householdId ? { householdId: String(householdId) } : {}),
                },
              })
            }
          />
        ) : null}
      </View>

      {isReminder(notification) ? (
        <View style={styles.reminder}>
          <Bell color="#92400e" size={18} />
          <Text style={styles.reminderText}>
            This reminder needs follow-up attention before the task is closed.
          </Text>
        </View>
      ) : null}

      {Object.keys(notification.payload).length > 0 ? (
        <View style={styles.payload}>
          <View style={styles.sectionHeader}>
            <Check color="#0f766e" size={18} />
            <Text style={styles.sectionTitle}>Notification payload</Text>
          </View>
          <Text style={styles.payloadText}>{compactValue(notification.payload)}</Text>
        </View>
      ) : null}
    </ScrollView>
  );
}

function ActionRow({
  icon,
  title,
  subtitle,
  onPress,
}: {
  icon: ReactNode;
  title: string;
  subtitle: string;
  onPress: () => void;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      style={({ pressed }) => [styles.actionRow, pressed ? styles.actionRowPressed : null]}
    >
      <View style={styles.actionIcon}>{icon}</View>
      <View style={styles.actionCopy}>
        <Text style={styles.actionTitle}>{title}</Text>
        <Text style={styles.actionSubtitle}>{subtitle}</Text>
      </View>
      <ArrowRight color="#64748b" size={18} />
    </Pressable>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.rowBetween}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

function notificationTitle(notification: Notification): string {
  if (notification.workflow_task_title) {
    return notification.workflow_task_title;
  }
  return formatLabel(notification.template_key.replace(/\./g, "_"));
}

function notificationSubtitle(notification: Notification): string {
  if (notification.template_key === "workflow_task.assignment") {
    return "New workflow assignment";
  }
  if (isReminder(notification)) {
    return "Follow-up reminder";
  }
  return notification.patient_name || formatLabel(notification.template_key.replace(/\./g, "_"));
}

function isReminder(notification: Notification): boolean {
  const text = `${notification.template_key} ${JSON.stringify(notification.payload)}`.toLowerCase();
  return text.includes("reminder") || text.includes("missed_follow_up");
}

function numericPayload(payload: Record<string, unknown>, key: string): number | null {
  const value = payload[key];
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && /^\d+$/.test(value)) {
    return Number(value);
  }
  return null;
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
  summary: {
    gap: 14,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  rowBetween: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
  },
  label: {
    fontSize: 13,
    fontWeight: "600",
    color: "#64748b",
  },
  value: {
    flex: 1,
    textAlign: "right",
    fontSize: 14,
    color: "#0f172a",
  },
  actionStack: {
    gap: 10,
  },
  actionRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#dbeafe",
    backgroundColor: "#ffffff",
  },
  actionRowPressed: {
    backgroundColor: "#f0fdfa",
  },
  actionIcon: {
    width: 38,
    height: 38,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
    backgroundColor: "#ecfeff",
  },
  actionCopy: {
    flex: 1,
    gap: 4,
  },
  actionTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#0f172a",
  },
  actionSubtitle: {
    fontSize: 13,
    lineHeight: 18,
    color: "#475569",
  },
  reminder: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#fde68a",
    backgroundColor: "#fffbeb",
    padding: 14,
  },
  reminderText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
    color: "#92400e",
  },
  payload: {
    gap: 10,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
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
  payloadText: {
    fontSize: 14,
    lineHeight: 21,
    color: "#1e293b",
  },
});
