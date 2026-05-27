import type { FacilitySummary, UserRole } from "@shieldtb/types";
import { useQuery } from "@tanstack/react-query";
import { Building2, Check, ChevronLeft, Shield, TriangleAlert } from "lucide-react-native";
import { Redirect, useRouter } from "expo-router";
import {
  Controller,
  type Control,
  type FieldPath,
  type RegisterOptions,
  useForm,
} from "react-hook-form";
import { type ReactNode, useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useAuthStore } from "../src/stores/auth";
import { formatApiError } from "../src/lib/errors";
import { apiClient } from "../src/lib/api";

type SignupForm = {
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  phone: string;
  facilityId: string;
  password: string;
  role: Exclude<UserRole, "admin">;
};

const ROLE_OPTIONS: Array<{ value: Exclude<UserRole, "admin">; label: string }> = [
  { value: "chw", label: "CHW" },
  { value: "clinician", label: "Clinician" },
  { value: "facility_officer", label: "Facility officer" },
  { value: "analyst", label: "Analyst" },
];

export default function SignupScreen() {
  const router = useRouter();
  const signup = useAuthStore((state) => state.signup);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [facilitySearch, setFacilitySearch] = useState("");
  const [selectedFacility, setSelectedFacility] = useState<FacilitySummary | null>(null);
  const {
    control,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<SignupForm>({
    defaultValues: {
      username: "",
      email: "",
      firstName: "",
      lastName: "",
      phone: "",
      facilityId: "",
      password: "",
      role: "chw",
    },
  });

  const selectedRole = watch("role");
  const facilityQuery = facilitySearch.trim();
  const facilitiesQuery = useQuery({
    queryKey: ["signup-facilities", facilityQuery],
    queryFn: () => apiClient.searchSignupFacilities(facilityQuery),
    enabled: facilityQuery.length >= 2 && !selectedFacility,
  });

  if (isAuthenticated) {
    return <Redirect href="/tasks" />;
  }

  const onSubmit = handleSubmit(async (values) => {
    setSubmitError(null);
    try {
      await signup({
        username: values.username.trim(),
        email: values.email.trim(),
        first_name: values.firstName.trim(),
        last_name: values.lastName.trim(),
        phone: values.phone.trim(),
        facility: Number(values.facilityId),
        password: values.password,
        role: values.role,
      });
      router.replace("/tasks");
    } catch (error) {
      setSubmitError(formatApiError(error, "Could not create account. Please try again."));
    }
  });

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.container}
      >
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
          <Pressable onPress={() => router.back()} style={styles.backButton}>
            <ChevronLeft color="#0f172a" size={18} />
            <Text style={styles.backText}>Back to sign in</Text>
          </Pressable>

          <View style={styles.brandBlock}>
            <View style={styles.brandIcon}>
              <Shield color="#ffffff" size={24} strokeWidth={2.25} />
            </View>
            <Text style={styles.title}>Create account</Text>
            <Text style={styles.subtitle}>
              Register for mobile field workflows and select the facility where you work.
            </Text>
          </View>

          <View style={styles.formBlock}>
            <LabeledField label="Role">
              <Controller
                control={control}
                name="role"
                render={({ field: { value, onChange } }) => (
                  <View style={styles.roleGrid}>
                    {ROLE_OPTIONS.map((role) => {
                      const selected = role.value === value;
                      return (
                        <Pressable
                          key={role.value}
                          onPress={() => onChange(role.value)}
                          style={[styles.roleOption, selected ? styles.roleOptionSelected : null]}
                        >
                          <Text
                            style={[
                              styles.roleOptionText,
                              selected ? styles.roleOptionTextSelected : null,
                            ]}
                          >
                            {role.label}
                          </Text>
                        </Pressable>
                      );
                    })}
                  </View>
                )}
              />
            </LabeledField>

            <FormInput
              control={control}
              name="username"
              label="Username"
              placeholder="Choose a username"
              rules={{ required: "Username is required." }}
              error={errors.username?.message}
            />

            <FormInput
              control={control}
              name="email"
              label="Email"
              placeholder="name@example.com"
              keyboardType="email-address"
              autoCapitalize="none"
              rules={{
                required: "Email is required.",
                pattern: { value: /\S+@\S+\.\S+/, message: "Enter a valid email address." },
              }}
              error={errors.email?.message}
            />

            <FormInput
              control={control}
              name="firstName"
              label="First name"
              placeholder="Given name"
              rules={{ required: "First name is required." }}
              error={errors.firstName?.message}
            />

            <FormInput
              control={control}
              name="lastName"
              label="Last name"
              placeholder="Family name"
              rules={{ required: "Last name is required." }}
              error={errors.lastName?.message}
            />

            <FormInput
              control={control}
              name="phone"
              label="Phone"
              placeholder="+2547..."
              keyboardType="phone-pad"
              rules={{ required: "Phone number is required." }}
              error={errors.phone?.message}
            />

            <LabeledField label="Facility" error={errors.facilityId?.message}>
              <Controller
                control={control}
                name="facilityId"
                rules={{ required: "Select your facility to continue." }}
                render={() => (
                  <>
                    <View style={styles.searchWrap}>
                      <Building2 color="#64748b" size={18} />
                      <TextInput
                        autoCapitalize="words"
                        autoCorrect={false}
                        onChangeText={(value) => {
                          setFacilitySearch(value);
                          if (selectedFacility) {
                            setSelectedFacility(null);
                            setValue("facilityId", "", { shouldValidate: true });
                          }
                        }}
                        placeholder="Search facility name or code"
                        placeholderTextColor="#94a3b8"
                        style={styles.searchInput}
                        value={facilitySearch}
                      />
                    </View>

                    {selectedFacility ? (
                      <View style={styles.selectedFacility}>
                        <View style={styles.facilityCopy}>
                          <Text style={styles.facilityName}>{selectedFacility.name}</Text>
                          <Text style={styles.facilityMeta}>
                            {selectedFacility.code}
                            {selectedFacility.county ? `  |  ${selectedFacility.county}` : ""}
                          </Text>
                        </View>
                        <Check color="#0f766e" size={20} />
                      </View>
                    ) : facilityQuery.length < 2 ? (
                      <Text style={styles.helperText}>Enter at least 2 characters to find a facility.</Text>
                    ) : facilitiesQuery.isLoading ? (
                      <Text style={styles.helperText}>Searching facilities...</Text>
                    ) : facilitiesQuery.isError ? (
                      <Text style={styles.fieldError}>Facility search is unavailable. Try again.</Text>
                    ) : facilitiesQuery.data?.length === 0 ? (
                      <Text style={styles.helperText}>No active facilities match that search.</Text>
                    ) : (
                      <View style={styles.facilityResults}>
                        {(facilitiesQuery.data ?? []).map((facility) => (
                          <Pressable
                            key={facility.id}
                            accessibilityRole="button"
                            onPress={() => {
                              setSelectedFacility(facility);
                              setFacilitySearch(`${facility.name} (${facility.code})`);
                              setValue("facilityId", String(facility.id), {
                                shouldValidate: true,
                              });
                            }}
                            style={({ pressed }) => [
                              styles.facilityOption,
                              pressed ? styles.facilityOptionPressed : null,
                            ]}
                          >
                            <Text style={styles.facilityName}>{facility.name}</Text>
                            <Text style={styles.facilityMeta}>
                              {facility.code}
                              {facility.county ? `  |  ${facility.county}` : ""}
                            </Text>
                          </Pressable>
                        ))}
                      </View>
                    )}
                  </>
                )}
              />
            </LabeledField>

            <FormInput
              control={control}
              name="password"
              label="Password"
              placeholder="Minimum 12 characters"
              secureTextEntry
              autoCapitalize="none"
              rules={{
                required: "Password is required.",
                minLength: { value: 12, message: "Password must be at least 12 characters." },
              }}
              error={errors.password?.message}
            />

            <Text style={styles.helperText}>
              Selected role: {formatRole(selectedRole)}. Admin accounts are intentionally excluded from public signup.
            </Text>

            {submitError ? (
              <View style={styles.errorBanner}>
                <TriangleAlert color="#b91c1c" size={18} />
                <Text style={styles.errorBannerText}>{submitError}</Text>
              </View>
            ) : null}

            <Pressable
              accessibilityRole="button"
              disabled={isSubmitting}
              onPress={onSubmit}
              style={({ pressed }) => [
                styles.submitButton,
                pressed ? styles.submitButtonPressed : null,
                isSubmitting ? styles.submitButtonDisabled : null,
              ]}
            >
              {isSubmitting ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.submitButtonText}>Create account</Text>
              )}
            </Pressable>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

