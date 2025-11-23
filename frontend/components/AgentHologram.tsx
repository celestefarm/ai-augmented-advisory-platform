'use client';

import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Line, Html, Float, Sparkles, Environment } from '@react-three/drei';
import * as THREE from 'three';
import { EffectComposer, Bloom, Noise, Vignette } from '@react-three/postprocessing';
import '../types';

// Luxury Palette
const GOLD = '#C5B358'; // Vegas Gold (Metallic)
const OLIVE_GOLD = '#6e683b'; // Brand Gold
const PLATINUM = '#E5E4E2';
const OBSIDIAN = '#0a0a0a';

// Reusable Materials
const ObsidianMaterial = () => (
  <meshPhysicalMaterial
    color={OBSIDIAN}
    metalness={0.9}
    roughness={0.1}
    clearcoat={1}
    clearcoatRoughness={0.1}
  />
);

const PlatinumMaterial = () => (
  <meshStandardMaterial
    color={PLATINUM}
    metalness={1}
    roughness={0.2}
  />
);

const GlassMaterial = ({ active, color }: { active: boolean, color: string }) => (
  <meshPhysicalMaterial
    color={active ? color : '#ffffff'}
    metalness={0.1}
    roughness={0}
    transmission={1} // Glass effect
    thickness={2} // Refraction volume
    ior={1.5}
    clearcoat={1}
    transparent
    opacity={0.8}
    emissive={active ? color : '#000000'}
    emissiveIntensity={active ? 0.5 : 0}
  />
);

const SpinningGroup = ({ children }: { children?: React.ReactNode }) => {
    const ref = useRef<THREE.Group>(null);
    useFrame(() => {
        if (ref.current) {
            ref.current.rotation.y += 0.001; // Slower, majestic rotation
        }
    });
    return <group ref={ref}>{children}</group>;
}

interface NodeProps {
  position: [number, number, number];
  color: string;
  label: string;
  subLabel: string;
  onClick: () => void;
  active: boolean;
}

const AgentNode: React.FC<NodeProps> = ({ position, color, label, subLabel, onClick, active }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (!meshRef.current) return;
    // Slow, diamond-like rotation
    meshRef.current.rotation.x += 0.005;
    meshRef.current.rotation.y += 0.01;
    
    // Subtle scale breath
    const targetScale = active || hovered ? 1.2 : 1.0;
    meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.05);
  });

  return (
    <group position={position}>
      <Float speed={1.5} rotationIntensity={0.1} floatIntensity={0.2}>
        {/* The Jewel / Prism */}
        <mesh 
          ref={meshRef} 
          onClick={onClick} 
          onPointerOver={() => { setHovered(true); document.body.style.cursor = 'pointer'; }}
          onPointerOut={() => { setHovered(false); document.body.style.cursor = 'default'; }}
        >
          <octahedronGeometry args={[0.5, 0]} />
          <GlassMaterial active={active || hovered} color={color} />
        </mesh>

        {/* Metallic Housing/Claw */}
        <group rotation={[0, Math.PI / 4, 0]}>
           <mesh scale={[1.05, 1.05, 1.05]}>
              <torusGeometry args={[0.4, 0.02, 16, 4]} /> {/* Square ring */}
              <meshStandardMaterial color={PLATINUM} metalness={0.8} roughness={0.2} />
           </mesh>
        </group>
        
        {/* Selection Halo (Subtle) */}
        {(active || hovered) && (
           <mesh>
             <sphereGeometry args={[0.8, 32, 32]} />
             <meshBasicMaterial color={color} transparent opacity={0.05} />
           </mesh>
        )}
      </Float>

      {/* Connection Beam (Fiber Optic Style) */}
      <Line
        points={[[0, 0, 0], [-position[0], -position[1], -position[2]]]}
        color={active || hovered ? color : '#333333'}
        lineWidth={active || hovered ? 2 : 0.5}
        transparent
        opacity={active || hovered ? 0.4 : 0.1}
      />

      {/* Minimalist Executive Label */}
      <Html distanceFactor={15} position={[0, 0.9, 0]} center style={{ pointerEvents: 'none' }}>
        <div className={`transition-all duration-700 flex flex-col items-center text-center w-64 ${active || hovered ? 'opacity-100 translate-y-0' : 'opacity-40 translate-y-2'}`}>
          <div className="flex items-center gap-2 mb-1">
             <div className={`w-1.5 h-1.5 rounded-full ${active ? 'animate-pulse' : ''}`} style={{ backgroundColor: color }}></div>
             <span className="text-sm font-display text-white tracking-[0.2em] uppercase font-bold">{label}</span>
          </div>
          <div className="h-px w-8 bg-white/20 mb-1"></div>
          <span className="text-xs text-gray-400 uppercase tracking-widest">{subLabel}</span>
        </div>
      </Html>
    </group>
  );
};

