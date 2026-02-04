import type { ReactNode } from "react"

interface PageWrapperProps {
    children: ReactNode
}

export function PageWrapper({ children }: PageWrapperProps) {
    return (
        <main className="mx-auto max-w-6xl px-6 py-12">
            {children}
        </main>
    )
}
