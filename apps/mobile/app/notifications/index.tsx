import type { Notification } from "@shieldtb/types";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Redirect, router } from "expo-router";
import { Bell, RefreshCcw } from "lucide-react-native";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { EmptyState } from "../../src/components/EmptyState";
import { LoadingBlock } from "../../src/components/LoadingBlock";
import { ScreenHeader } from "../../src/components/ScreenHeader";
import { StatusBadge } from "../../src/components/StatusBadge";
import { apiClient } from "../../src/lib/api";
import { formatDateTime, formatLabel } from "../../src/lib/format";
import { useAuthStore } from "../../src/stores/auth";

export default function NotificationInboxScreen() {
  const queryClient = useQueryClient();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const authorizedCall = useAuthStore((state) => state.authorizedCall);

  const notificationsQuery = useQuery({
    queryKey: ["notifications"],
    queryFn: () => authorizedCall((accessToken) => apiClient.listNotifications(accessToken)),
    enabled: isAuthenticated,
  });

  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  const unreadCount = notificationsQuery.data?.filter((item) => !item.read_at).length ?? 0;

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={notificationsQuery.data ?? []}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.content}
        ListHeaderComponent={
          <View style={styles.headerWrap}>
            <ScreenHeader
              title="Inbox"
              subtitle={`${unreadCount} unread notifications`}
              actions={
                <Pressable
                  accessibilityLabel="Refresh inbox"
                  onPress={() => {
                    void queryClient.invalidateQueries({ queryKey: ["notifications"] });
                  }}
                  style={styles.iconButton}
                >
                  <RefreshCcw color="#0f172a" size={18} />
                </Pressable>
              }
            />
          </View>
        }
        renderItem={({ item }) => (
          <NotificationRow
            notification={item}
            onPress={() => {
              router.push(`/notifications/${item.id}`);
            }}
          />
        )}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        ListEmptyComponent={
          notificationsQuery.isLoading ? (
            <LoadingBlock label="Loading notifications..." />
          ) : (
            <EmptyState
              title="No notifications"
              description="New assignments and reminders will appear here."
            />
          )
        }
      />
    </SafeAreaView>
  );
}

function NotificationRow({
  notification,
  onPress,
}: {
  notification: Notification;
  onPress: () => void;
}) {
  const unread = !notification.read_at;

  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      style={({ pressed }) => [
        styles.row,
        unread ? styles.rowUnread : null,
        pressed ? styles.rowPressed : null,
      ]}
    >
      <View style={styles.rowIcon}>
        <Bell color={unread ? "#0f766e" : "#64748b"} size={18} />
      </View>
      <View style={styles.rowCopy}>
        <View style={styles.rowTitleLine}>
          <Text style={styles.rowTitle}>{notificationTitle(notification)}</Text>
          {unread ? <View style={styles.unreadDot} /> : null}
        </View>
        <Text style={styles.rowSubtitle}>{notificationSubtitle(notification)}</Text>
        <View style={styles.rowMeta}>
          <StatusBadge value={notification.status} />
          <Text style={styles.rowTime}>{formatDateTime(notification.created_at)}</Text>
        </View>
      </View>
    </Pressable>
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
  if (notification.patient_name) {
    return notification.patient_name;
  }
  return formatLabel(notification.channel);
}

function isReminder(notification: Notification): boolean {
  const text = `${notification.template_key} ${JSON.stringify(notification.payload)}`.toLowerCase();
  return text.includes("reminder") || text.includes("missed_follow_up");
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  content: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 32,
  },
  headerWrap: {
    marginBottom: 12,
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
  row: {
    flexDirection: "row",
    gap: 12,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  rowUnread: {
    borderColor: "#99f6e4",
    backgroundColor: "#f0fdfa",
  },
  rowPressed: {
    opacity: 0.9,
  },
  rowIcon: {
    width: 38,
    height: 38,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
    backgroundColor: "#ecfeff",
  },
  rowCopy: {
    flex: 1,
    gap: 6,
  },
  rowTitleLine: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  rowTitle: {
    flex: 1,
    fontSize: 15,
    fontWeight: "700",
    color: "#0f172a",
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 999,
    backgroundColor: "#0f766e",
  },
  rowSubtitle: {
    fontSize: 13,
    lineHeight: 18,
    color: "#475569",
  },
  rowMeta: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
  },
  rowTime: {
    flexShrink: 1,
    textAlign: "right",
    fontSize: 12,
    color: "#64748b",
  },
  separator: {
    height: 12,
  },
});
