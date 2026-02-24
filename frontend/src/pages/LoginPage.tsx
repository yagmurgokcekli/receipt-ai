import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "@/auth/msalConfig";

export default function LoginPage() {
    const { instance } = useMsal();

    const handleLogin = () => {
        instance.loginRedirect({
            ...loginRequest,
            redirectStartPage: window.location.origin,
        });
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-6 bg-background transition-colors">

            <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-16 items-center">

                <div className="hidden lg:flex flex-col gap-8">
                    <h1 className="text-5xl font-bold leading-tight bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                        ReceiptAI
                    </h1>

                    <p className="text-lg text-muted-foreground max-w-md leading-relaxed">
                        AI-powered receipt analysis platform.
                        Upload, analyze and compare receipts instantly
                        using multiple AI engines.
                    </p>

                    <div className="flex flex-wrap gap-3 mt-4">
                        <span className="px-4 py-1.5 text-xs rounded-full border bg-muted/40">
                            ⚡ Fast processing
                        </span>
                        <span className="px-4 py-1.5 text-xs rounded-full border bg-muted/40">
                            🤖 AI extraction
                        </span>
                        <span className="px-4 py-1.5 text-xs rounded-full border bg-muted/40">
                            🔐 Secure storage
                        </span>
                    </div>
                </div>

                <Card className="w-full max-w-md mx-auto shadow-2xl border rounded-2xl bg-card">
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
                            className="w-full flex items-center gap-2 justify-center"
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