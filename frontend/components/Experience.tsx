'use client';

import React from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment, Sparkles, Float } from '@react-three/drei';
import { BrainParticles } from './BrainParticles';
import { EffectComposer, Bloom, Vignette, Noise } from '@react-three/postprocessing';
import * as THREE from 'three';
import '../types';

interface ExperienceProps {
  scrollProgress: number;
}

export const Experience: React.FC<ExperienceProps> = ({ scrollProgress }) => {
  return (
    <div className="fixed inset-0 w-full h-full z-0 pointer-events-none bg-[#050505]">
      <Canvas
        camera={{ position: [0, 0, 10], fov: 40 }}
        dpr={[1, 2]}
        gl={{ 
          antialias: true,
          toneMapping: THREE.ReinhardToneMapping,
          toneMappingExposure: 1.5
        }}
      >
        <color attach="background" args={['#050505']} />
        
        {/* Subtle Depth Fog */}
        <fog attach="fog" args={['#050505', 8, 25]} />

        {/* Background Atmosphere - Very Sparse */}
        <Sparkles 
          count={100} 
          scale={15} 
          size={1.5} 
          speed={0.1} 
          opacity={0.15} 
          color="#ffffff"
        />

        {/* Main Subject with Gentle Float */}
        <Float speed={0.4} rotationIntensity={0.05} floatIntensity={0.1}>
          <BrainParticles scrollProgress={scrollProgress} />
        </Float>

        {/* High-End Post Processing */}
        <EffectComposer enableNormalPass={false}>
          <Bloom 
            luminanceThreshold={0.1} 
            mipmapBlur 
            intensity={0.8} // Softer bloom
            radius={0.4}
          />
          {/* Very subtle grain for cinematic film look, not noisy */}
          <Noise opacity={0.02} /> 
          <Vignette eskil={false} offset={0.1} darkness={1.0} />
        </EffectComposer>
        
        {/* Studio Lighting Environment */}
        <Environment preset="studio" />
      </Canvas>
    </div>
  );
};