import "react-native-gesture-handler";
import "react-native-reanimated";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import { useMemo } from "react";
import { ActivityIndicator, View } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { useBootstrapAuth, useIsAuthHydrated } from "../src/stores/auth";

export default function RootLayout() {
  useBootstrapAuth();
  const isHydrated = useIsAuthHydrated();
  const queryClient = useMemo(() => new QueryClient(), []);

  if (!isHydrated) {
    return (
      <SafeAreaProvider>
        <View
          style={{
            flex: 1,
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "#f8fafc",
          }}
        >
          <ActivityIndicator size="large" color="#0f766e" />
        </View>
      </SafeAreaProvider>
    );
  }

  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <Stack
          screenOptions={{
            headerShadowVisible: false,
            headerStyle: { backgroundColor: "#ffffff" },
            headerTintColor: "#0f172a",
            contentStyle: { backgroundColor: "#f8fafc" },
          }}
        >
          <Stack.Screen name="index" options={{ headerShown: false }} />
          <Stack.Screen name="login" options={{ headerShown: false }} />
          <Stack.Screen name="signup" options={{ headerShown: false }} />
          <Stack.Screen name="tasks/index" options={{ title: "My tasks" }} />
          <Stack.Screen name="tasks/[id]" options={{ title: "Task detail" }} />
          <Stack.Screen name="households/[id]" options={{ title: "Household" }} />
        </Stack>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
