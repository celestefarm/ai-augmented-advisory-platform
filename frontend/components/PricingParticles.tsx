'use client';

import React, { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sparkles } from '@react-three/drei';
import * as THREE from 'three';
import { BrandColors } from '../types';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';

const PARTICLE_COUNT = 1500;

const AsymmetrySystem = () => {
  const pointsRef = useRef<THREE.Points>(null);

  const { positions, colors, targets } = useMemo(() => {
    const pos = new Float32Array(PARTICLE_COUNT * 3);
    const col = new Float32Array(PARTICLE_COUNT * 3);

    const tSymbiosis = new Float32Array(PARTICLE_COUNT * 3); // Double Helix
    const tMerkaba = new Float32Array(PARTICLE_COUNT * 3); // Star Tetrahedron
    const tSovereign = new Float32Array(PARTICLE_COUNT * 3); // Globe with Ring

    const cGold = new THREE.Color(BrandColors.NeuralYellow);
    const cPlatinum = new THREE.Color(BrandColors.Platinum);
    const cBlue = new THREE.Color(BrandColors.ElectricBlue);
    const cWhite = new THREE.Color('#ffffff');
    const tempColor = new THREE.Color();

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;

      // --- Target 0: The Symbiosis (Double Helix) ---
      // Represents the elegant fusion of Human Intent and AI Logic.
      // We create a tall, structured double helix cylinder.
      const t = (i / PARTICLE_COUNT) * Math.PI * 8; // 4 full turns
      const helixRadius = 2.5;
      // Normalize height from -6 to 6
      const height = (i / PARTICLE_COUNT) * 12 - 6; 
      
      // Split into two strands for the DNA effect
      const isStrandA = i % 2 === 0;
      const offset = isStrandA ? 0 : Math.PI;
      
      // Add volumetric thickness to the strands so they aren't just 1px lines
      const thickness = Math.random() * 0.5;
      const thickAngle = Math.random() * Math.PI * 2;
      
      tSymbiosis[i3] = Math.cos(t + offset) * helixRadius + Math.cos(thickAngle) * thickness;
      tSymbiosis[i3 + 1] = height;
      tSymbiosis[i3 + 2] = Math.sin(t + offset) * helixRadius + Math.sin(thickAngle) * thickness;

      // Initialize positions at Target 0 (Symbiosis) for an orchestrated start
      pos[i3] = tSymbiosis[i3];
      pos[i3+1] = tSymbiosis[i3+1];
      pos[i3+2] = tSymbiosis[i3+2];

      // --- Target 1: The Strategic Core (Star Tetrahedron / Merkaba) ---
      // Represents perfect balance, multidimensional analysis, and the "Diamond" edge.
      const scale = 4.5;
      
      // Define vertices for two interlocking tetrahedrons
      // Tetrahedron A (Base)
      const pA1 = new THREE.Vector3(1, 1, 1);
      const pA2 = new THREE.Vector3(1, -1, -1);
      const pA3 = new THREE.Vector3(-1, 1, -1);
      const pA4 = new THREE.Vector3(-1, -1, 1);
      
      // Tetrahedron B (Inverted)
      const pB1 = new THREE.Vector3(-1, -1, -1);
      const pB2 = new THREE.Vector3(-1, 1, 1);
      const pB3 = new THREE.Vector3(1, -1, 1);
      const pB4 = new THREE.Vector3(1, 1, -1);

      const whichTetra = i % 2; // Evenly split particles between shapes
      const face = Math.floor(Math.random() * 4); // Pick a face
      
      // Random Barycentric coordinates for uniform face distribution
      let a = Math.random();
      let b = Math.random();
      if (a + b > 1) { a = 1 - a; b = 1 - b; }
      
      const p = new THREE.Vector3();
      
      if (whichTetra === 0) {
          // Distribute on Tetra A faces
          if (face === 0) p.addScaledVector(pA1, 1-a-b).addScaledVector(pA2, a).addScaledVector(pA3, b);
          if (face === 1) p.addScaledVector(pA1, 1-a-b).addScaledVector(pA3, a).addScaledVector(pA4, b);
          if (face === 2) p.addScaledVector(pA1, 1-a-b).addScaledVector(pA4, a).addScaledVector(pA2, b);
          if (face === 3) p.addScaledVector(pA2, 1-a-b).addScaledVector(pA3, a).addScaledVector(pA4, b);
      } else {
          // Distribute on Tetra B faces
          if (face === 0) p.addScaledVector(pB1, 1-a-b).addScaledVector(pB2, a).addScaledVector(pB3, b);
          if (face === 1) p.addScaledVector(pB1, 1-a-b).addScaledVector(pB3, a).addScaledVector(pB4, b);
          if (face === 2) p.addScaledVector(pB1, 1-a-b).addScaledVector(pB4, a).addScaledVector(pB2, b);
          if (face === 3) p.addScaledVector(pB2, 1-a-b).addScaledVector(pB3, a).addScaledVector(pB4, b);
      }
      
      p.multiplyScalar(scale);

      tMerkaba[i3] = p.x;
      tMerkaba[i3+1] = p.y;
      tMerkaba[i3+2] = p.z;

      // --- Target 2: The Sovereign Sphere (Globe with Ring) ---
      // Represents global command, total coverage, and unity.
      const rSphere = 3.8;
      // 80% particles on sphere surface, 20% forming a Saturn-like ring
      if (Math.random() > 0.2) {
          // Sphere surface
          const phi = Math.acos(-1 + (2 * Math.random())); // Uniform sphere distro
          const theta = Math.sqrt(PARTICLE_COUNT * Math.PI) * phi;
          
          tSovereign[i3] = rSphere * Math.cos(theta) * Math.sin(phi);
          tSovereign[i3+1] = rSphere * Math.sin(theta) * Math.sin(phi);
          tSovereign[i3+2] = rSphere * Math.cos(phi);
      } else {
          // Orbital Ring
          const theta = Math.random() * Math.PI * 2;
          const rRing = rSphere * (1.4 + Math.random() * 0.4); // Ring extending out
          
          tSovereign[i3] = rRing * Math.cos(theta);
          tSovereign[i3+1] = (Math.random() - 0.5) * 0.15; // Flattened Y
          tSovereign[i3+2] = rRing * Math.sin(theta);
      }

      // --- Luxury Color Palette ---
      // Weighted towards Gold and Platinum, with sparse Electric Blue accents
      const mixFactor = Math.random();
      if (mixFactor > 0.7) {
         tempColor.copy(cGold);
      } else if (mixFactor > 0.25) {
         tempColor.copy(cPlatinum);
      } else {
         tempColor.copy(cBlue); // Rare blue accent
      }
      
      // Vary intensity for sparkling effect
      const intensity = 0.8 + Math.random() * 0.6;
      tempColor.multiplyScalar(intensity);
      
      col[i3] = tempColor.r;
      col[i3+1] = tempColor.g;
      col[i3+2] = tempColor.b;
    }

    return { positions: pos, colors: col, targets: [tSymbiosis, tMerkaba, tSovereign] };
  }, []);

  useFrame((state) => {
    if (!pointsRef.current) return;
    
    // Majestic, slow time scale for executive presence
    const time = state.clock.getElapsedTime() * 0.5;
    
    // Morph Cycle: Symbiosis -> Merkaba -> Sovereign -> Symbiosis
    const cycleDuration = 10;
    const totalCycles = 3;
    const progress = time % (cycleDuration * totalCycles);
    
    let currentTarget, nextTarget, mix;
    
    if (progress < cycleDuration) {
        // Phase 1: Structure (Helix) -> Strategy (Merkaba)
        currentTarget = targets[0];
        nextTarget = targets[1];
        mix = progress / cycleDuration;
    } else if (progress < cycleDuration * 2) {
        // Phase 2: Strategy (Merkaba) -> Command (Sovereign)
        currentTarget = targets[1];
        nextTarget = targets[2];
        mix = (progress - cycleDuration) / cycleDuration;
    } else {
        // Phase 3: Command (Sovereign) -> Structure (Helix)
        currentTarget = targets[2];
        nextTarget = targets[0];
        mix = (progress - cycleDuration * 2) / cycleDuration;
    }
    
    // Custom Easing: "The Magnetic Hold"
    // Holds the shape briefly at 0 and 1 to allow the viewer to appreciate the geometry
    const ease = (t: number) => {
        const hold = 0.15; // Hold for 15% of the duration at start/end
        if (t < hold) return 0;
        if (t > 1 - hold) return 1;
        
        // Remap internal range to 0-1
        const ft = (t - hold) / (1 - 2 * hold);
        // Cubic easing for the transition
        return ft < 0.5 ? 4 * ft * ft * ft : 1 - Math.pow(-2 * ft + 2, 3) / 2;
    };
    
    mix = ease(mix);

    const pos = pointsRef.current.geometry.attributes.position.array as Float32Array;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        const i3 = i * 3;
        const cx = currentTarget[i3]; const cy = currentTarget[i3+1]; const cz = currentTarget[i3+2];
        const nx = nextTarget[i3]; const ny = nextTarget[i3+1]; const nz = nextTarget[i3+2];
        
        let x = cx + (nx - cx) * mix;
        let y = cy + (ny - cy) * mix;
        let z = cz + (nz - cz) * mix;
        
        // Organic "Life" Noise
        // Subtle breathing motion, not chaotic scattering
        const noiseFreq = 0.4;
        const noiseAmp = 0.05; // Very subtle
        
        x += Math.sin(time * noiseFreq + y * 0.5) * noiseAmp;
        y += Math.cos(time * noiseFreq * 0.9 + z * 0.5) * noiseAmp;
        z += Math.sin(time * noiseFreq * 1.1 + x * 0.5) * noiseAmp;
        
        pos[i3] = x;
        pos[i3+1] = y;
        pos[i3+2] = z;
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true;
    
    // Slow, authoritative global rotation
    pointsRef.current.rotation.y = time * 0.08;
    pointsRef.current.rotation.z = Math.sin(time * 0.1) * 0.02; // Minimal tilt
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

export const PricingParticles = () => {
  return (
    <div className="fixed top-0 left-0 w-full h-full pointer-events-none z-0 overflow-hidden">
       {/* Fade out at bottom to blend seamless into page content */}
       <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-[#050505] to-transparent z-10"></div>
       
       <Canvas camera={{ position: [0, 0, 18], fov: 28 }} dpr={[1, 2]}>
          <color attach="background" args={['#050505']} />
          
          <Float speed={0.3} rotationIntensity={0.1} floatIntensity={0.1}>
              <AsymmetrySystem />
          </Float>
          
          {/* Additional gold sparkles for richness */}
          <Sparkles count={40} scale={12} size={2} speed={0.1} opacity={0.15} color={BrandColors.NeuralYellow} />
          
          <EffectComposer enableNormalPass={false}>
             <Bloom luminanceThreshold={0.2} mipmapBlur intensity={0.5} radius={0.5} />
             <Vignette eskil={false} offset={0.1} darkness={0.7} />
          </EffectComposer>
       </Canvas>
    </div>
  );
};