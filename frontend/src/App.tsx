import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Navbar } from "@/layouts/Navbar";
import { useMsal } from "@azure/msal-react";

import HomePage from "@/pages/HomePage";
import UploadPage from "@/pages/UploadPage";
import LoginPage from "@/pages/LoginPage";
import ReceiptDetailPage from "@/pages/ReceiptDetailPage";
import { Toaster } from "@/components/ui/sonner"

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

                <Route
                    path="/receipts/:id"
                    element={
                        <ProtectedRoute>
                            <ReceiptDetailPage />
                        </ProtectedRoute>
                    }
                />
            </Routes>
            <>
                <Toaster richColors position="top-right" />
            </>
        </div>
    );
}

export default App;