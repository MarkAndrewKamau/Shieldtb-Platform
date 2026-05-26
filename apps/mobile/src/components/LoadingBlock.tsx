import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

type LoadingBlockProps = {
  label: string;
};

export function LoadingBlock({ label }: LoadingBlockProps) {
  return (
    <View style={styles.container}>
      <ActivityIndicator color="#0f766e" size="small" />
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    minHeight: 220,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    padding: 24,
    backgroundColor: "#f8fafc",
  },
  label: {
    fontSize: 14,
    color: "#475569",
  },
});
