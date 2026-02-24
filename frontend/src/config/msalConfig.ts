import type { Configuration } from "@azure/msal-browser";

const azureClientId = import.meta.env.VITE_AZURE_CLIENT_ID as string;
const azureAuthority = import.meta.env.VITE_AZURE_AUTHORITY as string;

if (!azureClientId || !azureAuthority) {
    throw new Error("Missing Azure AD environment configuration");
}

export const msalConfig: Configuration = {
    auth: {
        clientId: azureClientId,
        authority: azureAuthority,
        redirectUri: window.location.origin,
    },
    cache: {
        cacheLocation: "localStorage",
    },
};

export const loginRequest = {
    scopes: ["User.Read"],
};