const GyroscopeCore = () => {
  const ring1 = useRef<THREE.Mesh>(null);
  const ring2 = useRef<THREE.Mesh>(null);
  const ring3 = useRef<THREE.Mesh>(null);

  useFrame((state) => {
     if (ring1.current) ring1.current.rotation.x += 0.002;
     if (ring2.current) ring2.current.rotation.y += 0.003;
     if (ring3.current) ring3.current.rotation.z += 0.001;
  });

  return (
    <group>
      {/* Central Obsidian Sphere */}
      <mesh>
        <sphereGeometry args={[1, 64, 64]} />
        <ObsidianMaterial />
      </mesh>
      
      {/* Inner Gold Glow (The Intelligence) */}
      <pointLight intensity={2} distance={3} decay={2} color={OLIVE_GOLD} />
      
      {/* Gyroscopic Rings - Precision Engineering */}
      <mesh ref={ring1} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1.4, 0.03, 16, 100]} />
        <PlatinumMaterial />
      </mesh>

      <mesh ref={ring2} rotation={[0, Math.PI / 6, 0]}>
        <torusGeometry args={[1.8, 0.03, 16, 100]} />
        <meshStandardMaterial color={OLIVE_GOLD} metalness={1} roughness={0.2} />
      </mesh>

      <mesh ref={ring3}>
        <torusGeometry args={[2.2, 0.02, 16, 100]} />
        <meshStandardMaterial color="#555" metalness={0.5} roughness={0.5} />
      </mesh>
    </group>
  );
};

export const AgentHologram = () => {
  const [activeId, setActiveId] = useState<number | null>(null);
  
  // Matches the AgentsPage.tsx Roster
  const agents = useMemo(() => [
    { id: 1, label: "Horizon Scanner", sub: "The Watchman", color: '#3b6285', pos: [4, 0.5, 0] },
    { id: 2, label: "Capital Sentinel", sub: "The Survivor", color: '#6e683b', pos: [1.5, 2.5, 1.5] },
    { id: 3, label: "Devil's Advocate", sub: "The Challenger", color: '#e0e0e0', pos: [-3.5, 1, -1] },
    { id: 4, label: "Culture Cipher", sub: "The Variable", color: '#a0a0a0', pos: [-2, -2, 2] },
    { id: 5, label: "Operational Bridge", sub: "The Architect", color: '#00f0ff', pos: [2, -2.5, -1] },
  ], []);

  return (
    <div className="w-full h-[650px] relative bg-[#050505]">
       {/* Ambient Background Gradient */}
       <div className="absolute inset-0 bg-gradient-to-b from-[#050505] via-[#08080a] to-[#050505] pointer-events-none" />

      <Canvas camera={{ position: [0, 0, 11], fov: 35 }} dpr={[1, 2]}>
        <color attach="background" args={['#050505']} />
        <fog attach="fog" args={['#050505', 15, 30]} />

        {/* Studio Lighting for Materials */}
        <Environment preset="city" /> 
        <ambientLight intensity={0.2} />
        
        {/* Dramatic Key Light */}
        <spotLight 
          position={[10, 15, 10]} 
          angle={0.3} 
          penumbra={1} 
          intensity={2} 
          castShadow 
          color="#ffffff" 
        />
        {/* Rim Light */}
        <pointLight position={[-5, 0, -5]} intensity={1.5} color={OLIVE_GOLD} />

        <group position={[0, 0, 0]}>
           <GyroscopeCore />
           
           <SpinningGroup>
              {agents.map((agent: any) => (
                  <AgentNode 
                    key={agent.id}
                    position={agent.pos as [number, number, number]}
                    color={agent.color}
                    label={agent.label}
                    subLabel={agent.sub}
                    onClick={() => setActiveId(agent.id === activeId ? null : agent.id)}
                    active={activeId === agent.id}
                  />
              ))}
           </SpinningGroup>
        </group>

        <Sparkles count={80} scale={12} size={1.5} speed={0.1} opacity={0.1} color={PLATINUM} />
        
        <EffectComposer enableNormalPass={false}>
          <Bloom luminanceThreshold={1} mipmapBlur intensity={0.5} radius={0.4} />
          <Noise opacity={0.02} />
          <Vignette eskil={false} offset={0.1} darkness={0.8} />
        </EffectComposer>
      </Canvas>
      
      {/* Interactive Instruction - Minimalist */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 text-center pointer-events-none z-10 opacity-50">
         <div className="w-px h-8 bg-white/20 mx-auto mb-3"></div>
         <p className="text-sm text-gray-400 uppercase tracking-[0.3em]">Interactive Network Topology</p>
      </div>
    </div>
  );
};