type FormInputProps = {
  control: Control<SignupForm>;
  name: FieldPath<SignupForm>;
  label: string;
  placeholder: string;
  error?: string;
  secureTextEntry?: boolean;
  keyboardType?: "default" | "email-address" | "phone-pad" | "number-pad";
  autoCapitalize?: "none" | "sentences" | "words" | "characters";
  rules?: RegisterOptions<SignupForm, FieldPath<SignupForm>>;
};

function FormInput({
  control,
  name,
  label,
  placeholder,
  error,
  secureTextEntry,
  keyboardType,
  autoCapitalize,
  rules,
}: FormInputProps) {
  return (
    <LabeledField label={label} error={error}>
      <Controller
        control={control}
        name={name}
        rules={rules}
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            autoCapitalize={autoCapitalize ?? "sentences"}
            autoCorrect={false}
            keyboardType={keyboardType}
            onBlur={onBlur}
            onChangeText={onChange}
            placeholder={placeholder}
            placeholderTextColor="#94a3b8"
            secureTextEntry={secureTextEntry}
            style={styles.input}
            value={String(value ?? "")}
          />
        )}
      />
    </LabeledField>
  );
}

function LabeledField({
  label,
  children,
  error,
}: {
  label: string;
  children: ReactNode;
  error?: string;
}) {
  return (
    <View style={styles.fieldBlock}>
      <Text style={styles.label}>{label}</Text>
      {children}
      {error ? <Text style={styles.fieldError}>{error}</Text> : null}
    </View>
  );
}

