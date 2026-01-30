import { Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"

export function Navbar() {
    const [isDark, setIsDark] = useState(false)

    useEffect(() => {
        const isDarkMode = document.documentElement.classList.contains("dark")
        setIsDark(isDarkMode)
    }, [])

    const toggleTheme = () => {
        const html = document.documentElement
        const next = !html.classList.contains("dark")

        html.classList.toggle("dark", next)
        localStorage.setItem("theme", next ? "dark" : "light")
        setIsDark(next)
    }
    return (
        <header className="border-b">
            <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
                <h1 className="text-xl font-semibold">
                    ReceiptAI
                </h1>
                <div className="flex items-center gap-4">
                    <nav className="text-sm text-muted-foreground">
                        Upload Receipts
                    </nav>

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
                </div>

            </div>
        </header>
    )
}
