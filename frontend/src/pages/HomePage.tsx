import { useEffect, useState } from "react"
import { useMsal } from "@azure/msal-react"
import { loginRequest } from "@/auth/msalConfig"
import { fetchReceipts, type ReceiptListItem } from "@/api/receipt"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { Button } from "@/components/ui/button"
import { useNavigate } from "react-router-dom"
import { ReceiptTable } from "@/components/receipts/ReceiptTable"
import { Plus } from "lucide-react"
import { ReceiptsTableSkeleton } from "@/components/receipts/ReceiptsTableSkeleton"

export default function HomePage() {
    const { instance } = useMsal()
    const navigate = useNavigate()

    const [receipts, setReceipts] = useState<ReceiptListItem[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const loadReceipts = async () => {
            try {
                const account = instance.getActiveAccount()
                if (!account) return

                const tokenResponse = await instance.acquireTokenSilent({
                    ...loginRequest,
                    account,
                })

                const data = await fetchReceipts(tokenResponse.accessToken)
                setReceipts(data)
            } catch (err) {
                console.error("Failed to load receipts:", err)
            } finally {
                setLoading(false)
            }
        }

        loadReceipts()
    }, [instance])

    return (
        <PageWrapper>
            <div className="space-y-6 w-full">

                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-semibold tracking-tight">
                        Your Receipts
                    </h2>

                    <Button
                        onClick={() => navigate("/upload")}
                        className="
                            gap-2
                            bg-black text-white hover:bg-black/90
                            dark:bg-white dark:text-black dark:hover:bg-white/90
                        "
                    >
                        <Plus className="h-4 w-4" />
                        Upload Receipt
                    </Button>
                </div>

                {loading ? (
                    <ReceiptsTableSkeleton />
                ) : receipts.length === 0 ? (
                    <div className="text-center py-20 space-y-4">
                        <h3 className="text-lg font-medium">
                            No receipts yet
                        </h3>
                        <p className="text-muted-foreground">
                            Upload your first receipt to get started.
                        </p>
                    </div>
                ) : (
                    <div className="w-full overflow-x-auto">
                        <ReceiptTable data={receipts} />
                    </div>
                )}

            </div>
        </PageWrapper>
    )
}