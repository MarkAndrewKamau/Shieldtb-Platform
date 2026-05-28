import "react-native-gesture-handler";
import "react-native-reanimated";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import { Shield } from "lucide-react-native";
import { useMemo } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { useBootstrapAuth, useIsAuthHydrated } from "../src/stores/auth";

export default function RootLayout() {
  useBootstrapAuth();
  const isHydrated = useIsAuthHydrated();
  const queryClient = useMemo(() => new QueryClient(), []);

  if (!isHydrated) {
    return (
      <SafeAreaProvider>
        <View style={styles.bootstrap}>
          <View style={styles.brandIcon}>
            <Shield color="#ffffff" size={24} strokeWidth={2.25} />
          </View>
          <Text style={styles.brand}>ShieldTB Mobile</Text>
          <ActivityIndicator size="large" color="#0f766e" />
          <Text style={styles.bootstrapText}>Restoring your account...</Text>
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
          <Stack.Screen name="account" options={{ title: "Account" }} />
          <Stack.Screen name="tasks/index" options={{ title: "My tasks" }} />
          <Stack.Screen name="tasks/[id]" options={{ title: "Task detail" }} />
          <Stack.Screen name="households/[id]" options={{ title: "Household" }} />
          <Stack.Screen name="patients/[id]" options={{ title: "Patient summary" }} />
        </Stack>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  bootstrap: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 14,
    backgroundColor: "#f8fafc",
  },
  brandIcon: {
    width: 48,
    height: 48,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#0f766e",
  },
  brand: {
    marginBottom: 8,
    fontSize: 20,
    fontWeight: "700",
    color: "#0f172a",
  },
  bootstrapText: {
    fontSize: 14,
    color: "#475569",
  },
});
