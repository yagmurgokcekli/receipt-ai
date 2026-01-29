export function Navbar() {
    return (
        <header className="border-b">
            <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
                <h1 className="text-xl font-semibold">
                    ReceiptAI
                </h1>

                <nav className="text-sm text-muted-foreground">
                    Upload Receipts
                </nav>
            </div>
        </header>
    )
}
