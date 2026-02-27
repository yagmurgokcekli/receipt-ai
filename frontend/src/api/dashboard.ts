const BASE_URL = "http://localhost:8000"

export async function fetchCategoryDistribution(token: string) {
    const res = await fetch(`${BASE_URL}/api/dashboard/category-distribution`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    })
    return res.json()
}

export async function fetchMonthlyTrend(token: string) {
    const res = await fetch(`${BASE_URL}/api/dashboard/monthly-trend`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    })
    return res.json()
}

export async function fetchSummary(token: string) {
    const res = await fetch(`${BASE_URL}/api/dashboard/summary`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    })
    return res.json()
}