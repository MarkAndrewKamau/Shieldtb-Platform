import type { ClinicalEncounter, ClinicalIntake, RiskAssessment } from "@shieldtb/types";
import { useQuery } from "@tanstack/react-query";
import { Redirect, useLocalSearchParams, useRouter } from "expo-router";
import { ArrowRight, HeartPulse, House, Phone, ShieldAlert, UserRound } from "lucide-react-native";
import type { ReactNode } from "react";
import { Linking, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { EmptyState } from "../../src/components/EmptyState";
import { LoadingBlock } from "../../src/components/LoadingBlock";
import { ScreenHeader } from "../../src/components/ScreenHeader";
import { StatusBadge } from "../../src/components/StatusBadge";
import { apiClient } from "../../src/lib/api";
import { compactValue, formatDateTime, formatLabel, formatShortDate } from "../../src/lib/format";
import { useAuthStore } from "../../src/stores/auth";

const INTAKE_FIELDS: Array<{ key: keyof ClinicalIntake; label: string }> = [
  { key: "cough", label: "Cough" },
  { key: "fever", label: "Fever" },
  { key: "night_sweats", label: "Night sweats" },
  { key: "weight_loss", label: "Weight loss" },
  { key: "hiv_positive", label: "HIV positive" },
  { key: "pregnant", label: "Pregnant" },
  { key: "postpartum", label: "Postpartum" },
  { key: "previous_tb", label: "Previous TB" },
  { key: "household_tb_contact", label: "Household TB contact" },
  { key: "crowded_housing", label: "Crowded housing" },
  { key: "poor_ventilation", label: "Poor ventilation" },
];

export default function PatientSummaryScreen() {
  const params = useLocalSearchParams<{ id: string; householdId?: string }>();
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const authorizedCall = useAuthStore((state) => state.authorizedCall);
  const patientId = Number(params.id);
  const householdId = params.householdId ? Number(params.householdId) : null;

  const patientQuery = useQuery({
    queryKey: ["patient", patientId],
    queryFn: () => authorizedCall((accessToken) => apiClient.getPatient(patientId, accessToken)),
    enabled: isAuthenticated && Number.isFinite(patientId),
  });

  const riskQuery = useQuery({
    queryKey: ["risk-assessments", "patient", patientId],
    queryFn: () =>
      authorizedCall((accessToken) =>
        apiClient.listRiskAssessments(accessToken, { patient: patientId }),
      ),
    enabled: isAuthenticated && Number.isFinite(patientId),
  });

  const encounterQuery = useQuery({
    queryKey: ["clinical-encounters", "patient", patientId],
    queryFn: () =>
      authorizedCall((accessToken) =>
        apiClient.listClinicalEncounters(accessToken, { patient: patientId }),
      ),
    enabled: isAuthenticated && Number.isFinite(patientId),
  });

  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  if (patientQuery.isLoading) {
    return <LoadingBlock label="Loading patient summary..." />;
  }

  if (!patientQuery.data) {
    return (
      <EmptyState
        title="Patient unavailable"
        description="This patient may be outside your assigned facility scope."
      />
    );
  }

  const patient = patientQuery.data;
  const latestRisk = riskQuery.data?.[0];
  const latestEncounter = encounterQuery.data?.[0];

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <ScreenHeader
        title={patient.full_name}
        subtitle={patient.external_id ? `Patient ${patient.external_id}` : "Index patient summary"}
      />

      <View style={styles.identity}>
        <View style={styles.identityIcon}>
          <UserRound color="#0f766e" size={24} />
        </View>
        <View style={styles.identityCopy}>
          <Text style={styles.identityName}>{patient.full_name}</Text>
          <Text style={styles.identityMeta}>
            {[formatLabel(patient.sex), patient.date_of_birth ? bornLabel(patient.date_of_birth) : null]
              .filter(Boolean)
              .join(" | ")}
          </Text>
        </View>
      </View>

      <View style={styles.details}>
        <DetailRow label="Enrollment source" value={formatLabel(patient.enrollment_source)} />
        <DetailRow
          label="Consent"
          value={patient.consented_at ? formatShortDate(patient.consented_at) : "Not recorded"}
        />
        <DetailRow label="Status" value={patient.is_active ? "Active" : "Inactive"} />
      </View>

      <View style={styles.actionGrid}>
        {patient.phone ? (
          <Pressable
            accessibilityRole="button"
            onPress={() => Linking.openURL(`tel:${patient.phone}`)}
            style={({ pressed }) => [styles.actionButton, pressed ? styles.actionPressed : null]}
          >
            <Phone color="#0f766e" size={18} />
            <Text style={styles.actionText}>Call patient</Text>
          </Pressable>
        ) : null}

        {householdId ? (
          <Pressable
            accessibilityRole="button"
            onPress={() => router.push(`/households/${householdId}`)}
            style={({ pressed }) => [styles.actionButton, pressed ? styles.actionPressed : null]}
          >
            <House color="#0f766e" size={18} />
            <Text style={styles.actionText}>Open household</Text>
          </Pressable>
        ) : null}
      </View>

      <Section title="Recent risk" icon={<ShieldAlert color="#0f766e" size={18} />}>
        {riskQuery.isLoading ? (
          <Text style={styles.muted}>Loading risk assessment...</Text>
        ) : latestRisk ? (
          <RiskSummary risk={latestRisk} />
        ) : (
          <Text style={styles.muted}>No risk assessment recorded yet.</Text>
        )}
      </Section>

      <Section title="Clinical summary" icon={<HeartPulse color="#0f766e" size={18} />}>
        {encounterQuery.isLoading ? (
          <Text style={styles.muted}>Loading clinical summary...</Text>
        ) : latestEncounter ? (
          <EncounterSummary encounter={latestEncounter} />
        ) : (
          <Text style={styles.muted}>No clinical encounter recorded yet.</Text>
        )}
      </Section>
    </ScrollView>
  );
}

