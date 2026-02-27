import {
    flexRender,
    getCoreRowModel,
    useReactTable,
    type ColumnDef,
} from "@tanstack/react-table"

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"

import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Trash2, Pencil, Check, X } from "lucide-react"

import type { ReceiptListItem, ReceiptAnalysis } from "@/api/receipt"
import { updateReceipt } from "@/api/receipt"
import { useMsal } from "@azure/msal-react"
import { useState } from "react"
import { Loader2 } from "lucide-react"

interface Props {
    data: ReceiptListItem[]
    onDelete: (id: number) => void
    onUpdateLocal: (updated: ReceiptListItem) => void
}

export function ReceiptTable({ data, onDelete, onUpdateLocal }: Props) {
    const { instance, accounts } = useMsal()
    const [savingId, setSavingId] = useState<number | null>(null)
    const [deletingId, setDeletingId] = useState<number | null>(null)

    const [editingId, setEditingId] = useState<number | null>(null)
    const [form, setForm] = useState<{
        merchant: string
        total: string
    }>({ merchant: "", total: "" })

    const getToken = async () => {
        const response = await instance.acquireTokenSilent({
            scopes: ["User.Read"],
            account: accounts[0],
        })
        return response.accessToken
    }

    const handleSave = async (row: ReceiptListItem) => {
        try {
            const token = await getToken()

            const payload: ReceiptAnalysis = {
                merchant: form.merchant || null,
                total: form.total === "" ? null : Number(form.total),
                currency: row.currency,
                transaction_date: row.transaction_date,
                items: [],
                source: row.source,
            }

            await updateReceipt(row.id, payload, token)

            onUpdateLocal({
                ...row,
                merchant: payload.merchant,
                total: payload.total,
            })

            setEditingId(null)
        } catch (err) {
            console.error(err)
        }
    }

    const columns: ColumnDef<ReceiptListItem>[] = [
        {
            accessorKey: "merchant",
            header: "Merchant",
        },
        {
            accessorKey: "transaction_date",
            header: "Date",
        },
        {
            accessorKey: "total",
            header: "Amount",
            cell: ({ row }) => (
                <div className="font-semibold">
                    {row.original.total ?? "-"} {row.original.currency ?? ""}
                </div>
            ),
        },
        {
            accessorKey: "source",
            header: "Engine",
        },
        {
            id: "actions",
            header: "",
        },
    ]

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
    })

    return (
        <div className="rounded-md border overflow-hidden">
            <Table>
                <TableHeader>
                    {table.getHeaderGroups().map((headerGroup) => (
                        <TableRow key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                                <TableHead key={header.id}>
                                    {flexRender(
                                        header.column.columnDef.header,
                                        header.getContext()
                                    )}
                                </TableHead>
                            ))}
                        </TableRow>
                    ))}
                </TableHeader>

                <TableBody>
                    {data.map((row) => {
                        const isEditing = editingId === row.id

                        if (isEditing) {
                            return (
                                <TableRow key={row.id}>
                                    <TableCell>
                                        <Input
                                            value={form.merchant}
                                            onChange={(e) =>
                                                setForm({ ...form, merchant: e.target.value })
                                            }
                                        />
                                    </TableCell>

                                    <TableCell>{row.transaction_date}</TableCell>

                                    <TableCell>
                                        <Input
                                            type="number"
                                            value={form.total}
                                            onChange={(e) =>
                                                setForm({ ...form, total: e.target.value })
                                            }
                                        />
                                    </TableCell>

                                    <TableCell>{row.source}</TableCell>

                                    <TableCell className="flex gap-2 justify-end">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            disabled={savingId === row.id}
                                            onClick={async () => {
                                                setSavingId(row.id)
                                                await handleSave(row)
                                                setSavingId(null)
                                            }}
                                        >
                                            {savingId === row.id ? (
                                                <Loader2 className="h-4 w-4 animate-spin text-green-600" />
                                            ) : (
                                                <Check className="h-4 w-4 text-green-600" />
                                            )}
                                        </Button>

                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={() => setEditingId(null)}
                                        >
                                            <X className="h-4 w-4 text-muted-foreground" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            )
                        }

                        return (
                            <TableRow key={row.id}>
                                <TableCell>{row.merchant}</TableCell>
                                <TableCell>{row.transaction_date}</TableCell>
                                <TableCell>
                                    {row.total ?? "-"} {row.currency ?? ""}
                                </TableCell>
                                <TableCell>{row.source}</TableCell>

                                <TableCell className="flex gap-2 justify-end">
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => {
                                            setEditingId(row.id)
                                            setForm({
                                                merchant: row.merchant ?? "",
                                                total: row.total?.toString() ?? "",
                                            })
                                        }}
                                    >
                                        <Pencil className="h-4 w-4" />
                                    </Button>

                                    <AlertDialog>
                                        <AlertDialogTrigger asChild>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="text-destructive"
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
                                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                                <AlertDialogAction
                                                    disabled={deletingId === row.id}
                                                    onClick={async (e) => {
                                                        e.preventDefault() // dialog auto-close olmasın

                                                        setDeletingId(row.id)

                                                        try {
                                                            await onDelete(row.id)
                                                        } finally {
                                                            setDeletingId(null)
                                                        }
                                                    }}
                                                    className="bg-destructive text-white hover:bg-destructive/90 min-w-22.5"
                                                >
                                                    {deletingId === row.id ? (
                                                        <Loader2 className="h-4 w-4 animate-spin mx-auto" />
                                                    ) : (
                                                        "Delete"
                                                    )}
                                                </AlertDialogAction>
                                            </AlertDialogFooter>
                                        </AlertDialogContent>
                                    </AlertDialog>
                                </TableCell>
                            </TableRow>
                        )
                    })}
                </TableBody>
            </Table>
        </div>
    )
}