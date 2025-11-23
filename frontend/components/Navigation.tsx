'use client';

import React, { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import { Logo } from './Logo';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '../lib/utils';

interface NavigationProps {
  currentPage?: string;
  onNavigate?: (page: string) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ currentPage: propCurrentPage, onNavigate }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  // Determine current page. Priority: Prop > Pathname > Default
  // This supports both the Next.js Router (standard) and the manual App.tsx (SPA mode) usage.
  const safePathname = pathname || '/';
  const computedPage = safePathname === '/' ? 'home' : safePathname.replace('/', '');
  const activePage = propCurrentPage || computedPage;

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleJoinBeta = () => {
    window.open('https://docs.google.com/forms/d/e/1FAIpQLScph-EGBWK_FMyLzNIypqCA5IfJOcWdKFHOw0D-v1n8zgIWFA/viewform', '_blank');
    setMobileMenuOpen(false);
  };

  const handleLinkClick = (e: React.MouseEvent, page: string) => {
    // If onNavigate is provided (App.tsx mode), override default navigation
    if (onNavigate) {
      e.preventDefault();
      onNavigate(page);
    }
    setMobileMenuOpen(false);
  };

  return (
    <nav
      className={`fixed top-0 w-full z-50 transition-all duration-1000 ${
        scrolled
          ? 'py-4 bg-black/40 backdrop-blur-xl'
          : 'py-8 bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-8 flex justify-between items-center">
        
        {/* Brand Identity Lockup */}
        <Link href="/" onClick={(e) => handleLinkClick(e, 'home')}>
          <div className="group flex items-center gap-4 cursor-pointer">
            <div className="relative">
              <Logo className="w-10 h-10 transition-transform duration-700 group-hover:scale-110 group-hover:rotate-180" />
              <div className="absolute inset-0 bg-[#6e683b] blur-xl opacity-0 group-hover:opacity-20 transition-opacity duration-700"></div>
            </div>
            
            <div className="flex flex-col">
              <span className="text-lg font-light tracking-[0.25em] font-display text-white group-hover:text-[#6e683b] transition-colors duration-700 leading-none">
                AI-AUGMENTED
              </span>
              <span className="text-[0.6rem] text-gray-500 uppercase tracking-[0.4em] mt-1 group-hover:text-white transition-colors duration-700 opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0">
                Command Intelligence
              </span>
            </div>
          </div>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex gap-12 items-center text-sm tracking-[0.2em] font-medium text-gray-500">
          {['home', 'about', 'agents', 'pricing', 'demo'].map((page) => (
            <Link
              key={page}
              href={page === 'home' ? '/' : `/${page}`}
              onClick={(e) => handleLinkClick(e, page)}
              className={cn(
                "hover:text-white transition-colors duration-500 uppercase relative group",
                activePage === page && "text-white"
              )}
            >
              {page}
              <span className={cn(
                "absolute -bottom-2 left-0 w-full h-px bg-[#6e683b] transform origin-left transition-transform duration-500",
                activePage === page ? "scale-x-100" : "scale-x-0 group-hover:scale-x-50"
              )}></span>
            </Link>
          ))}
          
          <button 
            onClick={handleJoinBeta}
            className="px-6 py-2 border border-[#6e683b]/20 text-[#6e683b] hover:bg-[#6e683b] hover:text-black transition-all duration-500 uppercase tracking-[0.15em] text-sm font-bold"
          >
            Join Beta
          </button>
        </div>

        {/* Mobile Toggle */}
        <button 
          className="md:hidden text-white/80 hover:text-white transition-colors"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={20} strokeWidth={1} /> : <Menu size={20} strokeWidth={1} />}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="absolute top-0 left-0 w-full h-screen bg-[#050505] flex flex-col items-center justify-center gap-12 md:hidden z-40">
           <Logo className="w-16 h-16 mb-4" />
           {['home', 'about', 'agents', 'pricing', 'demo'].map((page) => (
             <Link 
                key={page}
                href={page === 'home' ? '/' : `/${page}`}
                onClick={(e) => handleLinkClick(e, page)}
                className={cn(
                  "text-white text-2xl font-display font-light tracking-[0.2em] uppercase transition-colors",
                  activePage === page ? "text-[#6e683b]" : "text-white"
                )}
              >
                {page}
              </Link>
           ))}
          <button 
            onClick={handleJoinBeta}
            className="px-8 py-3 border border-[#6e683b]/20 text-[#6e683b] text-xl font-display font-light tracking-[0.2em] uppercase hover:bg-[#6e683b]/10 transition-all mt-4"
          >
            JOIN BETA
          </button>
        </div>
      )}
    </nav>
  );
};