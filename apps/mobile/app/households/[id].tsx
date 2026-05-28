import type { HouseholdContactStatus } from "@shieldtb/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Redirect, useLocalSearchParams, useRouter } from "expo-router";
import { Check, MapPinned, Navigation, Phone, Plus, UserRound, X } from "lucide-react-native";
import { useState } from "react";
import { Linking, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

import { EmptyState } from "../../src/components/EmptyState";
import { LoadingBlock } from "../../src/components/LoadingBlock";
import { ScreenHeader } from "../../src/components/ScreenHeader";
import { StatusBadge } from "../../src/components/StatusBadge";
import { apiClient } from "../../src/lib/api";
import { formatLabel } from "../../src/lib/format";
import { useAuthStore } from "../../src/stores/auth";

const CONTACT_STATUS_OPTIONS: HouseholdContactStatus[] = [
  "pending",
  "screened",
  "referred",
  "started_tpt",
  "missed_follow_up",
  "completed",
];

type ContactForm = {
  fullName: string;
  ageYears: string;
  phone: string;
  relationship: string;
  immunocompromised: boolean;
};

const EMPTY_CONTACT_FORM: ContactForm = {
  fullName: "",
  ageYears: "",
  phone: "",
  relationship: "",
  immunocompromised: false,
};

export default function HouseholdDetailScreen() {
  const params = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const authorizedCall = useAuthStore((state) => state.authorizedCall);
  const [expandedContactId, setExpandedContactId] = useState<number | null>(null);
  const [isAddingContact, setIsAddingContact] = useState(false);
  const [contactForm, setContactForm] = useState<ContactForm>(EMPTY_CONTACT_FORM);
  const [contactFormError, setContactFormError] = useState<string | null>(null);
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

  const createContactMutation = useMutation({
    mutationFn: () => {
      const ageYears = contactForm.ageYears.trim();
      return authorizedCall((accessToken) =>
        apiClient.createHouseholdContact(
          {
            household: householdId,
            full_name: contactForm.fullName.trim(),
            age_years: ageYears ? Number(ageYears) : null,
            phone: contactForm.phone.trim(),
            relationship_to_index: contactForm.relationship.trim(),
            immunocompromised: contactForm.immunocompromised,
            status: "pending",
          },
          accessToken,
        ),
      );
    },
    onSuccess: () => {
      setContactForm(EMPTY_CONTACT_FORM);
      setContactFormError(null);
      setIsAddingContact(false);
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
  const progress = screeningProgress(household.contacts);
  const canOpenMap = Boolean(household.latitude && household.longitude);

  const submitContact = () => {
    const fullName = contactForm.fullName.trim();
    if (!fullName) {
      setContactFormError("Full name is required.");
      return;
    }
    if (contactForm.ageYears.trim() && !/^\d+$/.test(contactForm.ageYears.trim())) {
      setContactFormError("Age must be a whole number.");
      return;
    }
    setContactFormError(null);
    createContactMutation.mutate();
  };

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <ScreenHeader
        title={household.index_patient_name}
        subtitle={household.assigned_chw_name || "Household under tracing"}
      />

      <View style={styles.summaryBlock}>
        <View style={styles.progressBlock}>
          <View style={styles.rowBetween}>
            <Text style={styles.sectionLabel}>Screening progress</Text>
            <Text style={styles.progressCount}>
              {progress.complete} / {progress.total} complete
            </Text>
          </View>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${progress.percent}%` }]} />
          </View>
          <Text style={styles.progressText}>{progress.label}</Text>
        </View>

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

        <View style={styles.actionGrid}>
          {household.index_patient ? (
            <Pressable
              accessibilityRole="button"
              onPress={() =>
                router.push({
                  pathname: "/patients/[id]",
                  params: { id: String(household.index_patient), householdId: String(household.id) },
                })
              }
              style={({ pressed }) => [styles.actionButton, pressed ? styles.actionPressed : null]}
            >
              <UserRound color="#0f766e" size={18} />
              <Text style={styles.actionText}>Patient</Text>
            </Pressable>
          ) : null}
          {canOpenMap ? (
            <Pressable
              accessibilityRole="button"
              onPress={() =>
                Linking.openURL(`geo:${household.latitude},${household.longitude}`)
              }
              style={({ pressed }) => [styles.actionButton, pressed ? styles.actionPressed : null]}
            >
              <Navigation color="#0f766e" size={18} />
              <Text style={styles.actionText}>Map</Text>
            </Pressable>
          ) : null}
        </View>
      </View>

      <View style={styles.contactsBlock}>
        <View style={styles.contactsHeader}>
          <Text style={styles.sectionTitle}>Household contacts</Text>
          <Pressable
            accessibilityRole="button"
            onPress={() => {
              setIsAddingContact((value) => !value);
              setContactFormError(null);
            }}
            style={({ pressed }) => [styles.addButton, pressed ? styles.addButtonPressed : null]}
          >
            {isAddingContact ? <X color="#0f172a" size={16} /> : <Plus color="#0f172a" size={16} />}
            <Text style={styles.addButtonText}>{isAddingContact ? "Cancel" : "Add"}</Text>
          </Pressable>
        </View>

        {isAddingContact ? (
          <View style={styles.addContactBlock}>
            <TextInput
              autoCapitalize="words"
              onChangeText={(value) => setContactForm((form) => ({ ...form, fullName: value }))}
              placeholder="Full name"
              placeholderTextColor="#94a3b8"
              style={styles.input}
              value={contactForm.fullName}
            />
            <View style={styles.formRow}>
              <TextInput
                keyboardType="number-pad"
                onChangeText={(value) => setContactForm((form) => ({ ...form, ageYears: value }))}
                placeholder="Age"
                placeholderTextColor="#94a3b8"
                style={[styles.input, styles.inputHalf]}
                value={contactForm.ageYears}
              />
              <TextInput
                keyboardType="phone-pad"
                onChangeText={(value) => setContactForm((form) => ({ ...form, phone: value }))}
                placeholder="Phone"
                placeholderTextColor="#94a3b8"
                style={[styles.input, styles.inputHalf]}
                value={contactForm.phone}
              />
            </View>
            <TextInput
              autoCapitalize="words"
              onChangeText={(value) => setContactForm((form) => ({ ...form, relationship: value }))}
              placeholder="Relationship to index patient"
              placeholderTextColor="#94a3b8"
              style={styles.input}
              value={contactForm.relationship}
            />
            <Pressable
              accessibilityRole="checkbox"
              accessibilityState={{ checked: contactForm.immunocompromised }}
              onPress={() =>
                setContactForm((form) => ({
                  ...form,
                  immunocompromised: !form.immunocompromised,
                }))
              }
              style={styles.checkboxRow}
            >
              <View
                style={[
                  styles.checkbox,
                  contactForm.immunocompromised ? styles.checkboxChecked : null,
                ]}
              >
                {contactForm.immunocompromised ? <Check color="#ffffff" size={14} /> : null}
              </View>
              <Text style={styles.checkboxText}>Immunocompromised</Text>
            </Pressable>

            {contactFormError || createContactMutation.error ? (
              <Text style={styles.errorText}>
                {contactFormError ??
                  (createContactMutation.error instanceof Error
                    ? createContactMutation.error.message
                    : "Could not add household contact.")}
              </Text>
            ) : null}

            <Pressable
              accessibilityRole="button"
              disabled={createContactMutation.isPending}
              onPress={submitContact}
              style={[
                styles.submitButton,
                createContactMutation.isPending ? styles.submitButtonDisabled : null,
              ]}
            >
              <Text style={styles.submitButtonText}>
                {createContactMutation.isPending ? "Adding..." : "Add contact"}
              </Text>
            </Pressable>
          </View>
        ) : null}

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
                    {contact.phone ? <Text style={styles.contactMeta}>{contact.phone}</Text> : null}
                  </View>
                  <StatusBadge value={contact.status} />
                </Pressable>

                {isExpanded ? (
                  <View style={styles.contactDetail}>
                    <View style={styles.contactActions}>
                      {contact.phone ? (
                        <Pressable
                          accessibilityRole="button"
                          onPress={() => Linking.openURL(`tel:${contact.phone}`)}
                          style={styles.smallAction}
                        >
                          <Phone color="#0f766e" size={16} />
                          <Text style={styles.smallActionText}>Call</Text>
                        </Pressable>
                      ) : null}
                      {contact.patient ? (
                        <Pressable
                          accessibilityRole="button"
                          onPress={() =>
                            router.push({
                              pathname: "/patients/[id]",
                              params: {
                                id: String(contact.patient),
                                householdId: String(household.id),
                              },
                            })
                          }
                          style={styles.smallAction}
                        >
                          <UserRound color="#0f766e" size={16} />
                          <Text style={styles.smallActionText}>Patient</Text>
                        </Pressable>
                      ) : null}
                    </View>

                    <Text style={styles.statusHelp}>Screening state</Text>
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

function screeningProgress(contacts: Array<{ status: HouseholdContactStatus }>): {
  complete: number;
  total: number;
  percent: number;
  label: string;
} {
  const total = contacts.length;
  const complete = contacts.filter((contact) =>
    ["screened", "referred", "started_tpt", "completed"].includes(contact.status),
  ).length;
  const missed = contacts.filter((contact) => contact.status === "missed_follow_up").length;
  const percent = total > 0 ? Math.round((complete / total) * 100) : 0;
  if (total === 0) {
    return { complete, total, percent, label: "Add contacts to begin household screening." };
  }
  if (complete === total) {
    return { complete, total, percent, label: "All listed contacts have a screening outcome." };
  }
  if (missed > 0) {
    return { complete, total, percent, label: `${missed} contact needs follow-up recovery.` };
  }
  return { complete, total, percent, label: "Screen or refer remaining household contacts." };
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
  progressBlock: {
    gap: 8,
  },
  rowBetween: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
    alignItems: "center",
  },
  progressCount: {
    fontSize: 13,
    fontWeight: "700",
    color: "#0f172a",
  },
  progressTrack: {
    height: 8,
    borderRadius: 999,
    overflow: "hidden",
    backgroundColor: "#e2e8f0",
  },
  progressFill: {
    height: "100%",
    borderRadius: 999,
    backgroundColor: "#0f766e",
  },
  progressText: {
    fontSize: 13,
    lineHeight: 18,
    color: "#475569",
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
  actionGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  actionButton: {
    minHeight: 44,
    flexGrow: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#ffffff",
    paddingHorizontal: 12,
  },
  actionPressed: {
    backgroundColor: "#f0fdfa",
  },
  actionText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#0f172a",
  },
  contactsBlock: {
    gap: 12,
  },
  contactsHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0f172a",
  },
  addButton: {
    minHeight: 36,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#ffffff",
    paddingHorizontal: 12,
  },
  addButtonPressed: {
    backgroundColor: "#f8fafc",
  },
  addButtonText: {
    fontSize: 13,
    fontWeight: "700",
    color: "#0f172a",
  },
  addContactBlock: {
    gap: 10,
    padding: 14,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  formRow: {
    flexDirection: "row",
    gap: 10,
  },
  input: {
    minHeight: 46,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    borderRadius: 8,
    paddingHorizontal: 12,
    backgroundColor: "#ffffff",
    fontSize: 15,
    color: "#0f172a",
  },
  inputHalf: {
    flex: 1,
  },
  checkboxRow: {
    minHeight: 42,
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: "#94a3b8",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ffffff",
  },
  checkboxChecked: {
    borderColor: "#0f766e",
    backgroundColor: "#0f766e",
  },
  checkboxText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#334155",
  },
  submitButton: {
    minHeight: 46,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
    backgroundColor: "#0f766e",
  },
  submitButtonDisabled: {
    opacity: 0.65,
  },
  submitButtonText: {
    color: "#ffffff",
    fontSize: 15,
    fontWeight: "700",
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
  contactDetail: {
    gap: 12,
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  contactActions: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  smallAction: {
    minHeight: 36,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#ffffff",
    paddingHorizontal: 10,
  },
  smallActionText: {
    fontSize: 13,
    fontWeight: "700",
    color: "#0f172a",
  },
  statusHelp: {
    fontSize: 13,
    fontWeight: "700",
    color: "#64748b",
  },
  statusPicker: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
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
