'use client';

import React, { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sparkles, Environment } from '@react-three/drei';
import * as THREE from 'three';
import { EffectComposer, Bloom, Vignette, Noise } from '@react-three/postprocessing';
import '../types';

const GOLD = '#6e683b';
const PLATINUM = '#e0e0e0';
const BLUE = '#3b6285';

const MorphingParticles = () => {
  const count = 4000;
  const mesh = useRef<THREE.Points>(null);
  
  const { positions, colors, targets } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    
    const tSphere = new Float32Array(count * 3);
    const tHelix = new Float32Array(count * 3);
    const tStrands = new Float32Array(count * 3);
    
    const color1 = new THREE.Color(GOLD);
    const color2 = new THREE.Color(PLATINUM);
    const color3 = new THREE.Color(BLUE);
    const tempColor = new THREE.Color();

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;

      // Initial Position (Sphere)
      const phi = Math.acos(-1 + (2 * i) / count);
      const theta = Math.sqrt(count * Math.PI) * phi;
      
      const rSphere = 3.5;
      const sx = rSphere * Math.cos(theta) * Math.sin(phi);
      const sy = rSphere * Math.sin(theta) * Math.sin(phi);
      const sz = rSphere * Math.cos(phi);
      
      positions[i3] = sx;
      positions[i3+1] = sy;
      positions[i3+2] = sz;
      
      tSphere[i3] = sx;
      tSphere[i3+1] = sy;
      tSphere[i3+2] = sz;

      // Target 2: DNA Helix (Symbiosis)
      const t = i * 0.02;
      const hRad = 1.8;
      const hY = (i / count) * 10 - 5;
      // Double helix offset
      const offset = i % 2 === 0 ? 0 : Math.PI;
      tHelix[i3] = Math.cos(t + offset) * hRad;
      tHelix[i3+1] = hY;
      tHelix[i3+2] = Math.sin(t + offset) * hRad;

      // Target 3: Neural Strands (Innovation/Flow)
      // Flowing lines representing data streams
      const strand = i % 12; // 12 distinct strands
      const sT = (i / count) * Math.PI * 2;
      const sRad = 1.5 + Math.sin(sT * 4) * 1.5; // Expanding/contracting radius
      const spiral = sT * 3;
      
      tStrands[i3] = Math.cos(spiral + strand) * sRad;
      tStrands[i3+1] = (i / count) * 12 - 6;
      tStrands[i3+2] = Math.sin(spiral + strand) * sRad;

      // Colors - heavily weighted towards gold/platinum for luxury
      const mixed = Math.random();
      if (mixed > 0.7) {
          tempColor.copy(color1); // Gold
      } else if (mixed > 0.3) {
          tempColor.copy(color2); // Platinum
      } else {
          tempColor.copy(color3); // Blue accent
      }
      
      colors[i3] = tempColor.r;
      colors[i3+1] = tempColor.g;
      colors[i3+2] = tempColor.b;
    }

    return { positions, colors, targets: [tHelix, tSphere, tStrands] };
  }, []);

  useFrame(({ clock, mouse }) => {
    if (!mesh.current) return;
    
    const time = clock.getElapsedTime() * 0.4; // Slow, majestic speed
    const cycleDuration = 8;
    const cycle = time % (cycleDuration * 3);
    
    let currentTarget = targets[0];
    let nextTarget = targets[1];
    let alpha = 0;

    // Cycle 1: Helix -> Sphere
    if (cycle < cycleDuration) {
        currentTarget = targets[0];
        nextTarget = targets[1];
        alpha = cycle / cycleDuration;
    } 
    // Cycle 2: Sphere -> Strands
    else if (cycle < cycleDuration * 2) {
        currentTarget = targets[1];
        nextTarget = targets[2];
        alpha = (cycle - cycleDuration) / cycleDuration;
    } 
    // Cycle 3: Strands -> Helix
    else {
        currentTarget = targets[2];
        nextTarget = targets[0];
        alpha = (cycle - cycleDuration * 2) / cycleDuration;
    }
    
    // Cubic easing for smoother transitions
    const easedAlpha = alpha < 0.5 ? 4 * alpha * alpha * alpha : 1 - Math.pow(-2 * alpha + 2, 3) / 2;

    const pos = mesh.current.geometry.attributes.position;
    
    for (let i = 0; i < count; i++) {
        const i3 = i * 3;
        
        const cx = currentTarget[i3];
        const cy = currentTarget[i3+1];
        const cz = currentTarget[i3+2];
        
        const nx = nextTarget[i3];
        const ny = nextTarget[i3+1];
        const nz = nextTarget[i3+2];
        
        let x = cx + (nx - cx) * easedAlpha;
        let y = cy + (ny - cy) * easedAlpha;
        let z = cz + (nz - cz) * easedAlpha;
        
        // Add gentle "breathing" noise
        const noiseAmp = 0.05;
        x += Math.sin(time * 2 + y) * noiseAmp;
        z += Math.cos(time * 1.5 + x) * noiseAmp;

        pos.setXYZ(i, x, y, z);
    }
    pos.needsUpdate = true;
    
    // Slow global rotation
    mesh.current.rotation.y = -time * 0.1;
    
    // Subtle mouse parallax
    mesh.current.rotation.x = THREE.MathUtils.lerp(mesh.current.rotation.x, mouse.y * 0.1, 0.05);
    mesh.current.rotation.z = THREE.MathUtils.lerp(mesh.current.rotation.z, mouse.x * 0.1, 0.05);
  });

  return (
    <points ref={mesh}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={count} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial 
        size={0.035} 
        vertexColors 
        transparent 
        opacity={0.85} 
        blending={THREE.AdditiveBlending} 
        sizeAttenuation 
        depthWrite={false} 
      />
    </points>
  );
};

export const OriginParticles = () => {
  return (
    <div className="absolute inset-0 w-full h-full z-0 pointer-events-none">
        <Canvas camera={{ position: [0, 0, 9], fov: 35 }} dpr={[1, 2]}>
            <color attach="background" args={['#050505']} />
            <fog attach="fog" args={['#050505', 10, 30]} />
            
            <Environment preset="city" />
            <ambientLight intensity={0.2} />

            <Float speed={1.5} rotationIntensity={0.1} floatIntensity={0.2}>
                <MorphingParticles />
            </Float>
            
            {/* Add atmosphere */}
            <Sparkles count={50} scale={12} size={2} speed={0.2} opacity={0.2} color={GOLD} />

            <EffectComposer enableNormalPass={false}>
               <Bloom luminanceThreshold={0.2} mipmapBlur intensity={0.6} radius={0.5} />
               <Noise opacity={0.02} />
               <Vignette eskil={false} offset={0.1} darkness={0.6} />
            </EffectComposer>
        </Canvas>
    </div>
  );
};