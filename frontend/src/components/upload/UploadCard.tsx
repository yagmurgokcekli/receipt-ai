import { useMsal } from "@azure/msal-react";
import { loginRequest } from "@/auth/msalConfig";
import { uploadReceipt } from "@/api/receipt"
import { useEffect, useRef, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText } from "lucide-react"
import type { ReceiptResponse } from "@/api/receipt"
import { ResultCard } from "@/components/result/ResultCard"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import type { ReceiptMethod } from "@/api/receipt"
import {
    Field,
    FieldContent,
    FieldDescription,
    FieldLabel,
    FieldTitle,
} from "@/components/ui/field"

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

const ALLOWED_TYPES = [
    "image/jpeg",
    "image/png",
    "application/pdf",
]

export function UploadCard() {
    const [method, setMethod] = useState<ReceiptMethod>("di")

    const [result, setResult] = useState<ReceiptResponse | null>(null)
    const [isUploading, setIsUploading] = useState(false)

    const fileInputRef = useRef<HTMLInputElement | null>(null)
    const [file, setFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)

    const { instance } = useMsal();


    useEffect(() => {
        return () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl)
            }
        }
    }, [previewUrl])

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0]
        if (!selectedFile) return

        if (!ALLOWED_TYPES.includes(selectedFile.type)) {
            alert("Only JPG, PNG or PDF files are allowed.")
            return
        }

        if (selectedFile.size > MAX_FILE_SIZE) {
            alert("File size exceeds 10MB limit")
            return
        }

        setFile(selectedFile)

        if (previewUrl) {
            URL.revokeObjectURL(previewUrl)
        }

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
            const account = instance.getActiveAccount();

            if (!account) {
                alert("Not logged in");
                return;
            }

            const tokenResponse = await instance.acquireTokenSilent({
                ...loginRequest,
                account,
            });

            const token = tokenResponse.accessToken;

            const data = await uploadReceipt(file, method, token);

            setResult(data)
        } catch (error) {
            console.error("Upload failed:", error)
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
                    if (previewUrl) {
                        URL.revokeObjectURL(previewUrl)
                    }
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
                                <span className="underline">Click to upload</span> your receipt
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


                <div className="flex flex-col gap-3 px-5 py-4">
                    <div className="flex flex-col gap-3 p-5">
                        <div className="space-y-2">
                            <p className="text-sm font-medium text-center">Choose an Analysis Engine</p>

                            <RadioGroup
                                value={method}
                                onValueChange={(v) => setMethod(v as ReceiptMethod)}
                                className="space-y-0"
                            >
                                <FieldLabel htmlFor="di" className="block w-full">
                                    <Field orientation="horizontal" className="cursor-pointer hover:bg-muted/50">
                                        <FieldContent>
                                            <FieldTitle>Document Intelligence</FieldTitle>
                                            <FieldDescription>
                                                Fast & structured OCR analysis
                                            </FieldDescription>
                                        </FieldContent>
                                        <RadioGroupItem value="di" id="di" />
                                    </Field>
                                </FieldLabel>

                                <FieldLabel htmlFor="openai" className="block w-full">
                                    <Field orientation="horizontal" className="cursor-pointer hover:bg-muted/50">
                                        <FieldContent>
                                            <FieldTitle>OpenAI</FieldTitle>
                                            <FieldDescription>
                                                LLM-based semantic extraction
                                            </FieldDescription>
                                        </FieldContent>
                                        <RadioGroupItem value="openai" id="openai" />
                                    </Field>
                                </FieldLabel>

                                <FieldLabel htmlFor="compare" className="block w-full">
                                    <Field orientation="horizontal" className="cursor-pointer hover:bg-muted/50">
                                        <FieldContent>
                                            <FieldTitle>Compare</FieldTitle>
                                            <FieldDescription>
                                                DI vs OpenAI side-by-side
                                            </FieldDescription>
                                        </FieldContent>
                                        <RadioGroupItem value="compare" id="compare" />
                                    </Field>
                                </FieldLabel>
                            </RadioGroup>
                        </div>

                        <Button
                            onClick={handleUpload}
                            disabled={!file || isUploading}
                            className="min-w-[140px]"
                        >
                            {isUploading ? "Uploading..." : "Upload File"}
                        </Button>

                        {!file && (
                            <p className="text-xs text-muted-foreground text-center">
                                Supported formats: JPG, PNG, PDF (max 10MB)
                            </p>
                        )}
                        {method === "compare" && (
                            <p className="text-xs text-muted-foreground text-center">
                                Compare mode may take longer as multiple engines are used.
                            </p>
                        )}

                    </div>


                </div>
            </CardContent>
        </Card>
    )
}
