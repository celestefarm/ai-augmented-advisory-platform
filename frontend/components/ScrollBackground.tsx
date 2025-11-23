'use client';

import React, { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { Experience } from './Experience';

export const ScrollBackground: React.FC = () => {
  const [scrollProgress, setScrollProgress] = useState(0);
  const pathname = usePathname();

  // Track scroll relative to total document height
  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
      const currentScroll = window.scrollY;
      // Normalize to 0-1
      const progress = totalHeight > 0 ? Math.min(Math.max(currentScroll / totalHeight, 0), 1) : 0;
      setScrollProgress(progress);
    };

    window.addEventListener('scroll', handleScroll);
    // Check on route change and resize
    handleScroll();
    window.addEventListener('resize', handleScroll);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleScroll);
    };
  }, [pathname]);

  // Hidden on Agents/Demo page for a clean look or distinct particles
  const hiddenRoutes = ['/agents', '/demo'];
  // Safe check in case pathname is undefined initially (though unlikely in client component)
  const isHidden = pathname ? hiddenRoutes.includes(pathname) : false;

  return (
    <div className={isHidden ? 'hidden' : 'block'}>
      <Experience scrollProgress={scrollProgress} />
    </div>
  );
};