import { Shield, TriangleAlert } from "lucide-react-native";
import { Redirect, useRouter } from "expo-router";
import { Controller, useForm } from "react-hook-form";
import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useAuthStore } from "../src/stores/auth";
import { formatLoginError } from "../src/lib/errors";

type LoginForm = {
  username: string;
  password: string;
};

export default function LoginScreen() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const sessionMessage = useAuthStore((state) => state.sessionMessage);
  const clearSessionMessage = useAuthStore((state) => state.clearSessionMessage);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    defaultValues: {
      username: "",
      password: "",
    },
  });

  if (isAuthenticated) {
    return <Redirect href="/tasks" />;
  }

  const onSubmit = handleSubmit(async (values) => {
    clearSessionMessage();
    setSubmitError(null);
    try {
      await login(values.username.trim(), values.password);
      router.replace("/tasks");
    } catch (error) {
      setSubmitError(formatLoginError(error));
    }
  });

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.container}
      >
        <View style={styles.brandBlock}>
          <View style={styles.brandIcon}>
            <Shield color="#ffffff" size={24} strokeWidth={2.25} />
          </View>
          <Text style={styles.title}>ShieldTB Mobile</Text>
          <Text style={styles.subtitle}>
            Community health worker workflows for household tracing and follow-up.
          </Text>
        </View>

        <View style={styles.formBlock}>
          <Text style={styles.label}>Username</Text>
          <Controller
            control={control}
            name="username"
            rules={{ required: "Username is required." }}
            render={({ field: { onChange, onBlur, value } }) => (
              <TextInput
                autoCapitalize="none"
                autoCorrect={false}
                onBlur={onBlur}
                onChangeText={onChange}
                placeholder="Enter your username"
                placeholderTextColor="#94a3b8"
                style={styles.input}
                value={value}
              />
            )}
          />
          {errors.username ? <Text style={styles.fieldError}>{errors.username.message}</Text> : null}

          <Text style={styles.label}>Password</Text>
          <Controller
            control={control}
            name="password"
            rules={{ required: "Password is required." }}
            render={({ field: { onChange, onBlur, value } }) => (
              <TextInput
                autoCapitalize="none"
                autoCorrect={false}
                onBlur={onBlur}
                onChangeText={onChange}
                placeholder="Enter your password"
                placeholderTextColor="#94a3b8"
                secureTextEntry
                style={styles.input}
                value={value}
              />
            )}
          />
          {errors.password ? <Text style={styles.fieldError}>{errors.password.message}</Text> : null}

          {sessionMessage || submitError ? (
            <View style={styles.errorBanner}>
              <TriangleAlert color="#b91c1c" size={18} />
              <Text style={styles.errorBannerText}>{sessionMessage ?? submitError}</Text>
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
              <Text style={styles.submitButtonText}>Sign in</Text>
            )}
          </Pressable>

          <Pressable
            accessibilityRole="button"
            onPress={() => router.push("/signup")}
            style={({ pressed }) => [styles.secondaryButton, pressed ? styles.secondaryButtonPressed : null]}
          >
            <Text style={styles.secondaryButtonText}>Create a new account</Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  container: {
    flex: 1,
    paddingHorizontal: 24,
    paddingVertical: 32,
    justifyContent: "center",
    gap: 28,
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
    gap: 10,
  },
  label: {
    marginTop: 8,
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
  fieldError: {
    fontSize: 13,
    color: "#b91c1c",
  },
  errorBanner: {
    marginTop: 8,
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
    marginTop: 12,
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
  secondaryButton: {
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "#cbd5e1",
    backgroundColor: "#ffffff",
  },
  secondaryButtonPressed: {
    opacity: 0.9,
  },
  secondaryButtonText: {
    color: "#0f172a",
    fontWeight: "600",
    fontSize: 15,
  },
});
