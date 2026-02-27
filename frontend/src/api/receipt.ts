export type ReceiptMethod = "di" | "openai" | "compare"

export interface ReceiptAnalysis {
    merchant: string | null
    total: number | null
    currency: string | null
    transaction_date: string | null
    items: {
        name: string
        quantity: number
        price: number
    }[]
    source: string
}

export interface ReceiptResponse {
    file_saved_as: string
    blob_url: string
    method: string
    analysis: ReceiptAnalysis
}

export async function uploadReceipt(
    file: File,
    method: ReceiptMethod,
    token: string
): Promise<ReceiptResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const apiBaseUrl =
        import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

    const response = await fetch(
        `${apiBaseUrl}/api/receipts?method=${method}`,
        {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`,
            },
            body: formData,
        }
    );

    if (!response.ok) {
        throw new Error("Upload failed");
    }

    return response.json();
}


export interface ReceiptListItem {
    id: number
    merchant: string | null
    total: number | null
    currency: string | null
    transaction_date: string | null
    source: string
    created_at: string
}

export async function fetchReceipts(
    token: string
): Promise<ReceiptListItem[]> {
    const apiBaseUrl =
        import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

    const response = await fetch(
        `${apiBaseUrl}/api/receipts`,
        {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }
    );

    if (!response.ok) {
        throw new Error("Failed to fetch receipts");
    }

    return response.json();
}

export async function deleteReceipt(
    receiptId: number,
    token: string
): Promise<void> {
    const apiBaseUrl =
        import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

    const response = await fetch(
        `${apiBaseUrl}/api/receipts/${receiptId}`,
        {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }
    );

    if (!response.ok) {
        throw new Error("Failed to delete receipt");
    }
}

export async function updateReceipt(
    receiptId: number,
    data: ReceiptAnalysis,
    token: string
): Promise<ReceiptAnalysis> {
    const apiBaseUrl =
        import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

    const response = await fetch(
        `${apiBaseUrl}/api/receipts/${receiptId}`,
        {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(data),
        }
    );

    if (!response.ok) {
        throw new Error("Failed to update receipt");
    }

    return response.json();
}