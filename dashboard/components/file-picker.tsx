"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Folder, File, ChevronUp, Loader2, CheckSquare, Square } from "lucide-react";

interface FilePickerProps {
    onSelect: (paths: string[]) => void;
    onCancel: () => void;
    initialPath?: string;
}

export function FilePicker({ onSelect, onCancel, initialPath = "." }: FilePickerProps) {
    const [currentPath, setCurrentPath] = useState(initialPath);
    const [items, setItems] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedPaths, setSelectedPaths] = useState<Set<string>>(new Set());

    useEffect(() => {
        fetchItems(currentPath);
    }, [currentPath]);

    const fetchItems = async (path: string) => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/fs/list?path=${encodeURIComponent(path)}`);
            const data = await res.json();
            if (data.items) {
                setItems(data.items);
                setCurrentPath(data.current_path);
            }
        } catch (e) {
            console.error("Failed to list files", e);
        } finally {
            setLoading(false);
        }
    };

    const handleNavigate = (item: any) => {
        if (item.is_dir && item.name !== "..") {
            fetchItems(item.path);
        } else if (item.name === "..") {
            fetchItems(item.path);
        }
    };

    const toggleSelection = (e: React.MouseEvent, path: string) => {
        e.stopPropagation();
        const newSelected = new Set(selectedPaths);
        if (newSelected.has(path)) {
            newSelected.delete(path);
        } else {
            newSelected.add(path);
        }
        setSelectedPaths(newSelected);
    };

    const handleSelectCurrent = () => {
        // If nothing selected, select current folder
        if (selectedPaths.size === 0) {
            onSelect([currentPath]);
        } else {
            onSelect(Array.from(selectedPaths));
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <Card className="w-full max-w-2xl h-[600px] flex flex-col bg-slate-900 border-slate-700 shadow-2xl">
                <CardHeader className="border-b border-slate-800 pb-4">
                    <CardTitle className="text-white flex items-center justify-between">
                        <span>Select Files or Folders</span>
                        <Button variant="ghost" size="sm" onClick={onCancel} className="text-slate-400 hover:text-white">✕</Button>
                    </CardTitle>
                    <div className="text-xs text-slate-400 font-mono break-all bg-slate-950 p-2 rounded border border-slate-800 mt-2">
                        {currentPath}
                    </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto p-2">
                    {loading ? (
                        <div className="flex h-full items-center justify-center">
                            <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-1">
                            {items.map((item, i) => {
                                const isSelected = selectedPaths.has(item.path);
                                return (
                                    <div
                                        key={i}
                                        onClick={() => handleNavigate(item)}
                                        className={`flex items-center gap-3 p-3 rounded-md cursor-pointer transition-colors hover:bg-slate-800 ${item.name === ".." ? "text-slate-400" : "text-slate-200"}`}
                                    >
                                        {item.name !== ".." && (
                                            <div onClick={(e) => toggleSelection(e, item.path)} className="text-slate-400 hover:text-purple-400">
                                                {isSelected ? <CheckSquare className="w-5 h-5 text-purple-500" /> : <Square className="w-5 h-5" />}
                                            </div>
                                        )}

                                        {item.name === ".." ? (
                                            <ChevronUp className="w-5 h-5" />
                                        ) : item.is_dir ? (
                                            <Folder className="w-5 h-5 text-blue-400" />
                                        ) : (
                                            <File className="w-5 h-5 text-slate-500" />
                                        )}
                                        <span className="truncate font-medium">{item.name}</span>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </CardContent>
                <div className="p-4 border-t border-slate-800 flex justify-between items-center bg-slate-900 rounded-b-lg">
                    <div className="text-sm text-slate-400">
                        {selectedPaths.size} items selected
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" onClick={onCancel} className="border-slate-700 text-slate-300">Cancel</Button>
                        <Button onClick={handleSelectCurrent} className="bg-purple-600 hover:bg-purple-500">
                            {selectedPaths.size > 0 ? `Analyze ${selectedPaths.size} Items` : "Analyze Current Folder"}
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
}
