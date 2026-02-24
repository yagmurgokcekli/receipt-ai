import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { useMsal } from "@azure/msal-react";

import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";

function App() {
    const { instance } = useMsal();
    const location = useLocation();

    const activeAccount =
        instance.getActiveAccount() ??
        instance.getAllAccounts()[0];

    const isAuthenticated = !!activeAccount;

    const ProtectedHome = () => {
        if (!isAuthenticated) {
            return <Navigate to="/login" replace />;
        }

        return <HomePage />;
    };

    return (
        <div>
            {location.pathname !== "/login" && <Navbar />}

            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/" element={<ProtectedHome />} />
            </Routes>
        </div>
    );
}

export default App;
