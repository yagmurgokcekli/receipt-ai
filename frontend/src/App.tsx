import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { useMsal } from "@azure/msal-react";

import HomePage from "@/pages/HomePage";
import UploadPage from "@/pages/UploadPage";
import LoginPage from "@/pages/LoginPage";

function App() {
    const { instance } = useMsal();
    const location = useLocation();

    const activeAccount =
        instance.getActiveAccount() ??
        instance.getAllAccounts()[0];

    const isAuthenticated = !!activeAccount;

    const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
        if (!isAuthenticated) {
            return <Navigate to="/login" replace />;
        }
        return <>{children}</>;
    };

    return (
        <div>
            {location.pathname !== "/login" && <Navbar />}

            <Routes>
                <Route path="/login" element={<LoginPage />} />

                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <HomePage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/upload"
                    element={
                        <ProtectedRoute>
                            <UploadPage />
                        </ProtectedRoute>
                    }
                />
            </Routes>
        </div>
    );
}

export default App;