function RiskSummary({ risk }: { risk: RiskAssessment }) {
  return (
    <View style={styles.stack}>
      <View style={styles.rowBetween}>
        <Text style={styles.label}>Tier</Text>
        <StatusBadge value={risk.tier} />
      </View>
      <DetailRow label="Score" value={String(risk.score)} />
      <DetailRow label="Assessed" value={formatDateTime(risk.created_at)} />
      {Object.keys(risk.explanation).length > 0 ? (
        <View style={styles.notesBlock}>
          <Text style={styles.label}>Explanation</Text>
          <Text style={styles.notes}>{compactValue(risk.explanation)}</Text>
        </View>
      ) : null}
    </View>
  );
}

function EncounterSummary({ encounter }: { encounter: ClinicalEncounter }) {
  const positiveFindings = encounter.intake
    ? INTAKE_FIELDS.filter((field) => Boolean(encounter.intake?.[field.key])).map(
        (field) => field.label,
      )
    : [];

  return (
    <View style={styles.stack}>
      <DetailRow label="Encounter" value={formatLabel(encounter.encounter_type)} />
      <DetailRow label="Occurred" value={formatDateTime(encounter.occurred_at)} />
      {encounter.risk_assessment ? (
        <View style={styles.rowBetween}>
          <Text style={styles.label}>Risk at encounter</Text>
          <StatusBadge value={encounter.risk_assessment.tier} />
        </View>
      ) : null}
      {positiveFindings.length > 0 ? (
        <View style={styles.findings}>
          {positiveFindings.map((finding) => (
            <Text key={finding} style={styles.finding}>
              {finding}
            </Text>
          ))}
        </View>
      ) : encounter.intake ? (
        <Text style={styles.muted}>No intake risk flags were marked.</Text>
      ) : null}
      {encounter.notes ? (
        <View style={styles.notesBlock}>
          <Text style={styles.label}>Notes</Text>
          <Text style={styles.notes}>{encounter.notes}</Text>
        </View>
      ) : null}
    </View>
  );
}

function Section({
  title,
  icon,
  children,
}: {
  title: string;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        {icon}
        <Text style={styles.sectionTitle}>{title}</Text>
      </View>
      {children}
    </View>
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

function bornLabel(dateOfBirth: string): string {
  return `Born ${formatShortDate(dateOfBirth)}`;
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
    width: 48,
    height: 48,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#f0fdfa",
  },
  identityCopy: {
    flex: 1,
    gap: 4,
  },
  identityName: {
    fontSize: 18,
    fontWeight: "700",
    color: "#0f172a",
  },
  identityMeta: {
    fontSize: 13,
    color: "#475569",
  },
  details: {
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  detailRow: {
    minHeight: 46,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
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
  actionGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  actionButton: {
    minHeight: 46,
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
  section: {
    gap: 12,
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
  rowBetween: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
  },
  stack: {
    gap: 12,
  },
  notesBlock: {
    gap: 6,
  },
  notes: {
    fontSize: 14,
    lineHeight: 21,
    color: "#1e293b",
  },
  muted: {
    fontSize: 14,
    lineHeight: 20,
    color: "#475569",
  },
  findings: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  finding: {
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 6,
    backgroundColor: "#fef3c7",
    color: "#92400e",
    fontSize: 12,
    fontWeight: "700",
  },
});
