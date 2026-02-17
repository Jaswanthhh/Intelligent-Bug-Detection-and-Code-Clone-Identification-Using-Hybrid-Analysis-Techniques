"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { readFile } from "@/lib/api";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";

function FileViewerContent() {
    const searchParams = useSearchParams();
    const path = searchParams.get("path");
    const line = searchParams.get("line");
    const jobId = searchParams.get("job_id");
    const [content, setContent] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!path) return;
        setLoading(true);
        readFile(path)
            .then(res => setContent(res.content))
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, [path]);

    if (loading) return <div className="flex h-screen items-center justify-center bg-slate-950 text-white"><Loader2 className="animate-spin" /></div>;
    if (error) return <div className="flex h-screen items-center justify-center bg-slate-950 text-red-500">Error: {error}</div>;

    const language = path?.endsWith(".py") ? "python" : path?.endsWith(".java") ? "java" : "javascript";

    return (
        <div className="min-h-screen bg-slate-950 text-white p-6">
            <div className="max-w-7xl mx-auto space-y-4">
                <div className="flex items-center gap-4">
                    <Link href={jobId ? `/dashboard?job_id=${jobId}` : "/dashboard"}>
                        <Button variant="ghost" size="icon"><ArrowLeft /></Button>
                    </Link>
                    <h1 className="text-xl font-mono truncate">{path}</h1>
                </div>
                <div className="rounded-lg overflow-hidden border border-slate-800 text-sm">
                    <SyntaxHighlighter
                        language={language}
                        style={vscDarkPlus}
                        showLineNumbers
                        wrapLines
                        lineProps={(lineNumber) => {
                            const style: React.CSSProperties = { display: "block" };
                            if (line && parseInt(line) === lineNumber) {
                                style.backgroundColor = "rgba(239, 68, 68, 0.2)";
                                style.borderLeft = "4px solid #ef4444";
                            }
                            return { style };
                        }}
                    >
                        {content}
                    </SyntaxHighlighter>
                </div>
            </div>
        </div>
    );
}

export default function FileViewer() {
    return (
        <Suspense fallback={<div className="flex h-screen items-center justify-center bg-slate-950 text-white"><Loader2 className="animate-spin" /></div>}>
            <FileViewerContent />
        </Suspense>
    );
}
