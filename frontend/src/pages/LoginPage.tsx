import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "@/auth/msalConfig";

export default function LoginPage() {
    const { instance } = useMsal();

    const handleLogin = () => {
        instance.loginRedirect({
            ...loginRequest,
            redirectStartPage: window.location.origin
        });
    };

    return (
        <div className="relative min-h-screen flex items-center justify-center overflow-hidden">

            {/* BACKGROUND */}
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-900 via-slate-900 to-black" />

            <div
                className="absolute inset-0 opacity-10 bg-cover bg-center"
                style={{
                    backgroundImage:
                        "url('/ai-background.jpg')",
                }}
            />

            {/* CONTENT */}
            <div className="relative grid md:grid-cols-2 gap-12 items-center px-6 max-w-6xl w-full">

                {/* LEFT SIDE */}
                <div className="hidden md:flex flex-col gap-6 text-white">
                    <h1 className="text-5xl font-bold leading-tight">
                        ReceiptAI
                    </h1>

                    <p className="text-xl text-muted-foreground max-w-md">
                        AI-powered receipt analysis platform.
                        Upload, analyze and compare receipts instantly
                        using multiple AI engines.
                    </p>

                    <div className="flex gap-3 text-sm text-muted-foreground">
                        <span>⚡ Fast processing</span>
                        <span>🤖 AI extraction</span>
                        <span>🔐 Secure storage</span>
                    </div>
                </div>

                {/* LOGIN CARD */}
                <Card className="backdrop-blur-xl bg-background/70 shadow-xl border border-white/10">
                    <CardHeader>
                        <CardTitle className="text-center text-2xl">
                            Welcome to ReceiptAI
                        </CardTitle>
                    </CardHeader>

                    <CardContent className="flex flex-col gap-6">

                        <p className="text-sm text-muted-foreground text-center">
                            Sign in to continue
                        </p>

                        <Button
                            onClick={handleLogin}
                            className="flex items-center gap-2 w-full"
                            variant="secondary"
                        >
                            <img
                                src="/microsoft-logo.webp"
                                alt="Microsoft"
                                className="h-4 w-4"
                            />
                            Sign in with Microsoft
                        </Button>


                        <p className="text-xs text-muted-foreground text-center">
                            Secure authentication via Microsoft
                        </p>

                    </CardContent>
                </Card>
            </div>
        </div>
    );
}