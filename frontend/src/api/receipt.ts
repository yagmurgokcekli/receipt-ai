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
