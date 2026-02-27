import { useNavigate } from "react-router-dom";
import { ModeToggle } from "@/components/ModeToggle/ModeToggle";
import { AvatarDropdown } from "@/components/AvatarDropdown/AvatarDropdown";

export function Navbar() {
    const navigate = useNavigate();


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
                    <AvatarDropdown />
                    <ModeToggle />
                </div>
            </div>
        </header>
    );
}
