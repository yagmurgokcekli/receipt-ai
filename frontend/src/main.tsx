import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { ThemeProvider } from "@/providers/ThemeProvider";
import { msalConfig } from "./config/msalConfig";
import App from "./App";
import "./index.css";

const msalInstance = new PublicClientApplication(msalConfig);

function BootstrapError() {
  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Application failed to start</h1>
      <p>Authentication initialization failed.</p>
      <button onClick={() => window.location.reload()}>
        Reload
      </button>
    </div>
  );
}

async function bootstrap() {
  const rootElement = document.getElementById("root");
  if (!rootElement) {
    console.error("Root element not found");
    return;
  }

  const root = ReactDOM.createRoot(rootElement);

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

    root.render(
      <React.StrictMode>
        <MsalProvider instance={msalInstance}>
          <BrowserRouter>
            <ThemeProvider
              defaultTheme="dark"
              storageKey="receiptai-theme"
            >
              <App />
            </ThemeProvider>
          </BrowserRouter>
        </MsalProvider>
      </React.StrictMode>
    );

  } catch (error) {
    console.error("App bootstrap failed:", error);
    root.render(<BootstrapError />);
  }
}

bootstrap();