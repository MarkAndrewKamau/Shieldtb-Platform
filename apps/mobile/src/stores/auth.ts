import { useEffect } from "react";
import * as SecureStore from "expo-secure-store";
import { create } from "zustand";

import { ApiError } from "@shieldtb/api-client";
import type { SignupRequest, User } from "@shieldtb/types";

import { apiClient } from "../lib/api";

const ACCESS_TOKEN_KEY = "shieldtb.accessToken";
const REFRESH_TOKEN_KEY = "shieldtb.refreshToken";
const USER_KEY = "shieldtb.user";

type AuthorizedOperation<T> = (accessToken: string) => Promise<T>;

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  isHydrated: boolean;
  isAuthenticated: boolean;
  sessionMessage: string | null;
  initialize: () => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  signup: (payload: SignupRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearSessionMessage: () => void;
  refreshSession: () => Promise<string>;
  authorizedCall: <T>(operation: AuthorizedOperation<T>) => Promise<T>;
};

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: null,
  refreshToken: null,
  user: null,
  isHydrated: false,
  isAuthenticated: false,
  sessionMessage: null,

  initialize: async () => {
    const [accessToken, refreshToken, userJson] = await Promise.all([
      SecureStore.getItemAsync(ACCESS_TOKEN_KEY),
      SecureStore.getItemAsync(REFRESH_TOKEN_KEY),
      SecureStore.getItemAsync(USER_KEY),
    ]);

    if (!refreshToken) {
      await clearSession();
      set({
        accessToken: null,
        refreshToken: null,
        user: null,
        isHydrated: true,
        isAuthenticated: false,
        sessionMessage: null,
      });
      return;
    }

    set({
      accessToken,
      refreshToken,
      user: userJson ? (JSON.parse(userJson) as User) : null,
      isAuthenticated: Boolean(accessToken || refreshToken),
    });

    try {
      let activeAccessToken = accessToken;
      if (!activeAccessToken) {
        activeAccessToken = await get().refreshSession();
      }
      const user = await apiClient.me(activeAccessToken);
      await persistSession({
        accessToken: activeAccessToken,
        refreshToken: get().refreshToken,
        user,
      });
      set({
        accessToken: activeAccessToken,
        refreshToken: get().refreshToken,
        user,
        isHydrated: true,
        isAuthenticated: true,
        sessionMessage: null,
      });
    } catch (error) {
      await clearSession();
      set({
        accessToken: null,
        refreshToken: null,
        user: null,
        isHydrated: true,
        isAuthenticated: false,
        sessionMessage: isUnauthenticated(error)
          ? "Your session expired. Sign in again to continue."
          : "We could not restore your session. Sign in again to continue.",
      });
    }
  },

  login: async (username, password) => {
    const response = await apiClient.login({ username, password, auth_mode: "token" });
    if (!response.access || !response.refresh) {
      throw new Error("Server did not return a mobile token pair.");
    }

    await persistSession({
      accessToken: response.access,
      refreshToken: response.refresh,
      user: response.user,
    });

    set({
      accessToken: response.access,
      refreshToken: response.refresh,
      user: response.user,
      isHydrated: true,
      isAuthenticated: true,
      sessionMessage: null,
    });
  },

  signup: async (payload) => {
    const response = await apiClient.signup({ ...payload, auth_mode: "token" });
    if (!response.access || !response.refresh) {
      throw new Error("Server did not return a mobile token pair.");
    }

    await persistSession({
      accessToken: response.access,
      refreshToken: response.refresh,
      user: response.user,
    });

    set({
      accessToken: response.access,
      refreshToken: response.refresh,
      user: response.user,
      isHydrated: true,
      isAuthenticated: true,
      sessionMessage: null,
    });
  },

  logout: async () => {
    const accessToken = get().accessToken;
    const refreshToken = get().refreshToken ?? undefined;

    if (accessToken) {
      try {
        await apiClient.logout(refreshToken, accessToken);
      } catch {
        // Local cleanup still matters even if the remote logout call fails.
      }
    }

    await clearSession();
    set({
      accessToken: null,
      refreshToken: null,
      user: null,
      isHydrated: true,
      isAuthenticated: false,
      sessionMessage: null,
    });
  },

  clearSessionMessage: () => set({ sessionMessage: null }),

  refreshSession: async () => {
    const refreshToken = get().refreshToken;
    if (!refreshToken) {
      throw new Error("No refresh token available.");
    }

    const response = await apiClient.refresh({ refresh: refreshToken, auth_mode: "token" });
    if (!response.access) {
      throw new Error("Server did not return a refreshed access token.");
    }

    const nextRefreshToken = response.refresh ?? refreshToken;
    await persistSession({
      accessToken: response.access,
      refreshToken: nextRefreshToken,
      user: get().user,
    });

    set({
      accessToken: response.access,
      refreshToken: nextRefreshToken,
      isAuthenticated: true,
    });

    return response.access;
  },

  authorizedCall: async <T>(operation: AuthorizedOperation<T>) => {
    let accessToken = get().accessToken;
    if (!accessToken) {
      accessToken = await get().refreshSession();
    }

    try {
      return await operation(accessToken);
    } catch (error) {
      if (!isUnauthenticated(error)) {
        throw error;
      }

      if (get().refreshToken) {
        try {
          const refreshedAccessToken = await get().refreshSession();
          return await operation(refreshedAccessToken);
        } catch (retryError) {
          if (!isUnauthenticated(retryError)) {
            throw retryError;
          }
        }
      }

      await clearSession();
      set({
        accessToken: null,
        refreshToken: null,
        user: null,
        isHydrated: true,
        isAuthenticated: false,
        sessionMessage: "Your session expired. Sign in again to continue.",
      });
      throw new Error("Your session expired. Sign in again to continue.");
    }
  },
}));

export function useBootstrapAuth(): void {
  const initialize = useAuthStore((state) => state.initialize);

  useEffect(() => {
    void initialize();
  }, [initialize]);
}

export function useIsAuthHydrated(): boolean {
  return useAuthStore((state) => state.isHydrated);
}

async function persistSession({
  accessToken,
  refreshToken,
  user,
}: {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
}): Promise<void> {
  await Promise.all([
    persistValue(ACCESS_TOKEN_KEY, accessToken),
    persistValue(REFRESH_TOKEN_KEY, refreshToken),
    persistValue(USER_KEY, user ? JSON.stringify(user) : null),
  ]);
}

async function clearSession(): Promise<void> {
  await Promise.all([
    SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY),
    SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY),
    SecureStore.deleteItemAsync(USER_KEY),
  ]);
}

async function persistValue(key: string, value: string | null): Promise<void> {
  if (value === null) {
    await SecureStore.deleteItemAsync(key);
    return;
  }
  await SecureStore.setItemAsync(key, value);
}

function isUnauthenticated(error: unknown): boolean {
  return error instanceof ApiError && error.status === 401;
}
