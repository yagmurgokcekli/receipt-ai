import {
    ChevronsUpDown,
    LogOut,
} from "lucide-react"

import {
    Avatar,
    AvatarFallback,
} from "@/components/ui/avatar"

import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

import { Button } from "@/components/ui/button"
import { useNavigate } from "react-router-dom"
import { useMsal } from "@azure/msal-react"

export function AvatarDropdown() {
    const navigate = useNavigate()
    const { instance } = useMsal()
    const account = instance.getActiveAccount()

    if (!account) return null

    const name = account.name ?? "User"

    const email =
        account.username ||
        account.idTokenClaims?.preferred_username ||
        ""

        const handleLogout = () => {
            instance.clearCache();
            navigate("/login");
        };

    const getInitials = (name?: string) => {
        if (!name) return "?"
        const parts = name.split(" ")
        if (parts.length === 1) return parts[0][0].toUpperCase()
        return (
            parts[0][0].toUpperCase() +
            parts[parts.length - 1][0].toUpperCase()
        )
    }

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button
                    variant="ghost"
                    className="flex items-center gap-2 px-2"
                >
                    <Avatar className="h-8 w-8 rounded-lg">
                        <AvatarFallback>
                            {getInitials(name)}
                        </AvatarFallback>
                    </Avatar>

                    <div className="hidden sm:grid text-left text-sm leading-tight">
                        <span className="truncate font-medium">
                            {name}
                        </span>
                        <span className="truncate text-xs text-muted-foreground">
                            {email}
                        </span>
                    </div>

                    <ChevronsUpDown className="size-4 opacity-60" />
                </Button>
            </DropdownMenuTrigger>

            <DropdownMenuContent
                align="end"
                className="w-80"
            >
                <DropdownMenuLabel className="p-0 font-normal">
                    <div className="flex items-center gap-3 px-3 py-3">
                        <Avatar className="h-10 w-10 rounded-lg">
                            <AvatarFallback>
                                {getInitials(name)}
                            </AvatarFallback>
                        </Avatar>

                        <div className="grid text-sm leading-tight">
                            <span className="font-medium">
                                {name}
                            </span>
                            <span className="text-xs text-muted-foreground">
                                {email}
                            </span>
                        </div>
                    </div>
                </DropdownMenuLabel>

                <DropdownMenuSeparator />

                <DropdownMenuItem
                    onClick={handleLogout}
                    className="cursor-pointer flex items-center gap-2 text-red-500 focus:text-red-500"
                >
                    <LogOut className="h-4 w-4" />
                    Log out
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}