import type { HouseholdContactStatus } from "@shieldtb/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Redirect, useLocalSearchParams } from "expo-router";
import { MapPinned } from "lucide-react-native";
import { useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { EmptyState } from "../../src/components/EmptyState";
import { LoadingBlock } from "../../src/components/LoadingBlock";
import { ScreenHeader } from "../../src/components/ScreenHeader";
import { StatusBadge } from "../../src/components/StatusBadge";
import { apiClient } from "../../src/lib/api";
import { useAuthStore } from "../../src/stores/auth";

const CONTACT_STATUS_OPTIONS: HouseholdContactStatus[] = [
  "pending",
  "screened",
  "referred",
  "started_tpt",
  "missed_follow_up",
  "completed",
];

export default function HouseholdDetailScreen() {
  const params = useLocalSearchParams<{ id: string }>();
  const queryClient = useQueryClient();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const authorizedCall = useAuthStore((state) => state.authorizedCall);
  const [expandedContactId, setExpandedContactId] = useState<number | null>(null);
  const householdId = Number(params.id);

  const householdQuery = useQuery({
    queryKey: ["household", householdId],
    queryFn: () => authorizedCall((accessToken) => apiClient.getHousehold(householdId, accessToken)),
    enabled: isAuthenticated && Number.isFinite(householdId),
  });

  const updateContactMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: HouseholdContactStatus }) =>
      authorizedCall((accessToken) => apiClient.updateHouseholdContactStatus(id, status, accessToken)),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["household", householdId] });
      void queryClient.invalidateQueries({ queryKey: ["workflow-task"] });
      void queryClient.invalidateQueries({ queryKey: ["workflow-tasks"] });
    },
  });

  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  if (householdQuery.isLoading) {
    return <LoadingBlock label="Loading household..." />;
  }

  if (!householdQuery.data) {
    return (
      <EmptyState
        title="Household unavailable"
        description="This household may no longer be assigned to you."
      />
    );
  }

  const household = householdQuery.data;

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <ScreenHeader
        title={household.index_patient_name}
        subtitle={household.assigned_chw_name || "Household under tracing"}
      />

      <View style={styles.summaryBlock}>
        <View style={styles.locationRow}>
          <View style={styles.mapIcon}>
            <MapPinned color="#0f766e" size={18} />
          </View>
          <View style={styles.locationCopy}>
            <Text style={styles.locationTitle}>Location</Text>
            <Text style={styles.locationText}>
              {[
                household.village,
                household.ward,
                household.sub_county,
                household.county,
              ]
                .filter(Boolean)
                .join(", ") || "Location not yet recorded"}
            </Text>
          </View>
        </View>

        {household.address_description ? (
          <View style={styles.addressBlock}>
            <Text style={styles.sectionLabel}>Directions</Text>
            <Text style={styles.addressText}>{household.address_description}</Text>
          </View>
        ) : null}
      </View>

      <View style={styles.contactsBlock}>
        <Text style={styles.sectionTitle}>Household contacts</Text>
        {household.contacts.length === 0 ? (
          <EmptyState
            title="No contacts recorded"
            description="Contacts added to this household will appear here for CHW follow-up."
          />
        ) : (
          household.contacts.map((contact) => {
            const isExpanded = expandedContactId === contact.id;

            return (
              <View key={contact.id} style={styles.contactRow}>
                <Pressable
                  onPress={() => setExpandedContactId(isExpanded ? null : contact.id)}
                  style={styles.contactSummary}
                >
                  <View style={styles.contactCopy}>
                    <Text style={styles.contactName}>{contact.full_name}</Text>
                    <Text style={styles.contactMeta}>
                      {[contact.relationship_to_index, contact.age_years ? `${contact.age_years} yrs` : null]
                        .filter(Boolean)
                        .join(" • ") || "Relationship not recorded"}
                    </Text>
                    {contact.immunocompromised ? (
                      <Text style={styles.contactFlag}>Immunocompromised</Text>
                    ) : null}
                  </View>
                  <StatusBadge value={contact.status} />
                </Pressable>

                {isExpanded ? (
                  <View style={styles.statusPicker}>
                    {CONTACT_STATUS_OPTIONS.map((status) => {
                      const selected = status === contact.status;
                      return (
                        <Pressable
                          key={status}
                          disabled={updateContactMutation.isPending}
                          onPress={() => updateContactMutation.mutate({ id: contact.id, status })}
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
                ) : null}
              </View>
            );
          })
        )}

        {updateContactMutation.error ? (
          <Text style={styles.errorText}>
            {updateContactMutation.error instanceof Error
              ? updateContactMutation.error.message
              : "Could not update household contact."}
          </Text>
        ) : null}
      </View>
    </ScrollView>
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
  summaryBlock: {
    gap: 14,
    padding: 16,
    borderRadius: 8,
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  locationRow: {
    flexDirection: "row",
    gap: 12,
    alignItems: "center",
  },
  mapIcon: {
    width: 40,
    height: 40,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ecfeff",
  },
  locationCopy: {
    flex: 1,
    gap: 4,
  },
  locationTitle: {
    fontSize: 13,
    fontWeight: "600",
    color: "#64748b",
  },
  locationText: {
    fontSize: 15,
    color: "#0f172a",
  },
  addressBlock: {
    gap: 6,
  },
  sectionLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: "#64748b",
  },
  addressText: {
    fontSize: 15,
    lineHeight: 22,
    color: "#1e293b",
  },
  contactsBlock: {
    gap: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0f172a",
  },
  contactRow: {
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
    overflow: "hidden",
  },
  contactSummary: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
    padding: 16,
  },
  contactCopy: {
    flex: 1,
    gap: 4,
  },
  contactName: {
    fontSize: 15,
    fontWeight: "700",
    color: "#0f172a",
  },
  contactMeta: {
    fontSize: 13,
    color: "#475569",
  },
  contactFlag: {
    fontSize: 13,
    fontWeight: "600",
    color: "#b45309",
  },
  statusPicker: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  statusOption: {
    minWidth: "47%",
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 10,
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
    fontSize: 13,
  },
  statusOptionTextSelected: {
    color: "#0f766e",
  },
  errorText: {
    fontSize: 13,
    color: "#b91c1c",
  },
});
