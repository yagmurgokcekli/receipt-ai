import { uploadReceipt } from "@/api/receipt"
import { useRef, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText } from "lucide-react"
import type { ReceiptResponse } from "@/api/receipt"
import { ResultCard } from "@/components/result/ResultCard"

export function UploadCard() {
    const [result, setResult] = useState<ReceiptResponse | null>(null)
    const [isUploading, setIsUploading] = useState(false)

    const fileInputRef = useRef<HTMLInputElement | null>(null)
    const [file, setFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0]
        if (!selectedFile) return

        setFile(selectedFile)

        if (selectedFile.type.startsWith("image/")) {
            setPreviewUrl(URL.createObjectURL(selectedFile))
        } else {
            setPreviewUrl(null)
        }
    }

    const handleUpload = async () => {
        if (!file) return

        try {
            setIsUploading(true)
            const data = await uploadReceipt(file)
            setResult(data)
        } catch {
            alert("Upload failed. Please try again.")
        } finally {
            setIsUploading(false)
        }
    }


    if (result) {
        return (
            <ResultCard
                result={result}
                onReset={() => {
                    setResult(null)
                    setFile(null)
                    setPreviewUrl(null)
                }}
            />
        )
    }


    return (
        <Card className="mt-8 max-w-xl mx-auto">
            <CardHeader>
                <CardTitle className="text-center">
                    Upload Your Receipt
                </CardTitle>
            </CardHeader>

            <CardContent>

                <div
                    onClick={() => fileInputRef.current?.click()}
                    className="
            flex cursor-pointer flex-col items-center justify-center gap-4
            rounded-lg border-2 border-dashed
            border-muted-foreground/30
            hover:border-muted-foreground/60
            p-10 text-center transition-colors
          "
                >
                    {!file && (
                        <>
                            <Upload className="h-8 w-8 text-muted-foreground" />
                            <p className="text-sm text-muted-foreground">
                                Drag & drop your receipt or{" "}
                                <span className="underline">click to upload</span>
                            </p>
                        </>
                    )}

                    {file && (
                        <>
                            {previewUrl ? (
                                <img
                                    src={previewUrl}
                                    alt="Receipt preview"
                                    className="max-h-48 rounded-md object-contain"
                                />
                            ) : (
                                <FileText className="h-10 w-10 text-muted-foreground" />
                            )}
                            <p className="text-sm font-medium">{file.name}</p>
                        </>
                    )}
                </div>


                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".jpg,.jpeg,.png,.pdf"
                    className="hidden"
                    onChange={handleFileSelect}
                />


                <div className="flex flex-col items-center gap-3 p-5">
                    <Button
                        onClick={handleUpload}
                        disabled={!file || isUploading}
                        className="min-w-[140px]"
                    >
                        {isUploading ? "Uploading..." : "Upload File"}
                    </Button>

                    {!file && (
                        <p className="text-xs text-muted-foreground">
                            Supported formats: JPG, PNG, PDF (max 10MB)
                        </p>
                    )}
                </div>
            </CardContent>
        </Card>
    )
}
