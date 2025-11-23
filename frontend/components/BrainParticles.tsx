'use client';

import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { BrandColors } from '../types/index';

interface BrainParticlesProps {
  scrollProgress: number;
}

export const BrainParticles: React.FC<BrainParticlesProps> = ({ scrollProgress }) => {
  const pointsRef = useRef<THREE.Points>(null);
  
  // Increase particle count for a denser, more premium look
  const count = 5000;

  // Pre-calculate positions for different morph targets
  const { positions, colors, targetShapes } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    
    // Define morphological targets
    // 0: Dual Spheres (Separated)
    // 1: Merged Sphere (Symbiosis)
    // 2: Torus/Galaxy (Agents/Network)
    // 3: Diamond/Octahedron (Command/Structure)
    
    const shapeDual = new Float32Array(count * 3);
    const shapeMerged = new Float32Array(count * 3);
    const shapeTorus = new Float32Array(count * 3);
    const shapeDiamond = new Float32Array(count * 3);

    const colorBlue = new THREE.Color(BrandColors.ElectricBlue);
    const colorGold = new THREE.Color(BrandColors.NeuralYellow);
    const colorPlatinum = new THREE.Color(BrandColors.Platinum);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      
      // --- Base Calculation Helpers ---
      const u = Math.random();
      const v = Math.random();
      const theta = 2 * Math.PI * u;
      const phi = Math.acos(2 * v - 1);

      // --- Shape 0: Dual Spheres ---
      const isLeft = i % 2 === 0;
      const rDual = 2.0; // Smaller radius for individual brains
      const offsetX = isLeft ? -2.5 : 2.5;
      
      shapeDual[i3] = offsetX + rDual * Math.sin(phi) * Math.cos(theta);
      shapeDual[i3 + 1] = rDual * Math.sin(phi) * Math.sin(theta);
      shapeDual[i3 + 2] = rDual * Math.cos(phi);

      // --- Shape 1: Merged Sphere ---
      const rMerged = 3.0; // Larger unified brain
      // Add some noise to make it look organic
      const rVar = rMerged + (Math.random() - 0.5) * 0.2;
      
      shapeMerged[i3] = rVar * Math.sin(phi) * Math.cos(theta);
      shapeMerged[i3 + 1] = rVar * Math.sin(phi) * Math.sin(theta);
      shapeMerged[i3 + 2] = rVar * Math.cos(phi);

      // --- Shape 2: Torus / Galaxy (Agents) ---
      // Torus parametric equation
      const tR = 4.5; // Major radius
      const tr = 0.8; // Minor radius
      const tTheta = u * Math.PI * 2;
      const tPhi = v * Math.PI * 2;
      
      shapeTorus[i3] = (tR + tr * Math.cos(tPhi)) * Math.cos(tTheta);
      shapeTorus[i3 + 1] = tr * Math.sin(tPhi); // Flattened
      shapeTorus[i3 + 2] = (tR + tr * Math.cos(tPhi)) * Math.sin(tTheta);
      
      // Scatter some particles inside the ring for volume
      if (Math.random() > 0.8) {
        shapeTorus[i3 + 1] *= 4; 
      }

      // --- Shape 3: Diamond / Octahedron (Structure) ---
      // Simple Octahedron logic: |x| + |y| + |z| = r
      // Generate random point in cube, project to octahedron surface
      let x = (Math.random() - 0.5) * 2;
      let y = (Math.random() - 0.5) * 2;
      let z = (Math.random() - 0.5) * 2;
      const dist = Math.abs(x) + Math.abs(y) + Math.abs(z);
      const scale = 3.5 / dist;
      
      shapeDiamond[i3] = x * scale;
      shapeDiamond[i3 + 1] = y * scale;
      shapeDiamond[i3 + 2] = z * scale;


      // --- Initialize Colors ---
      // Start with Dual Colors
      const c = isLeft ? colorBlue : colorGold;
      colors[i3] = c.r;
      colors[i3 + 1] = c.g;
      colors[i3 + 2] = c.b;
      
      // Set initial positions
      positions[i3] = shapeDual[i3];
      positions[i3 + 1] = shapeDual[i3 + 1];
      positions[i3 + 2] = shapeDual[i3 + 2];
    }
    
    return { 
      positions, 
      colors, 
      targetShapes: [shapeDual, shapeMerged, shapeTorus, shapeDiamond] 
    };
  }, []);

  useFrame((state) => {
    if (!pointsRef.current) return;

    const time = state.clock.getElapsedTime();
    const positionsAttr = pointsRef.current.geometry.attributes.position;
    const colorsAttr = pointsRef.current.geometry.attributes.color;
    
    // Determine active morph targets based on scroll
    // 0.0 - 0.25: Dual -> Merged
    // 0.25 - 0.50: Merged -> Torus
    // 0.50 - 0.75: Torus -> Diamond
    // 0.75 - 1.0: Diamond (Hold)
    
    let startIndex = 0;
    let endIndex = 1;
    let localProgress = 0;

    if (scrollProgress < 0.3) {
      startIndex = 0;
      endIndex = 1;
      localProgress = scrollProgress / 0.3; // 0 to 1
    } else if (scrollProgress < 0.6) {
      startIndex = 1;
      endIndex = 2;
      localProgress = (scrollProgress - 0.3) / 0.3;
    } else {
      startIndex = 2;
      endIndex = 3;
      localProgress = (scrollProgress - 0.6) / 0.4;
    }
    
    // Clamp progress
    localProgress = Math.min(Math.max(localProgress, 0), 1);
    
    // Easing for smoothness
    const ease = (t: number) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    const smoothProgress = ease(localProgress);

    const startShape = targetShapes[startIndex];
    const endShape = targetShapes[endIndex];

    // Color definitions
    const colorBlue = new THREE.Color(BrandColors.ElectricBlue);
    const colorGold = new THREE.Color(BrandColors.NeuralYellow);
    const colorPlatinum = new THREE.Color(BrandColors.Platinum);
    const colorWhite = new THREE.Color('#ffffff');
    const tempColor = new THREE.Color();

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;

      // --- Position Interpolation ---
      const sx = startShape[i3];
      const sy = startShape[i3+1];
      const sz = startShape[i3+2];
      
      const ex = endShape[i3];
      const ey = endShape[i3+1];
      const ez = endShape[i3+2];

      // Lerp
      let x = sx + (ex - sx) * smoothProgress;
      let y = sy + (ey - sy) * smoothProgress;
      let z = sz + (ez - sz) * smoothProgress;

      // Add calm breathing noise
      // Noise reduces as we get closer to shape 3 (Diamond) which represents order
      const structureFactor = Math.max(0, (scrollProgress - 0.6) * 2.5); // 0 -> 1 as we approach end
      const noiseAmp = 0.05 * (1 - structureFactor);
      
      // Slowed down time multiplier for calmer movement (was 1.5, 1.2, 1.3)
      x += Math.sin(time * 0.4 + y) * noiseAmp;
      y += Math.cos(time * 0.3 + x) * noiseAmp;
      z += Math.sin(time * 0.35 + z) * noiseAmp;

      positionsAttr.setXYZ(i, x, y, z);

      // --- Color Interpolation ---
      // Phase 0: Distinct Blue/Gold
      // Phase 1: Merging to Platinum/Mixed
      // Phase 2: Platinum with Electric accents
      // Phase 3: Pure Crystalline White/Gold
      
      const isLeft = i % 2 === 0;
      const baseColor = isLeft ? colorBlue : colorGold;

      if (scrollProgress < 0.3) {
        // Transition to Platinum
        tempColor.copy(baseColor).lerp(colorPlatinum, smoothProgress * 0.6);
      } else if (scrollProgress < 0.6) {
        // Platinum/Blue mix
        tempColor.copy(colorPlatinum).lerp(colorBlue, 0.2);
      } else {
        // Transition to Diamond (White/Gold)
        tempColor.copy(colorPlatinum).lerp(colorWhite, localProgress);
        // Add some gold sparkles
        if (i % 20 === 0) tempColor.lerp(colorGold, 0.5);
      }

      colorsAttr.setXYZ(i, tempColor.r, tempColor.g, tempColor.b);
    }

    positionsAttr.needsUpdate = true;
    colorsAttr.needsUpdate = true;

    // Gentle Global Rotation
    // Rotates faster in Phase 2 (Galaxy), slower in Phase 3 (Diamond)
    // Slowed down globally
    const rotSpeed = scrollProgress > 0.3 && scrollProgress < 0.6 ? 0.1 : 0.02;
    pointsRef.current.rotation.y += rotSpeed * 0.02;
    
    // Very slow oscillation
    pointsRef.current.rotation.z = Math.sin(time * 0.05) * 0.03;
    
    // Tilt based on scroll
    pointsRef.current.rotation.x = scrollProgress * 0.15;

  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={colors.length / 3}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.03} // Finer particles
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
};