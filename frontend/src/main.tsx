import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";

import { msalConfig } from "./auth/msalConfig";
import App from "./App";
import "./index.css";

if (localStorage.getItem("theme") === "dark") {
  document.documentElement.classList.add("dark");
}

const msalInstance = new PublicClientApplication(msalConfig);

async function bootstrap() {
  try {
    await msalInstance.initialize();

    const response = await msalInstance.handleRedirectPromise();

    if (response) {
      msalInstance.setActiveAccount(response.account);
    } else {
      const accounts = msalInstance.getAllAccounts();
      if (accounts.length > 0) {
        msalInstance.setActiveAccount(accounts[0]);
      }
    }

    const rootElement = document.getElementById("root");
    if (!rootElement) throw new Error("Root element not found");

    ReactDOM.createRoot(rootElement).render(
      <React.StrictMode>
        <MsalProvider instance={msalInstance}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </MsalProvider>
      </React.StrictMode>
    );
  } catch (error) {
    console.error("App bootstrap failed:", error);
  }
}

bootstrap();
