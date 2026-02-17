"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { analyzeCode } from "@/lib/api";
import { Loader2, Sparkles, Code2, ShieldCheck, Zap, FolderOpen, Settings } from "lucide-react";
import { motion } from "framer-motion";
import { FilePicker } from "@/components/file-picker";

export default function Home() {
  const [paths, setPaths] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilePicker, setShowFilePicker] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [inputMode, setInputMode] = useState<"local" | "github">("local");
  const [githubUrl, setGithubUrl] = useState("");
  const router = useRouter();

  const handleAnalyze = async () => {
    if (inputMode === "local" && paths.length === 0) return;
    if (inputMode === "github" && !githubUrl) return;

    setLoading(true);
    try {
      const res = await analyzeCode(paths, inputMode === "github" ? githubUrl : undefined);
      if (res.job_id) {
        router.push(`/dashboard?job_id=${res.job_id}`);
      }
    } catch (error) {
      console.error("Analysis failed", error);
      alert("Failed to start analysis. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  // ... (settings code)

  return (
    <main className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-slate-950 text-white selection:bg-purple-500/30">
      {/* ... (background and settings modal) */}

      {/* File Picker Modal */}
      {showFilePicker && (
        <FilePicker
          initialPath={paths[0] || "."}
          onSelect={(selectedPaths) => {
            setPaths(selectedPaths);
            setShowFilePicker(false);
          }}
          onCancel={() => setShowFilePicker(false)}
        />
      )}

      <div className="z-10 w-full max-w-5xl px-6">
        {/* ... (nav) */}

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* ... (left column) */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            {/* ... (content) */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              <span>New: Multi-File Analysis</span>
            </div>

            <h1 className="text-5xl lg:text-7xl font-bold tracking-tight leading-tight">
              Secure your code <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 animate-gradient">
                before it breaks.
              </span>
            </h1>

            <p className="text-lg text-slate-400 max-w-lg leading-relaxed">
              Advanced hybrid analysis engine. Detect semantic clones, logic errors, and security vulnerabilities in seconds.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <ShieldCheck className="w-4 h-4 text-green-500" />
                <span>Enterprise Grade</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Zap className="w-4 h-4 text-yellow-500" />
                <span>Real-time Analysis</span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl blur-2xl opacity-20"></div>
            <Card className="relative border-slate-800 bg-slate-900/50 backdrop-blur-xl shadow-2xl">
              <CardHeader>
                <CardTitle className="text-white">Start Analysis</CardTitle>
                <CardDescription className="text-slate-400">
                  Select files or folders to begin.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Input Mode Tabs */}
                <div className="flex p-1 bg-slate-950 rounded-lg mb-4">
                  <button
                    onClick={() => setInputMode("local")}
                    className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-md text-sm font-medium transition-all ${inputMode === "local" ? "bg-slate-800 text-white shadow-sm" : "text-slate-500 hover:text-slate-300"}`}
                  >
                    <FolderOpen className="w-4 h-4" /> Local Files
                  </button>
                  <button
                    onClick={() => setInputMode("github")}
                    className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-md text-sm font-medium transition-all ${inputMode === "github" ? "bg-slate-800 text-white shadow-sm" : "text-slate-500 hover:text-slate-300"}`}
                  >
                    {/* Github Icon SVG inline */}
                    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" /></svg>
                    GitHub Repo
                  </button>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                    {inputMode === "local" ? "Selected Paths" : "Repository URL"}
                  </label>

                  {inputMode === "local" ? (
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Select files..."
                        readOnly
                        className="flex h-12 w-full rounded-lg border border-slate-800 bg-slate-950/50 px-4 py-2 text-sm text-white placeholder:text-slate-600 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none transition-all cursor-pointer"
                        value={paths.length > 0 ? `${paths.length} items selected` : ""}
                        onClick={() => setShowFilePicker(true)}
                      />
                      <Button
                        onClick={() => setShowFilePicker(true)}
                        className="h-12 w-12 bg-slate-800 hover:bg-slate-700 border border-slate-700"
                      >
                        <FolderOpen className="w-5 h-5 text-purple-400" />
                      </Button>
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="https://github.com/username/repo"
                        className="flex h-12 w-full rounded-lg border border-slate-800 bg-slate-950/50 px-4 py-2 text-sm text-white placeholder:text-slate-600 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none transition-all"
                        value={githubUrl}
                        onChange={(e) => setGithubUrl(e.target.value)}
                      />
                    </div>
                  )}

                  {inputMode === "local" && paths.length > 0 && (
                    <div className="text-xs text-slate-500 max-h-20 overflow-y-auto">
                      {paths.map((p, i) => <div key={i} className="truncate">{p}</div>)}
                    </div>
                  )}
                </div>
                <Button
                  onClick={handleAnalyze}
                  disabled={loading || (inputMode === "local" && paths.length === 0) || (inputMode === "github" && !githubUrl)}
                  className="w-full h-12 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-medium text-lg shadow-lg shadow-purple-500/25 transition-all hover:scale-[1.02]"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      {inputMode === "github" ? "Cloning & Analyzing..." : "Initializing Engine..."}
                    </>
                  ) : (
                    "Launch Inspector"
                  )}
                </Button>
                <p className="text-xs text-center text-slate-600">
                  Supports Python, Java, JS, C++.
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </main>
  );
}
