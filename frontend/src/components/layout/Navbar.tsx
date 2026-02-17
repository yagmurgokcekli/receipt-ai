import { Moon, Sun, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMsal } from "@azure/msal-react";

import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function Navbar() {
    const navigate = useNavigate();
    const { instance } = useMsal();

    const account = instance.getActiveAccount();

    const handleLogout = () => {
        instance.logoutRedirect({
            postLogoutRedirectUri: "/login",
        });
    };

    const getInitials = (name?: string) => {
        if (!name) return "?";

        const parts = name.split(" ");
        if (parts.length === 1) return parts[0][0].toUpperCase();

        return (
            parts[0][0].toUpperCase() +
            parts[parts.length - 1][0].toUpperCase()
        );
    };

    const [isDark, setIsDark] = useState(() =>
        document.documentElement.classList.contains("dark")
    );

    const toggleTheme = () => {
        const html = document.documentElement;
        const next = !html.classList.contains("dark");

        html.classList.toggle("dark", next);
        localStorage.setItem("theme", next ? "dark" : "light");
        setIsDark(next);
    };

    return (
        <header className="border-b">
            <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
                <h1
                    className="text-xl font-semibold cursor-pointer"
                    onClick={() => navigate("/")}
                >
                    ReceiptAI
                </h1>

                <div className="flex items-center gap-4">
                    {/* Theme toggle */}
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={toggleTheme}
                        aria-label="Toggle theme"
                    >
                        {isDark ? (
                            <Sun className="h-5 w-5" />
                        ) : (
                            <Moon className="h-5 w-5" />
                        )}
                    </Button>

                    {/* Avatar + menu */}
                    {account && (
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="rounded-full bg-primary text-primary-foreground font-semibold hover:bg-primary/90"
                                >
                                    {getInitials(account.name)}
                                </Button>
                            </DropdownMenuTrigger>

                            <DropdownMenuContent align="end">
                                <DropdownMenuItem
                                    className="cursor-pointer flex items-center gap-2"
                                    onClick={handleLogout}
                                >
                                    <LogOut className="h-4 w-4" />
                                    Log out
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    )}
                </div>
            </div>
        </header>
    );
}
