import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import { useMsal } from "@azure/msal-react"
import { loginRequest } from "@/config/msalConfig"
import { fetchReceiptById, updateReceipt } from "@/api/receipt"
import type { ReceiptDetail } from "@/api/receipt"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Loader2, Trash2 } from "lucide-react"
import { deleteReceipt } from "@/api/receipt"
import { useNavigate } from "react-router-dom"
import { Plus } from "lucide-react"

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

import {
    AlertDialog,
    AlertDialogTrigger,
    AlertDialogContent,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogCancel,
    AlertDialogAction,
} from "@/components/ui/alert-dialog"


import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"

import { toast } from "sonner"
import { Skeleton } from "@/components/ui/skeleton"

export default function ReceiptDetailPage() {

    const categories = [
        "Food",
        "Fuel",
        "Electronics",
        "Clothing",
        "Health",
        "Transport",
        "Entertainment",
        "Other",
    ]

    const { id } = useParams()
    const { instance } = useMsal()
    const navigate = useNavigate()

    const [deleting, setDeleting] = useState(false)
    const [receipt, setReceipt] = useState<ReceiptDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [isEditing, setIsEditing] = useState(false)

    const getToken = async () => {
        const account = instance.getActiveAccount()

        if (!account) {
            throw new Error("No active account")
        }

        const response = await instance.acquireTokenSilent({
            scopes: ["User.Read"],
            account,
        })

        return response.accessToken
    }

    useEffect(() => {
        const loadReceipt = async () => {
            try {
                const account = instance.getActiveAccount()
                if (!account || !id) return

                const tokenResponse = await instance.acquireTokenSilent({
                    ...loginRequest,
                    account,
                })

                const data = await fetchReceiptById(
                    Number(id),
                    tokenResponse.accessToken
                )

                setReceipt(data)
            } catch (err) {
                console.error("Failed to load receipt:", err)
            } finally {
                setLoading(false)
            }
        }

        loadReceipt()
    }, [id, instance])

    const handleSave = async () => {
        console.log("Receipt:", receipt)
        if (!receipt || !receipt.id) {
            toast.error("Invalid receipt data")
            return
        }
        console.log("Receipt:", receipt)
        try {
            setSaving(true)

            const token = await getToken()

            const { id, blob_url, ...payload } = receipt

            await updateReceipt(id, payload, token)

            toast.success("Saved successfully")

            setIsEditing(false)

        } catch (err) {
            toast.error("Update failed")
        } finally {
            setSaving(false)
        }
    }

    const handleDelete = async () => {
        if (!receipt?.id) return

        try {
            setDeleting(true)

            const token = await getToken()
            await deleteReceipt(receipt.id, token)

            toast.success("Receipt deleted")

            navigate("/")
        } catch (err) {
            toast.error("Delete failed")
        } finally {
            setDeleting(false)
        }
    }

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto p-8">
                <div className="grid grid-cols-1 lg:grid-cols-6 gap-8">

                    {/* left side skeleton */}
                    <Card className="lg:col-span-2 h-[calc(100vh-200px)]">
                        <CardContent className="p-6 space-y-4">
                            <Skeleton className="w-full h-full rounded-xl" />
                        </CardContent>
                    </Card>

                    {/* right side skeleton */}
                    <Card className="lg:col-span-4">

                        <CardHeader className="flex flex-row items-center justify-between">
                            <Skeleton className="h-6 w-40" />

                            <div className="flex gap-3">
                                <Skeleton className="h-8 w-16 rounded-md" />
                                <Skeleton className="h-8 w-8 rounded-md" />
                            </div>
                        </CardHeader>

                        <CardContent className="p-6 space-y-6">

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <Skeleton className="h-16 rounded-xl" />
                                <Skeleton className="h-16 rounded-xl" />
                                <Skeleton className="h-16 rounded-xl" />
                                <Skeleton className="h-16 rounded-xl" />
                            </div>

                            <div className="space-y-3 pt-4">
                                <Skeleton className="h-8 w-full" />
                                <Skeleton className="h-8 w-full" />
                                <Skeleton className="h-8 w-full" />
                                <Skeleton className="h-8 w-full" />
                            </div>

                        </CardContent>
                    </Card>

                </div>
            </div>
        )
    }

    if (!receipt) {
        return <div className="p-10">Receipt not found</div>
    }

    return (
        <div className="max-w-7xl mx-auto p-8">
            <div className="grid grid-cols-1 lg:grid-cols-6 gap-8">


                <Card className="lg:col-span-2 h-[calc(100vh-200px)]">
                    <CardContent className="p-4 h-full">
                        <div className="h-full flex items-center justify-center overflow-hidden rounded-md bg-muted/20">

                            {receipt?.blob_url && (
                                <img
                                    src={receipt.blob_url}
                                    alt="Receipt"
                                    className="h-full w-full object-contain"
                                />
                            )}

                        </div>
                    </CardContent>
                </Card>

                {/* right side */}
                <Card className="lg:col-span-4">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>Receipt Analysis</CardTitle>

                        <div className="flex items-center gap-3">

                            {!isEditing && (
                                <>
                                    <Button
                                        size="sm"
                                        onClick={() => setIsEditing(true)}
                                        className="bg-white text-black hover:bg-white/90"
                                    >
                                        Edit
                                    </Button>

                                    <AlertDialog>
                                        <AlertDialogTrigger asChild>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="text-destructive hover:text-destructive"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </AlertDialogTrigger>

                                        <AlertDialogContent>
                                            <AlertDialogHeader>
                                                <AlertDialogTitle>
                                                    Are you sure you want to delete this receipt?
                                                </AlertDialogTitle>
                                                <AlertDialogDescription>
                                                    This action cannot be undone.
                                                </AlertDialogDescription>
                                            </AlertDialogHeader>

                                            <AlertDialogFooter>
                                                <AlertDialogCancel>
                                                    Cancel
                                                </AlertDialogCancel>

                                                <AlertDialogAction
                                                    disabled={deleting}
                                                    onClick={async (e) => {
                                                        e.preventDefault()
                                                        await handleDelete()
                                                    }}
                                                    className="bg-destructive text-white hover:bg-destructive/90 min-w-22.5"
                                                >
                                                    {deleting ? (
                                                        <Loader2 className="h-4 w-4 animate-spin mx-auto" />
                                                    ) : (
                                                        "Delete"
                                                    )}
                                                </AlertDialogAction>
                                            </AlertDialogFooter>
                                        </AlertDialogContent>
                                    </AlertDialog>
                                </>
                            )}

                            {isEditing && (
                                <>
                                    <Button
                                        variant="secondary"
                                        size="sm"
                                        onClick={() => setIsEditing(false)}
                                    >
                                        Cancel
                                    </Button>

                                    <Button
                                        onClick={handleSave}
                                        disabled={saving}
                                        size="sm"
                                        className="bg-white text-black hover:bg-white/90 min-w-22.5"
                                    >
                                        {saving ? (
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                        ) : (
                                            "Save"
                                        )}
                                    </Button>
                                </>
                            )}
                        </div>
                    </CardHeader>

                    <CardContent className="space-y-6">

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">

                            <div>
                                <p className="text-muted-foreground">Merchant</p>

                                {isEditing ? (
                                    <Input
                                        value={receipt.merchant ?? ""}
                                        onChange={(e) =>
                                            setReceipt({
                                                ...receipt,
                                                merchant: e.target.value,
                                            })
                                        }
                                    />
                                ) : (
                                    <p className="font-medium">
                                        {receipt.merchant ?? "-"}
                                    </p>
                                )}
                            </div>

                            <div>
                                <p className="text-muted-foreground">Date</p>

                                {isEditing ? (
                                    <Input
                                        type="date"
                                        value={receipt.transaction_date ?? ""}
                                        onChange={(e) =>
                                            setReceipt({
                                                ...receipt,
                                                transaction_date: e.target.value,
                                            })
                                        }
                                    />
                                ) : (
                                    <p className="font-medium">
                                        {receipt.transaction_date ?? "-"}
                                    </p>
                                )}
                            </div>

                            <div>
                                <p className="text-muted-foreground">Total</p>

                                {isEditing ? (
                                    <Input
                                        type="number"
                                        value={receipt.total ?? ""}
                                        onChange={(e) =>
                                            setReceipt({
                                                ...receipt,
                                                total: Number(e.target.value),
                                            })
                                        }
                                    />
                                ) : (
                                    <p className="font-medium">
                                        {receipt.total} {receipt.currency}
                                    </p>
                                )}
                            </div>

                            <div>
                                <p className="text-muted-foreground">Source</p>
                                <Badge variant="secondary">
                                    {receipt.source}
                                </Badge>
                            </div>
                        </div>

                        <div>
                            <h3 className="font-medium mb-2">Items</h3>

                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Item</TableHead>
                                        <TableHead>Category</TableHead>
                                        <TableHead className="text-right">Quantity</TableHead>
                                        <TableHead className="text-right">Line Total</TableHead>
                                    </TableRow>
                                </TableHeader>

                                <TableBody>
                                    {receipt.items?.map((item, index) => (
                                        <TableRow key={index}>

                                            <TableCell>
                                                {isEditing ? (
                                                    <Input
                                                        value={item.name}
                                                        onChange={(e) => {
                                                            const updated = [...receipt.items]
                                                            updated[index].name = e.target.value
                                                            setReceipt({
                                                                ...receipt,
                                                                items: updated,
                                                            })
                                                        }}
                                                    />
                                                ) : (
                                                    item.name
                                                )}
                                            </TableCell>

                                            <TableCell>
                                                {isEditing ? (
                                                    <Select
                                                        value={item.category ?? "Other"}
                                                        onValueChange={(value) => {
                                                            const updatedItems = [...receipt.items]
                                                            updatedItems[index] = {
                                                                ...updatedItems[index],
                                                                category: value,
                                                            }

                                                            setReceipt({
                                                                ...receipt,
                                                                items: updatedItems,
                                                            })
                                                        }}
                                                    >
                                                        <SelectTrigger className="w-35">
                                                            <SelectValue />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            {categories.map((cat) => (
                                                                <SelectItem key={cat} value={cat}>
                                                                    {cat}
                                                                </SelectItem>
                                                            ))}
                                                        </SelectContent>
                                                    </Select>
                                                ) : (
                                                    <Badge variant="secondary">
                                                        {item.category ?? "Uncategorized"}
                                                    </Badge>
                                                )}
                                            </TableCell>

                                            <TableCell className="text-right">
                                                {isEditing ? (
                                                    <Input
                                                        type="number"
                                                        value={item.quantity}
                                                        onChange={(e) => {
                                                            const updated = [...receipt.items]
                                                            updated[index].quantity = Number(e.target.value)
                                                            setReceipt({
                                                                ...receipt,
                                                                items: updated,
                                                            })
                                                        }}
                                                    />
                                                ) : (
                                                    item.quantity
                                                )}
                                            </TableCell>

                                            <TableCell className="text-right">
                                                {isEditing ? (
                                                    <Input
                                                        type="number"
                                                        value={item.price}
                                                        onChange={(e) => {
                                                            const updated = [...receipt.items]
                                                            updated[index].price = Number(e.target.value)
                                                            setReceipt({
                                                                ...receipt,
                                                                items: updated,
                                                            })
                                                        }}
                                                    />
                                                ) : (
                                                    <>
                                                        {item.price} {receipt.currency}
                                                    </>
                                                )}
                                            </TableCell>

                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                        <div className="flex justify-center pt-8">
                            <Button
                                variant="outline"
                                onClick={() => navigate("/upload")}
                                className="gap-2"
                            >
                                <Plus className="h-4 w-4" />
                                Upload another receipt
                            </Button>
                        </div>

                    </CardContent>
                </Card>

            </div>
        </div>
    )
}