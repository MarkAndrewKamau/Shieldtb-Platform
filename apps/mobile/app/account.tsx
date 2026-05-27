import { useQuery } from "@tanstack/react-query";
import { Redirect, useRouter } from "expo-router";
import { Building2, LogOut, UserRound } from "lucide-react-native";
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { LoadingBlock } from "../src/components/LoadingBlock";
import { ScreenHeader } from "../src/components/ScreenHeader";
import { apiClient } from "../src/lib/api";
import { useAuthStore } from "../src/stores/auth";

export default function AccountScreen() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const authorizedCall = useAuthStore((state) => state.authorizedCall);
  const logout = useAuthStore((state) => state.logout);
  const facilityQuery = useQuery({
    queryKey: ["account-facility", user?.facility_id],
    queryFn: () => authorizedCall((accessToken) => apiClient.listFacilities(accessToken)),
    enabled: isAuthenticated && Boolean(user?.facility_id),
  });

  if (!isAuthenticated || !user) {
    return <Redirect href="/login" />;
  }

  const facility = facilityQuery.data?.find((item) => item.id === user.facility_id);
  const displayName =
    [user.first_name, user.last_name].filter(Boolean).join(" ") || user.username;

  const confirmLogout = () => {
    Alert.alert("Sign out?", "You will need to sign in again to access assigned work.", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Sign out",
        style: "destructive",
        onPress: () => {
          void logout().then(() => router.replace("/login"));
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <ScreenHeader title="Account" subtitle="Your ShieldTB staff profile" />

      <View style={styles.identity}>
        <View style={styles.identityIcon}>
          <UserRound color="#0f766e" size={26} />
        </View>
        <View style={styles.identityCopy}>
          <Text style={styles.name}>{displayName}</Text>
          <Text style={styles.username}>@{user.username}</Text>
        </View>
      </View>

      <View style={styles.details}>
        <DetailRow label="Role" value={formatLabel(user.role)} />
        <DetailRow label="Email" value={user.email || "Not recorded"} />
        <DetailRow label="Phone" value={user.phone || "Not recorded"} />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Facility</Text>
        {user.facility_id && facilityQuery.isLoading ? (
          <LoadingBlock label="Loading facility..." />
        ) : facility ? (
          <View style={styles.facility}>
            <View style={styles.facilityIcon}>
              <Building2 color="#0f766e" size={20} />
            </View>
            <View style={styles.facilityCopy}>
              <Text style={styles.facilityName}>{facility.name}</Text>
              <Text style={styles.facilityMeta}>
                {facility.code}
                {facility.county ? `  |  ${facility.county}` : ""}
              </Text>
            </View>
          </View>
        ) : (
          <Text style={styles.muted}>
            {user.facility_id ? "Facility details are unavailable." : "No facility assigned."}
          </Text>
        )}
      </View>

      <Pressable
        accessibilityRole="button"
        onPress={confirmLogout}
        style={({ pressed }) => [styles.signOutButton, pressed ? styles.signOutPressed : null]}
      >
        <LogOut color="#b91c1c" size={18} />
        <Text style={styles.signOutText}>Sign out</Text>
      </Pressable>
    </ScrollView>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.detailRow}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
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
  scroll: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  content: {
    paddingHorizontal: 20,
    paddingVertical: 20,
    gap: 16,
  },
  identity: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  identityIcon: {
    width: 50,
    height: 50,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
    backgroundColor: "#f0fdfa",
  },
  identityCopy: {
    flex: 1,
    gap: 4,
  },
  name: {
    fontSize: 19,
    fontWeight: "700",
    color: "#0f172a",
  },
  username: {
    fontSize: 14,
    color: "#475569",
  },
  details: {
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
    paddingHorizontal: 16,
  },
  detailRow: {
    minHeight: 50,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#f1f5f9",
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
  section: {
    gap: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0f172a",
  },
  facility: {
    minHeight: 70,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    padding: 14,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  facilityIcon: {
    width: 42,
    height: 42,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
    backgroundColor: "#f0fdfa",
  },
  facilityCopy: {
    flex: 1,
    gap: 4,
  },
  facilityName: {
    fontSize: 15,
    fontWeight: "700",
    color: "#0f172a",
  },
  facilityMeta: {
    fontSize: 13,
    color: "#475569",
  },
  muted: {
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    padding: 16,
    fontSize: 14,
    color: "#475569",
    backgroundColor: "#ffffff",
  },
  signOutButton: {
    height: 52,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#fecaca",
    backgroundColor: "#ffffff",
  },
  signOutPressed: {
    backgroundColor: "#fef2f2",
  },
  signOutText: {
    fontSize: 15,
    fontWeight: "600",
    color: "#b91c1c",
  },
});
