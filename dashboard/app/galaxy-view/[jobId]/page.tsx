"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation"; // No useSearchParams needed
import { getStatus } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2, Sparkles } from "lucide-react";
import CodeGalaxy from "@/components/code-galaxy";

export default function GalaxyPage(props: { params: Promise<{ jobId: string }> }) {
    const params = use(props.params);
    const router = useRouter();
    const jobId = params.jobId;
    const [status, setStatus] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!jobId) {
            setLoading(false);
            return;
        }

        getStatus(jobId).then((res) => {
            setStatus(res);
            setLoading(false);
        }).catch((err) => {
            console.error(err);
            setLoading(false);
        });
    }, [jobId]);

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center text-purple-500">
                <Loader2 className="w-8 h-8 animate-spin" />
            </div>
        );
    }

    if (!status || !status.result) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">
                <p>Job not ready or failed.</p>
                <Button onClick={() => router.push('/')} variant="link" className="text-purple-400">Go Home</Button>
            </div>
        );
    }

    // Flatten file list for the visualizer
    // Handle both CLI (flat) and API (nested) response structures
    const flatFiles = status.result.static || status.result.static_analysis?.files || [];
    const fusionReports = status.result.reports || status.result.fusion_reports?.reports || [];
    const allBugs = status.result.bugs || status.result.bug_detection?.bugs || [];

    if (flatFiles.length === 0) {
        return (
            <div className="w-full h-screen bg-slate-950 flex flex-col items-center justify-center text-white space-y-4">
                <div className="bg-slate-900/50 p-8 rounded-full border border-slate-800">
                    <Sparkles className="w-16 h-16 text-slate-700" />
                </div>
                <h2 className="text-2xl font-bold">The Galaxy is Empty</h2>
                <p className="text-slate-400 max-w-md text-center">
                    No analysis results found in memory. You need to run an analysis on a codebase to populate the visualization.
                </p>
                <div className="flex gap-4">
                    <Button onClick={() => router.push('/')} variant="outline">
                        Go to Dashboard
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full h-screen bg-black relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 z-10 p-6 flex justify-between items-start pointer-events-none">
                <div className="pointer-events-auto">
                    <Button
                        onClick={() => router.back()}
                        variant="ghost"
                        className="text-white hover:bg-white/10 gap-2 mb-2"
                    >
                        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
                    </Button>
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600 flex items-center gap-3">
                        Code Topology 3D
                    </h1>
                    <p className="text-slate-400 text-sm mt-1 max-w-md">
                        Visualizing {flatFiles.length} files, {fusionReports.length} clones, and {allBugs.length} bugs.
                    </p>
                </div>

                <div className="bg-slate-900/80 backdrop-blur border border-slate-700 p-4 rounded-lg text-xs space-y-2 text-slate-300 pointer-events-auto">
                    <div className="font-bold text-white mb-1">Legend</div>
                    <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-blue-500"></span> Python File</div>
                    <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-purple-500"></span> Java/Other File</div>
                    <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></span> Bug Detected</div>
                    <div className="flex items-center gap-2"><span className="w-8 h-0.5 bg-green-400 opacity-50"></span> Clone Link</div>
                </div>
            </div>

            <CodeGalaxy files={flatFiles} clones={fusionReports} bugs={allBugs} />
        </div>
    );
}
