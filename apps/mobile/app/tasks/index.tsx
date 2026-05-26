import { useQuery, useQueryClient } from "@tanstack/react-query";
import { router } from "expo-router";
import { LogOut, RefreshCcw } from "lucide-react-native";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { EmptyState } from "../../src/components/EmptyState";
import { LoadingBlock } from "../../src/components/LoadingBlock";
import { ScreenHeader } from "../../src/components/ScreenHeader";
import { TaskCard } from "../../src/components/TaskCard";
import { apiClient } from "../../src/lib/api";
import { useAuthStore } from "../../src/stores/auth";

export default function TaskListScreen() {
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const authorizedCall = useAuthStore((state) => state.authorizedCall);

  const tasksQuery = useQuery({
    queryKey: ["workflow-tasks"],
    queryFn: () => authorizedCall((accessToken) => apiClient.listWorkflowTasks(accessToken)),
  });

  const assignedCount = tasksQuery.data?.length ?? 0;

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={tasksQuery.data ?? []}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.content}
        ListHeaderComponent={
          <View style={styles.headerWrap}>
            <ScreenHeader
              title="My tasks"
              subtitle={
                user
                  ? `${user.first_name || user.username} • ${assignedCount} assigned`
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
                    accessibilityLabel="Log out"
                    onPress={() => {
                      void logout();
                      router.replace("/login");
                    }}
                    style={styles.iconButton}
                  >
                    <LogOut color="#0f172a" size={18} />
                  </Pressable>
                </View>
              }
            />
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
              title="No assigned tasks"
              description="When households or follow-ups are routed to this CHW, they will appear here."
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
    marginBottom: 12,
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
});
