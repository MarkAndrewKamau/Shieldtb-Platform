import type { WorkflowTaskStatus } from "@shieldtb/types";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Redirect, router } from "expo-router";
import { RefreshCcw, UserRound } from "lucide-react-native";
import { useMemo, useState } from "react";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { EmptyState } from "../../src/components/EmptyState";
import { LoadingBlock } from "../../src/components/LoadingBlock";
import { ScreenHeader } from "../../src/components/ScreenHeader";
import { TaskCard } from "../../src/components/TaskCard";
import { apiClient } from "../../src/lib/api";
import { useAuthStore } from "../../src/stores/auth";

type TaskFilter = "all" | WorkflowTaskStatus;

const TASK_FILTERS: Array<{ value: TaskFilter; label: string }> = [
  { value: "all", label: "All" },
  { value: "open", label: "Open" },
  { value: "in_progress", label: "In progress" },
  { value: "blocked", label: "Blocked" },
  { value: "completed", label: "Done" },
];

export default function TaskListScreen() {
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const authorizedCall = useAuthStore((state) => state.authorizedCall);
  const [filter, setFilter] = useState<TaskFilter>("all");

  const tasksQuery = useQuery({
    queryKey: ["workflow-tasks"],
    queryFn: () => authorizedCall((accessToken) => apiClient.listWorkflowTasks(accessToken)),
    enabled: isAuthenticated,
  });

  const assignedCount = tasksQuery.data?.length ?? 0;
  const filteredTasks = useMemo(() => {
    const tasks = tasksQuery.data ?? [];
    if (filter === "all") {
      return tasks;
    }
    return tasks.filter((task) => task.status === filter);
  }, [filter, tasksQuery.data]);

  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={filteredTasks}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.content}
        ListHeaderComponent={
          <View style={styles.headerWrap}>
            <ScreenHeader
              title="My tasks"
              subtitle={
                user
                  ? `${user.first_name || user.username} | ${filteredTasks.length} of ${assignedCount} shown`
                  : "Assigned household screening and follow-up work"
              }
              actions={
                <View style={styles.actions}>
                  <Pressable
                    accessibilityLabel="Refresh tasks"
                    onPress={() => {
                      void queryClient.invalidateQueries({ queryKey: ["workflow-tasks"] });
                    }}
                    style={styles.iconButton}
                  >
                    <RefreshCcw color="#0f172a" size={18} />
                  </Pressable>
                  <Pressable
                    accessibilityLabel="Open account"
                    onPress={() => {
                      router.push("/account");
                    }}
                    style={styles.iconButton}
                  >
                    <UserRound color="#0f172a" size={18} />
                  </Pressable>
                </View>
              }
            />
            <View style={styles.filterRow}>
              {TASK_FILTERS.map((item) => {
                const selected = filter === item.value;
                return (
                  <Pressable
                    key={item.value}
                    accessibilityRole="button"
                    onPress={() => setFilter(item.value)}
                    style={[styles.filterButton, selected ? styles.filterButtonSelected : null]}
                  >
                    <Text
                      style={[
                        styles.filterButtonText,
                        selected ? styles.filterButtonTextSelected : null,
                      ]}
                    >
                      {item.label}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          </View>
        }
        renderItem={({ item }) => (
          <TaskCard
            task={item}
            onPress={() => {
              router.push(`/tasks/${item.id}`);
            }}
          />
        )}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        ListEmptyComponent={
          tasksQuery.isLoading ? (
            <LoadingBlock label="Loading assigned tasks..." />
          ) : (
            <EmptyState
              title={filter === "all" ? "No assigned tasks" : "No tasks in this status"}
              description={
                filter === "all"
                  ? "When households or follow-ups are routed to this CHW, they will appear here."
                  : "Switch filters to review another part of the queue."
              }
            />
          )
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  content: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 32,
    flexGrow: 1,
  },
  headerWrap: {
    marginBottom: 14,
    gap: 14,
  },
  actions: {
    flexDirection: "row",
    gap: 10,
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
  separator: {
    height: 12,
  },
  filterRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  filterButton: {
    minHeight: 36,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#ffffff",
    justifyContent: "center",
    paddingHorizontal: 12,
  },
  filterButtonSelected: {
    borderColor: "#0f766e",
    backgroundColor: "#f0fdfa",
  },
  filterButtonText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#334155",
  },
  filterButtonTextSelected: {
    color: "#0f766e",
  },
});
