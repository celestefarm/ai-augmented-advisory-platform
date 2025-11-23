
import React from 'react';

interface LogoProps {
  className?: string;
}

export const Logo: React.FC<LogoProps> = ({ className = "w-8 h-8" }) => {
  return (
    <svg 
      viewBox="0 0 50 50" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg" 
      className={className}
    >
      <defs>
        <filter id="glow-gold" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {/* The Human Vector (Left - Platinum/White) */}
      {/* Represents Structure and Intent */}
      <path 
        d="M 25 4 L 11 44" 
        stroke="currentColor" 
        strokeWidth="2.5" 
        strokeLinecap="square"
        className="text-white opacity-90"
      />

      {/* The AI Vector (Right - Gold) */}
      {/* Represents Intelligence and Value */}
      <path 
        d="M 25 4 L 39 44" 
        stroke="#6e683b" 
        strokeWidth="2.5" 
        strokeLinecap="square"
        style={{ filter: 'drop-shadow(0 0 8px rgba(110,104,59,0.3))' }}
      />

      {/* The Crystalized Strategy (Center Diamond) */}
      {/* Represents the output of the symbiosis */}
      <path 
        d="M 25 20 L 29 26 L 25 32 L 21 26 Z" 
        fill="#6e683b"
        className="animate-pulse"
        style={{ animationDuration: '3s' }}
      />
      
      {/* The Foundation Line (Subtle Connection) */}
      {/* Optional: Adds weight to the bottom, grounded in reality */}
      <path 
        d="M 18 36 L 32 36" 
        stroke="url(#gradient-shine)" 
        strokeWidth="0.5" 
        strokeOpacity="0.5"
      />

      <defs>
        <linearGradient id="gradient-shine" x1="18" y1="36" x2="32" y2="36" gradientUnits="userSpaceOnUse">
          <stop stopColor="white" stopOpacity="0" />
          <stop offset="0.5" stopColor="white" />
          <stop offset="1" stopColor="white" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  );
};
