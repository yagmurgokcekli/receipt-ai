
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

export async function uploadReceipt(file: File): Promise<ReceiptResponse> {
    const formData = new FormData()

    formData.append("file", file)

    const response = await fetch(`http://127.0.0.1:8000/api/receipts`, {
        method: "POST",
        body: formData,
    })

    if (!response.ok) {
        throw new Error("Upload failed")
    }

    return response.json()
}
