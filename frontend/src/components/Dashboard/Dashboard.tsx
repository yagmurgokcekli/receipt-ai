import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    ResponsiveContainer,
} from "recharts"

interface DashboardProps {
    categoryData: any[]
    trendData: any[]
    summary: any
}

const COLORS = [
    "#6366F1",
    "#22C55E",
    "#F59E0B",
    "#EF4444",
    "#3B82F6",
    "#A855F7",
]

const formatCurrency = (value: number) =>
    new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(value)

export function Dashboard({
    categoryData,
    trendData,
    summary,
}: DashboardProps) {
    return (
        <div className="space-y-10">

            <div className="grid grid-cols-3 gap-6">
                <div className="p-6 rounded-2xl shadow bg-white dark:bg-zinc-900">
                    <p className="text-sm text-muted-foreground">This Month</p>
                    <h3 className="text-2xl font-bold">
                        ${formatCurrency(summary.current_month_total)}
                    </h3>
                    <p
                        className={`text-sm ${summary.percent_change >= 0
                                ? "text-green-500"
                                : "text-red-500"
                            }`}
                    >
                        {summary.percent_change}% vs last month
                    </p>
                </div>

                <div className="p-6 rounded-2xl shadow bg-white dark:bg-zinc-900">
                    <p className="text-sm text-muted-foreground">Top Category</p>
                    <h3 className="text-2xl font-bold">
                        {summary.top_category || "—"}
                    </h3>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-8">

                <div className="p-6 rounded-2xl shadow bg-white dark:bg-zinc-900">
                    <div className="flex items-center justify-between mb-4">
                        <h4 className="font-semibold">
                            Spending by Category
                        </h4>

                    </div>

                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={categoryData}
                                dataKey="total"
                                nameKey="category"
                                outerRadius={100}
                                label={({ value }) =>
                                    typeof value === "number"
                                        ? `$${formatCurrency(value)}`
                                        : ""
                                }
                            >
                                {categoryData.map((_, index) => (
                                    <Cell
                                        key={index}
                                        fill={COLORS[index % COLORS.length]}
                                    />
                                ))}
                            </Pie>

                            <Tooltip
                                formatter={(value) =>
                                    typeof value === "number"
                                        ? `$${formatCurrency(value)}`
                                        : "-"
                                }
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                <div className="p-6 rounded-2xl shadow bg-white dark:bg-zinc-900">
                    <h4 className="mb-4 font-semibold">Monthly Trend</h4>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={trendData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis
                                tickFormatter={(value) =>
                                    `$${formatCurrency(value)}`
                                }
                            />
                            <Tooltip
                                formatter={(value) =>
                                    typeof value === "number"
                                        ? `$${formatCurrency(value)}`
                                        : "-"
                                }
                            />
                            <Line
                                type="monotone"
                                dataKey="total"
                                stroke="#6366F1"
                                strokeWidth={3}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

            </div>
        </div>
    )
}