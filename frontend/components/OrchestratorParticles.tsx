'use client';

import React, { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sparkles, Environment } from '@react-three/drei';
import * as THREE from 'three';
import { BrandColors } from '../types';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';

const PARTICLE_COUNT = 5000;
const AGENT_COUNT = 5;

const ParticleSystem = () => {
  const pointsRef = useRef<THREE.Points>(null);

  const { positions, colors, targetConfig } = useMemo(() => {
    const pos = new Float32Array(PARTICLE_COUNT * 3);
    const col = new Float32Array(PARTICLE_COUNT * 3);
    const config = new Float32Array(PARTICLE_COUNT); // Stores which cluster (0=Orchestrator, 1-5=Agents)

    const cGold = new THREE.Color(BrandColors.NeuralYellow);
    const cBlue = new THREE.Color(BrandColors.ElectricBlue);
    const cPlatinum = new THREE.Color(BrandColors.Platinum);
    const cWhite = new THREE.Color('#ffffff');

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;
      
      // Distribution: 30% Core (Orchestrator), 70% Agents (Satellites)
      const type = Math.random() > 0.3 ? Math.ceil(Math.random() * AGENT_COUNT) : 0;
      config[i] = type;

      // Initial Scattering (Chaos for "assembling" effect)
      pos[i3] = (Math.random() - 0.5) * 40;
      pos[i3 + 1] = (Math.random() - 0.5) * 40;
      pos[i3 + 2] = (Math.random() - 0.5) * 40;

      // Colors
      const tempColor = new THREE.Color();
      if (type === 0) {
        // Core: Dominant Gold/White
        const r = Math.random();
        if (r > 0.5) tempColor.copy(cGold);
        else if (r > 0.2) tempColor.copy(cWhite);
        else tempColor.copy(cPlatinum);
      } else {
        // Agents: Dominant Blue/Platinum
        const r = Math.random();
        if (r > 0.6) tempColor.copy(cBlue);
        else if (r > 0.3) tempColor.copy(cPlatinum);
        else tempColor.copy(cWhite);
      }

      col[i3] = tempColor.r;
      col[i3 + 1] = tempColor.g;
      col[i3 + 2] = tempColor.b;
    }

    return { positions: pos, colors: col, targetConfig: config };
  }, []);

  useFrame((state) => {
    if (!pointsRef.current) return;
    const time = state.clock.getElapsedTime();
    const pos = pointsRef.current.geometry.attributes.position.array as Float32Array;

    // Orchestrator Pulse
    const corePulse = 1 + Math.sin(time * 1.5) * 0.05;
    
    // Orbital Parameters for Agents
    const orbitRadiusX = 4.2;
    const orbitRadiusZ = 3.5;
    const orbitSpeed = 0.15; // Slow, majestic orbit

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;
      const type = targetConfig[i];
      
      let tx = 0, ty = 0, tz = 0;

      if (type === 0) {
        // --- ORCHESTRATOR (Center) ---
        // Spherical structure with internal flow
        const u = (i * 0.01) % 1; 
        const v = (i * 0.03) % 1;
        const theta = 2 * Math.PI * u + time * 0.2;
        const phi = Math.acos(2 * v - 1);
        
        const r = 1.4 * corePulse;
        
        // Add turbulence
        const noise = Math.sin(i * 0.5 + time) * 0.15;
        
        tx = (r + noise) * Math.sin(phi) * Math.cos(theta);
        ty = (r + noise) * Math.sin(phi) * Math.sin(theta);
        tz = (r + noise) * Math.cos(phi);

      } else {
        // --- AGENTS (Satellites) ---
        const agentIdx = type - 1;
        
        // Calculate orbital center for this agent
        // Evenly spaced around the circle
        const angleOffset = (agentIdx / AGENT_COUNT) * Math.PI * 2;
        const currentAngle = angleOffset + time * orbitSpeed;
        
        const centerX = Math.cos(currentAngle) * orbitRadiusX;
        const centerZ = Math.sin(currentAngle) * orbitRadiusZ;
        // Gentle vertical wave based on orbit
        const centerY = Math.sin(currentAngle * 2 + time) * 0.8; 

        // Agent Shape (Dense Cluster)
        // Use a local index seed for stable random shape
        const localSeed = i % 200;
        const rLocal = 0.65;
        
        // Random scatter within the agent cluster
        // We use simple trig to make cloud-like shapes
        const lx = Math.sin(localSeed) * rLocal;
        const ly = Math.cos(localSeed * 1.2) * rLocal;
        const lz = Math.sin(localSeed * 2.5) * rLocal;
        
        // Rotate agent cluster locally to make it feel alive
        const rotSpeed = 1.5;
        const rotX = lx * Math.cos(time * rotSpeed) - lz * Math.sin(time * rotSpeed);
        const rotZ = lx * Math.sin(time * rotSpeed) + lz * Math.cos(time * rotSpeed);

        tx = centerX + rotX;
        ty = centerY + ly;
        tz = centerZ + rotZ;
      }

      // LERP Logic for "Gradual Assembly" and Fluid Motion
      // The particles constantly seek their target positions
      const lerpFactor = 0.035; // Smooth drag
      
      pos[i3] += (tx - pos[i3]) * lerpFactor;
      pos[i3 + 1] += (ty - pos[i3 + 1]) * lerpFactor;
      pos[i3 + 2] += (tz - pos[i3 + 2]) * lerpFactor;
    }

    pointsRef.current.geometry.attributes.position.needsUpdate = true;
    
    // Gentle global rotation of entire system
    pointsRef.current.rotation.y = time * 0.05;
    pointsRef.current.rotation.z = Math.sin(time * 0.15) * 0.05;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={PARTICLE_COUNT} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={PARTICLE_COUNT} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={0.04}
        vertexColors
        transparent
        opacity={0.9}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
        sizeAttenuation
      />
    </points>
  );
};

export const OrchestratorParticles: React.FC = () => {
  return (
    <div className="relative w-full h-[80vh] bg-[#050505] overflow-hidden border-y border-white/5">
       {/* Top/Bottom Fades for Seamless Section Integration */}
       <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-[#050505] to-transparent z-10 pointer-events-none"></div>
       <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-[#050505] to-transparent z-10 pointer-events-none"></div>
       
       {/* Subtle Cinematic Backdrop Glow */}
       <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(110,104,59,0.08)_0%,transparent_60%)] pointer-events-none"></div>

       <Canvas camera={{ position: [0, 4, 12], fov: 35 }} dpr={[1, 2]}>
          <color attach="background" args={['#050505']} />
          <fog attach="fog" args={['#050505', 12, 35]} />
          
          <Environment preset="city" />
          
          <Float speed={0.5} rotationIntensity={0.1} floatIntensity={0.1}>
             <ParticleSystem />
          </Float>
          
          {/* Background Dust */}
          <Sparkles count={80} scale={18} size={2} speed={0.2} opacity={0.2} color="#ffffff" />
          
          <EffectComposer enableNormalPass={false}>
             {/* Luxurious Soft Bloom */}
             <Bloom luminanceThreshold={0.2} mipmapBlur intensity={0.5} radius={0.5} />
             <Vignette eskil={false} offset={0.1} darkness={0.7} />
          </EffectComposer>
       </Canvas>
    </div>
  );
};