function formatRole(role: Exclude<UserRole, "admin">): string {
  return role
    .split("_")
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(" ");
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  container: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 24,
    paddingVertical: 24,
    gap: 22,
  },
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    alignSelf: "flex-start",
  },
  backText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#334155",
  },
  brandBlock: {
    gap: 12,
  },
  brandIcon: {
    width: 48,
    height: 48,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#0f766e",
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "#0f172a",
  },
  subtitle: {
    fontSize: 15,
    lineHeight: 22,
    color: "#475569",
  },
  formBlock: {
    gap: 14,
  },
  fieldBlock: {
    gap: 8,
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
    color: "#334155",
  },
  input: {
    borderWidth: 1,
    borderColor: "#cbd5e1",
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 14,
    backgroundColor: "#ffffff",
    fontSize: 16,
    color: "#0f172a",
  },
  searchWrap: {
    height: 52,
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    borderRadius: 8,
    paddingHorizontal: 14,
    backgroundColor: "#ffffff",
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: "#0f172a",
  },
  facilityResults: {
    gap: 8,
  },
  facilityOption: {
    gap: 4,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  facilityOptionPressed: {
    backgroundColor: "#f0fdfa",
    borderColor: "#99f6e4",
  },
  selectedFacility: {
    minHeight: 56,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#99f6e4",
    backgroundColor: "#f0fdfa",
  },
  facilityCopy: {
    flex: 1,
    gap: 4,
  },
  facilityName: {
    fontSize: 14,
    fontWeight: "600",
    color: "#0f172a",
  },
  facilityMeta: {
    fontSize: 12,
    color: "#475569",
  },
  roleGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  roleOption: {
    minWidth: "47%",
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#ffffff",
  },
  roleOptionSelected: {
    borderColor: "#0f766e",
    backgroundColor: "#f0fdfa",
  },
  roleOptionText: {
    textAlign: "center",
    fontWeight: "600",
    color: "#0f172a",
    fontSize: 14,
  },
  roleOptionTextSelected: {
    color: "#0f766e",
  },
  fieldError: {
    fontSize: 13,
    color: "#b91c1c",
  },
  helperText: {
    fontSize: 13,
    lineHeight: 19,
    color: "#64748b",
  },
  errorBanner: {
    flexDirection: "row",
    gap: 8,
    alignItems: "flex-start",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#fecaca",
    backgroundColor: "#fef2f2",
    padding: 12,
  },
  errorBannerText: {
    flex: 1,
    fontSize: 13,
    lineHeight: 18,
    color: "#991b1b",
  },
  submitButton: {
    marginTop: 8,
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#0f766e",
  },
  submitButtonPressed: {
    opacity: 0.92,
  },
  submitButtonDisabled: {
    opacity: 0.7,
  },
  submitButtonText: {
    color: "#ffffff",
    fontWeight: "700",
    fontSize: 16,
  },
});
