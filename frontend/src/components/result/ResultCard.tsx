import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import type { ReceiptResponse } from "@/api/receipt"

interface ResultCardProps {
    result: ReceiptResponse
    onReset: () => void
}

export function ResultCard({ result, onReset }: ResultCardProps) {
    const { analysis } = result

    return (
        <Card className="mt-8 max-w-4xl mx-auto">
            <CardHeader>
                <CardTitle className="text-center">
                    Receipt Analysis
                </CardTitle>
            </CardHeader>

            <CardContent className="space-y-6">
               
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                        <p className="text-muted-foreground">Merchant</p>
                        <p className="font-medium">{analysis.merchant ?? "-"}</p>
                    </div>

                    <div>
                        <p className="text-muted-foreground">Date</p>
                        <p className="font-medium">
                            {analysis.transaction_date ?? "-"}
                        </p>
                    </div>

                    <div>
                        <p className="text-muted-foreground">Total</p>
                        <p className="font-medium">
                            {analysis.total} {analysis.currency}
                        </p>
                    </div>

                    <div>
                        <p className="text-muted-foreground">Source</p>
                        <Badge variant="secondary">
                            {analysis.source}
                        </Badge>
                    </div>
                </div>

                
                <div>
                    <h3 className="font-medium mb-2">Items</h3>

                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Item</TableHead>
                                <TableHead className="text-right">Quantity</TableHead>
                                <TableHead className="text-right">Line Total</TableHead>
                            </TableRow>
                        </TableHeader>

                        <TableBody>
                            {analysis.items.map((item, index) => (
                                <TableRow key={index}>
                                    <TableCell>{item.name}</TableCell>
                                    <TableCell className="text-right">
                                        {item.quantity}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        {item.price} {analysis.currency}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>

                
                <div className="flex justify-center pt-4">
                    <Button variant="outline" onClick={onReset}>
                        Upload another receipt
                    </Button>
                </div>
            </CardContent>
        </Card>
    )
}
