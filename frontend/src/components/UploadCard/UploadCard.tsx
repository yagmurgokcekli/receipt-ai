import { useMsal } from "@azure/msal-react";
import { loginRequest } from "@/config/msalConfig";
import { uploadReceipt } from "@/api/receipt"
import { useEffect, useRef, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText } from "lucide-react"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import type { ReceiptMethod } from "@/api/receipt"
import {
    Field,
    FieldContent,
    FieldDescription,
    FieldLabel,
    FieldTitle,
} from "@/components/ui/field"
import { Spinner } from "@/components/ui/spinner"
import { useNavigate } from "react-router-dom"

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

const ALLOWED_TYPES = [
    "image/jpeg",
    "image/png",
    "application/pdf",
]


export function UploadCard() {
    const [method, setMethod] = useState<ReceiptMethod>("di")

    const [isUploading, setIsUploading] = useState(false)

    const fileInputRef = useRef<HTMLInputElement | null>(null)
    const [file, setFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)

    const { instance } = useMsal();

    const navigate = useNavigate()

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
                await instance.loginRedirect(loginRequest);
                return;
            }

            const tokenResponse = await instance.acquireTokenSilent({
                ...loginRequest,
                account,
            });

            const token = tokenResponse.accessToken;

            const data = await uploadReceipt(file, method, token);
            navigate(`/receipts/${data.id}`)
        } catch (error) {
            console.error("Upload failed:", error)
            alert("Upload failed. Please try again.")
        } finally {
            setIsUploading(false)
        }
    }

    return (
        <Card className="max-w-xl mx-auto">
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
                            </RadioGroup>
                        </div>

                        <Button
                            onClick={handleUpload}
                            disabled={!file || isUploading}
                            className="
                                min-w-40
                                gap-2
                                bg-black text-white hover:bg-black/90
                                dark:bg-white dark:text-black dark:hover:bg-white/90
                            "
                        >
                            {isUploading ? (
                                <>
                                    <Spinner className="h-4 w-4" />
                                </>
                            ) : (
                                "Upload File"
                            )}
                        </Button>

                        {!file && (
                            <p className="text-xs text-muted-foreground text-center">
                                Supported formats: JPG, PNG, PDF (max 10MB)
                            </p>
                        )}

                    </div>


                </div>
            </CardContent>
        </Card>
    )
}
