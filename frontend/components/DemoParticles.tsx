'use client';

import React, { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sparkles } from '@react-three/drei';
import * as THREE from 'three';
import { BrandColors } from '../types';
import { EffectComposer, Bloom, Vignette, Noise } from '@react-three/postprocessing';

const PARTICLE_COUNT = 3000;

const TerrainSystem = () => {
  const pointsRef = useRef<THREE.Points>(null);

  const { positions, colors } = useMemo(() => {
    const pos = new Float32Array(PARTICLE_COUNT * 3);
    const col = new Float32Array(PARTICLE_COUNT * 3);

    const cGold = new THREE.Color(BrandColors.NeuralYellow);
    const cBlue = new THREE.Color(BrandColors.ElectricBlue);
    const cPlatinum = new THREE.Color(BrandColors.Platinum);
    const cDeep = new THREE.Color('#0a0a0a');

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;

      // Create a grid-like distribution but distorted
      const gridSize = 60; // spread
      const x = (Math.random() - 0.5) * gridSize;
      const z = (Math.random() - 0.5) * gridSize;
      // Initial flat plane
      const y = -4;

      pos[i3] = x;
      pos[i3 + 1] = y;
      pos[i3 + 2] = z;

      // Color Logic: Data Grid aesthetic
      const dist = Math.sqrt(x * x + z * z);
      const tempColor = new THREE.Color();

      if (dist < 5) {
          // Center hotspot (Command)
          tempColor.copy(cGold);
      } else if (Math.random() > 0.9) {
          // Data spikes (Anomalies)
          tempColor.copy(cBlue);
      } else {
          // General grid (Noise)
          tempColor.copy(cPlatinum).lerp(cDeep, 0.7);
      }

      col[i3] = tempColor.r;
      col[i3 + 1] = tempColor.g;
      col[i3 + 2] = tempColor.b;
    }

    return { positions: pos, colors: col };
  }, []);

  useFrame((state) => {
    if (!pointsRef.current) return;
    const time = state.clock.getElapsedTime();
    const pos = pointsRef.current.geometry.attributes.position.array as Float32Array;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        const i3 = i * 3;
        const x = pos[i3];
        const z = pos[i3 + 2];
        
        // Terrain Undulation Function (Simulating market volatility)
        // We only modify Y
        
        // Wave 1: Slow rolling macro trends
        const wave1 = Math.sin(x * 0.1 + time * 0.2) * Math.cos(z * 0.1 + time * 0.1) * 2;
        
        // Wave 2: Fast micro fluctuations
        const wave2 = Math.sin(x * 0.5 - time) * Math.cos(z * 0.5 + time) * 0.5;
        
        // Center focus (flat area for the UI)
        const dist = Math.sqrt(x * x + z * z);
        const centerFlatten = Math.min(dist / 10, 1); // 0 at center, 1 at edge

        pos[i3 + 1] = -5 + (wave1 + wave2) * centerFlatten;
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true;
    
    // Slow Rotation
    pointsRef.current.rotation.y = time * 0.02;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={PARTICLE_COUNT} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={PARTICLE_COUNT} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={0.08}
        vertexColors
        transparent
        opacity={0.6}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
        sizeAttenuation
      />
    </points>
  );
};

export const DemoParticles = () => {
  return (
    <div className="fixed top-0 left-0 w-full h-full pointer-events-none z-0">
       {/* Gradient overlays for text readability */}
       <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-[#050505] via-transparent to-[#050505] opacity-90 z-10"></div>
       
       <Canvas camera={{ position: [0, 5, 15], fov: 45 }} dpr={[1, 2]}>
          <color attach="background" args={['#050505']} />
          
          <Float speed={0.2} rotationIntensity={0.05} floatIntensity={0.05}>
             <TerrainSystem />
          </Float>
          
          <Sparkles count={50} scale={20} size={2} speed={0.4} opacity={0.1} color="#00f0ff" />

          <EffectComposer enableNormalPass={false}>
             <Bloom luminanceThreshold={0.1} mipmapBlur intensity={0.6} radius={0.6} />
             <Noise opacity={0.03} />
             <Vignette eskil={false} offset={0.1} darkness={0.6} />
          </EffectComposer>
       </Canvas>
    </div>
  );
};