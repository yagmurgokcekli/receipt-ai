import { useEffect, useState } from "react"
import { useMsal } from "@azure/msal-react"
import { loginRequest } from "@/config/msalConfig"
import { fetchReceipts, type ReceiptListItem } from "@/api/receipt"
import { PageWrapper } from "@/layouts/PageWrapper"
import { Button } from "@/components/ui/button"
import { useNavigate } from "react-router-dom"
import { ReceiptTable } from "@/components/ReceiptTable/ReceiptTable"
import { Plus } from "lucide-react"
import { ReceiptsTableSkeleton } from "@/components/ReceiptTable/ReceiptsTableSkeleton"
import { Dashboard } from "@/components/Dashboard/Dashboard"
import {
    fetchCategoryDistribution,
    fetchMonthlyTrend,
    fetchSummary,
} from "@/api/dashboard"
import { Skeleton } from "@/components/ui/skeleton"

export default function HomePage() {
    const { instance } = useMsal()
    const navigate = useNavigate()

    const [receipts, setReceipts] = useState<ReceiptListItem[]>([])
    const [loading, setLoading] = useState(true)
    const [dashboardLoading, setDashboardLoading] = useState(true)

    const [categoryData, setCategoryData] = useState<any[]>([])
    const [trendData, setTrendData] = useState<any[]>([])
    const [summary, setSummary] = useState<any>(null)

    useEffect(() => {
        const loadData = async () => {
            try {
                const account = instance.getActiveAccount()
                if (!account) return

                const tokenResponse = await instance.acquireTokenSilent({
                    ...loginRequest,
                    account,
                })

                const token = tokenResponse.accessToken

                const [
                    receiptsData,
                    categories,
                    trend,
                    summaryData,
                ] = await Promise.all([
                    fetchReceipts(token),
                    fetchCategoryDistribution(token),
                    fetchMonthlyTrend(token),
                    fetchSummary(token),
                ])

                // receipts
                setReceipts(receiptsData)

                // dashboard
                setCategoryData(categories)

                setTrendData(
                    trend.map((t: any) => ({
                        name: `${t.year}-${String(t.month).padStart(2, "0")}`,
                        total: t.total,
                    }))
                )

                setSummary(summaryData)

            } catch (err) {
                console.error("Failed to load data:", err)
            } finally {
                setLoading(false)
                setDashboardLoading(false)
            }
        }

        loadData()
    }, [instance])

    return (
        <PageWrapper>
            <div className="space-y-6 w-full">

                {dashboardLoading ? (
                    <div className="space-y-10">
                        <div className="grid grid-cols-3 gap-6">
                            <Skeleton className="h-30 rounded-2xl" />
                            <Skeleton className="h-30 rounded-2xl" />
                        </div>
                        <div className="grid grid-cols-2 gap-8">
                            <Skeleton className="h-97 rounded-2xl" />
                            <Skeleton className="h-97 rounded-2xl" />
                        </div>
                    </div>
                ) : (
                    summary && (
                        <Dashboard
                            categoryData={categoryData}
                            trendData={trendData}
                            summary={summary}
                        />
                    )
                )}

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
                    <ReceiptTable data={receipts} />
                )}

            </div>
        </PageWrapper>
    )
}