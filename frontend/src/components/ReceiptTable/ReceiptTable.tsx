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


import type { ReceiptListItem } from "@/api/receipt"
import { useNavigate } from "react-router-dom"


interface Props {
    data: ReceiptListItem[]
}

export function ReceiptTable({ data }: Props) {
    const navigate = useNavigate()

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
                    {table.getRowModel().rows.map((row) => (
                        <TableRow
                            key={row.id}
                            className="cursor-pointer hover:bg-accent/40"
                            onClick={() =>
                                navigate(`/receipts/${row.original.id}`)
                            }
                        >
                            {row.getVisibleCells().map((cell) => (
                                <TableCell key={cell.id}>
                                    {flexRender(
                                        cell.column.columnDef.cell,
                                        cell.getContext()
                                    )}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}