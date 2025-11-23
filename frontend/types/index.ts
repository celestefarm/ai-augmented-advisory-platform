export type Theme = "light" | "dark" | "system";

export interface Message {
  id?: string;
  sender: "user" | "ai";
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  error?: boolean;
  metadata?: {
    response_time: number;
    total_tokens: number;
    cost: number;
    model: string;
    chunks_sent: number;
  };
  confidence?: {
    level: string;
    percentage: number;
    explanation: string;
  };
  responseId?: string;
}
import React from 'react';
import type { ThreeElements } from '@react-three/fiber';

// Augment React's JSX namespace to include Three.js elements (mesh, group, etc.)
// We use module augmentation on 'react' to ensure we merge with standard IntrinsicElements (div, span, etc.)
// rather than overwriting the global namespace which causes "Property 'div' does not exist" errors.
declare module 'react' {
  namespace JSX {
    interface IntrinsicElements extends ThreeElements {}
  }
}

export enum BrandColors {
  DeepBlack = '#050505',
  ElectricBlue = '#00f0ff',
  NeuralYellow = '#ffd700',
  Platinum = '#e0e0e0',
  GlassBorder = 'rgba(255, 255, 255, 0.1)',
  GlassBg = 'rgba(255, 255, 255, 0.03)',
}

export interface ScrollState {
  progress: number; // 0 to 1 overall
  scrollY: number;
}

export interface AgentData {
  id: number;
  title: string;
  role: string;
  icon: string;
}
