import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useMsal } from "@azure/msal-react";

export function AvatarDropdown() {
    const navigate = useNavigate();
    const { instance } = useMsal();

    const account = instance.getActiveAccount();

    const handleLogout = () => {
        instance.clearCache();
        navigate("/login");
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

    if (!account) return null;

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="rounded-full">
                    <Avatar>
                        <AvatarFallback>
                            {getInitials(account.name)}
                        </AvatarFallback>
                    </Avatar>
                </Button>
            </DropdownMenuTrigger>

            <DropdownMenuContent align="end" className="w-36">
                <DropdownMenuGroup>
                    <DropdownMenuItem
                        onClick={handleLogout}
                        className="cursor-pointer flex items-center gap-2 text-red-500"
                    >
                        <LogOut className="h-4 w-4" />
                        Log out
                    </DropdownMenuItem>
                </DropdownMenuGroup>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
