import { ShieldTBApiClient } from "@shieldtb/api-client";

import { API_BASE_URL } from "./env";

export const apiClient = new ShieldTBApiClient(API_BASE_URL);
