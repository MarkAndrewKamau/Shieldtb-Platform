import { Redirect } from "expo-router";

import { useAuthStore } from "../src/stores/auth";

export default function IndexScreen() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return <Redirect href={isAuthenticated ? "/tasks" : "/login"} />;
}
