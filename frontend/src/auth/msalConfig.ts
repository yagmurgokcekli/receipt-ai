import type { Configuration } from "@azure/msal-browser";

export const msalConfig: Configuration = {
    auth: {
        clientId: "a10dccd0-0b4c-402f-a070-6441987df931",
        authority:
            "https://login.microsoftonline.com/c97b1af3-2a79-4eb2-b30b-4564a05e35e5/",
        redirectUri: window.location.origin,
    },
    cache: {
        cacheLocation: "localStorage",
    },
};

export const loginRequest = {
    scopes: ["User.Read"],
};
