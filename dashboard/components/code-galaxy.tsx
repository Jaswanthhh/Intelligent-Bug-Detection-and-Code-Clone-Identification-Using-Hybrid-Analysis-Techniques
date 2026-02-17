// @ts-nocheck
"use client";

import { useRef, useMemo, useState, useLayoutEffect, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars, Text, Trail } from "@react-three/drei";
import * as THREE from "three";
import { motion } from "framer-motion";

// Types based on the API response
interface FileNode {
    path: string;
    size: number;
    type: "function" | "class" | "file";
    hasBug: boolean;
    bugSeverity?: string;
}

interface CloneLink {
    source: string; // path
    target: string; // path
    score: number;
}

interface CodeGalaxyProps {
    files: any[];
    clones: any[];
    bugs: any[];
}

function Connections({ links, nodePositions }: { links: CloneLink[], nodePositions: Record<string, [number, number, number]> }) {
    const points = useMemo(() => {
        const lines: THREE.Vector3[][] = [];
        links.forEach(link => {
            const start = nodePositions[link.source];
            const end = nodePositions[link.target];
            if (start && end) {
                lines.push([new THREE.Vector3(...start), new THREE.Vector3(...end)]);
            }
        });
        return lines;
    }, [links, nodePositions]);

    return (
        <>
            {points.map((line, i) => (
                <line key={i}>
                    <bufferGeometry>
                        <bufferAttribute
                            attach="attributes-position"
                            count={2}
                            array={new Float32Array([...line[0].toArray(), ...line[1].toArray()])}
                            itemSize={3}
                        />
                    </bufferGeometry>
                    <lineBasicMaterial color="#4ade80" transparent opacity={0.3} linewidth={1} />
                </line>
            ))}
        </>
    );
}

function InstancedNodes({ nodes, positions, onSelectNode }: { nodes: FileNode[], positions: Record<string, [number, number, number]>, onSelectNode: (n: FileNode) => void }) {
    const meshRef = useRef<THREE.InstancedMesh>(null);
    const [hoveredId, setHoveredId] = useState<number | null>(null);
    const tempObject = useMemo(() => new THREE.Object3D(), []);
    const tempColor = useMemo(() => new THREE.Color(), []);

    // Layout effect to update instances
    useLayoutEffect(() => {
        if (!meshRef.current) return;

        nodes.forEach((node, i) => {
            const [x, y, z] = positions[node.path];
            tempObject.position.set(x, y, z);

            // Pulse effect handled in useFrame slightly differently, for static layout we set base scale
            tempObject.scale.set(0.5, 0.5, 0.5);

            tempObject.updateMatrix();
            meshRef.current!.setMatrixAt(i, tempObject.matrix);

            // Set Color
            const color = node.hasBug
                ? (node.bugSeverity === 'critical' ? '#ef4444' : '#f97316')
                : (node.path.endsWith('.py') ? '#3b82f6' : '#a855f7');

            tempColor.set(color);
            meshRef.current!.setColorAt(i, tempColor);
        });

        meshRef.current.instanceMatrix.needsUpdate = true;
        if (meshRef.current.instanceColor) meshRef.current.instanceColor.needsUpdate = true;

    }, [nodes, positions]);

    // Animation Loop for hover/pulse
    useFrame((state) => {
        if (!meshRef.current) return;

        // We can't easily animate individual scales without iterating all.
        // For performance, we only animate the Hovered node or rely on shader.
        // For now, simple hover scale.

        if (hoveredId !== null && nodes[hoveredId]) {
            const node = nodes[hoveredId];
            const [x, y, z] = positions[node.path];
            tempObject.position.set(x, y, z);

            // Pulse/Scale up hovered
            const s = 1.0 + Math.sin(state.clock.elapsedTime * 10) * 0.2;
            tempObject.scale.set(s, s, s);

            tempObject.updateMatrix();
            meshRef.current.setMatrixAt(hoveredId, tempObject.matrix);
            meshRef.current.instanceMatrix.needsUpdate = true;
        }
    });

    return (
        <instancedMesh
            ref={meshRef}
            args={[undefined, undefined, nodes.length]}
            onClick={(e) => {
                e.stopPropagation();
                if (e.instanceId !== undefined && nodes[e.instanceId]) {
                    onSelectNode(nodes[e.instanceId]);
                }
            }}
            onPointerOver={(e) => {
                e.stopPropagation();
                setHoveredId(e.instanceId !== undefined ? e.instanceId : null);
                // Change cursor
                document.body.style.cursor = 'pointer';
            }}
            onPointerOut={(e) => {
                setHoveredId(null);
                document.body.style.cursor = 'auto';
            }}
        >
            <sphereGeometry args={[1, 16, 16]} />
            <meshStandardMaterial />
        </instancedMesh>
    );
}


