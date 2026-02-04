import { Navbar } from "@/components/layout/Navbar"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { UploadCard } from "@/components/upload/UploadCard"

function App() {
    return (
        <>
            <Navbar />
            <PageWrapper>
                <h1 className="text-center text-3xl font-bold mb-2">
                    Welcome to ReceiptAI
                </h1>
                <p className="text-center text-muted-foreground mb-6">
                    Upload your receipt to extract structured data.
                </p>
                <UploadCard />                
            </PageWrapper>
        </>
    )
}

export default App