function Scene({ files, clones, bugs, onSelectNode, filters }: {
    files: any[], clones: any[], bugs: any[],
    onSelectNode: (n: FileNode) => void,
    filters: { showHealthy: boolean; showBugs: boolean; showClones: boolean; autoRotate: boolean }
}) {
    // Pre-process data
    const { nodes, links, positions } = useMemo(() => {
        let nodes: FileNode[] = files.map((f: any) => {
            const fileBugs = bugs.filter((b: any) => b.file === f.path);
            const maxSeverity = fileBugs.length > 0
                ? fileBugs.some((b: any) => b.severity === 'critical') ? 'critical' : 'high'
                : undefined;

            return {
                path: f.path,
                size: 1,
                type: 'file',
                hasBug: fileBugs.length > 0,
                bugSeverity: maxSeverity
            };
        });

        // Filter nodes
        nodes = nodes.filter(n => {
            if (n.hasBug && !filters.showBugs) return false;
            if (!n.hasBug && !filters.showHealthy) return false;
            return true;
        });

        // Layout
        const positions: Record<string, [number, number, number]> = {};
        const phi = Math.PI * (3 - Math.sqrt(5));

        nodes.forEach((node, i) => {
            const y = 1 - (i / (nodes.length - 1)) * 2;
            const radius = Math.sqrt(1 - y * y);
            const theta = phi * i;

            const r = 10;
            const x = Math.cos(theta) * radius * r;
            const z = Math.sin(theta) * radius * r;
            const y_pos = y * r;

            positions[node.path] = [x, y_pos, z];
        });

        let links: CloneLink[] = clones.map((c: any) => ({
            source: c.file_a,
            target: c.file_b,
            score: c.fusion_score
        }));

        if (!filters.showClones) {
            links = [];
        } else {
            links = links.filter(l => positions[l.source] && positions[l.target]);
        }

        return { nodes, links, positions };
    }, [files, clones, bugs, filters.showBugs, filters.showHealthy, filters.showClones]);

    return (
        <>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />

            <InstancedNodes nodes={nodes} positions={positions} onSelectNode={onSelectNode} />

            <Connections links={links} nodePositions={positions} />
            <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} autoRotate={filters.autoRotate} autoRotateSpeed={0.5} />
        </>
    );
}

export default function CodeGalaxy({ files, clones, bugs }: CodeGalaxyProps) {
    const [selectedNode, setSelectedNode] = useState<FileNode | null>(null);
    const [filters, setFilters] = useState({
        showHealthy: true,
        showBugs: true,
        showClones: true,
        autoRotate: true
    });

    return (
        <div className="w-full h-full relative">
            <Canvas camera={{ position: [0, 0, 25], fov: 60 }} dpr={[1, 2]} performance={{ min: 0.5 }}>
                {/* dpr and performance props allow automatic quality scaling */}
                <Scene files={files} clones={clones} bugs={bugs} onSelectNode={setSelectedNode} filters={filters} />
            </Canvas>

            {/* Filter Controls (Bottom Right) */}
            <div className="absolute bottom-4 right-4 p-4 bg-slate-900/80 border border-slate-700 rounded-lg backdrop-blur-md text-white w-48 z-10">
                <h4 className="font-bold text-sm mb-3 text-purple-400">Galaxy Controls</h4>
                <div className="space-y-2 text-xs">
                    <label className="flex items-center gap-2 cursor-pointer hover:text-purple-300">
                        <input type="checkbox" checked={filters.showBugs} onChange={e => setFilters({ ...filters, showBugs: e.target.checked })} className="sc-checkbox" />
                        Show Bugs
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer hover:text-purple-300">
                        <input type="checkbox" checked={filters.showHealthy} onChange={e => setFilters({ ...filters, showHealthy: e.target.checked })} className="sc-checkbox" />
                        Show Healthy Files
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer hover:text-purple-300">
                        <input type="checkbox" checked={filters.showClones} onChange={e => setFilters({ ...filters, showClones: e.target.checked })} className="sc-checkbox" />
                        Show Clone Links
                    </label>
                    <div className="h-px bg-slate-700 my-2"></div>
                    <label className="flex items-center gap-2 cursor-pointer hover:text-purple-300">
                        <input type="checkbox" checked={filters.autoRotate} onChange={e => setFilters({ ...filters, autoRotate: e.target.checked })} className="sc-checkbox" />
                        Auto-Rotate
                    </label>
                </div>
            </div>

            {selectedNode && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute bottom-4 left-4 p-4 bg-slate-900/90 border border-slate-700 rounded-lg text-white max-w-sm backdrop-blur-md"
                >
                    <h3 className="font-bold text-lg text-purple-400 break-all">{selectedNode.path.split('/').pop()}</h3>
                    <p className="text-xs text-slate-500 font-mono mb-2">{selectedNode.path}</p>
                    {selectedNode.hasBug ? (
                        <div className="text-red-400 font-bold">
                            ⚠ Bugs Detected ({selectedNode.bugSeverity?.toUpperCase()})
                        </div>
                    ) : (
                        <div className="text-green-400">
                            ✓ Code Healthy
                        </div>
                    )}
                    <p className="text-xs text-slate-400 mt-2">
                        Click outside to unselect. Drag to rotate galaxy.
                    </p>
                </motion.div>
            )}
        </div>
    );
}
