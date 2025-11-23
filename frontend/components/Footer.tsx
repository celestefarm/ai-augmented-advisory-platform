'use client';

import React from 'react';
import { Linkedin } from 'lucide-react';
import { Logo } from './Logo';
import Link from 'next/link';

interface FooterProps {
  onNavigate?: (page: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  
  const handleNav = (e: React.MouseEvent, page: string) => {
    if (onNavigate) {
      e.preventDefault();
      onNavigate(page);
      window.scrollTo(0, 0);
    }
  };

  return (
    <section className="py-20 bg-[#050505] flex flex-col items-center relative pointer-events-auto border-t border-white/5 z-20">
        
        {/* Detailed Footer Grid */}
        <div className="w-full max-w-5xl px-6 grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-24 text-center md:text-left mb-16">
             <div className="flex flex-col gap-6 md:items-start items-center">
                 <div className="flex items-center gap-3">
                    <Logo className="w-8 h-8" />
                    <span className="text-white font-display text-lg tracking-[0.2em] font-bold">AI-AUGMENTED</span>
                 </div>
                 <span className="text-sm text-gray-500 uppercase tracking-widest leading-relaxed">
                   The Architecture of Power. <br/>
                   Ascend to Augmented.
                 </span>
                 <a href="https://www.linkedin.com/company/ai-augmented/" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-[#6e683b] transition-colors inline-block p-2 border border-white/5 hover:border-[#6e683b]/30">
                    <Linkedin size={18} strokeWidth={1.5} />
                 </a>
             </div>

            <div>
                <h4 className="text-white font-display text-sm tracking-[0.2em] uppercase mb-8 font-bold text-[#6e683b]">Protocol</h4>
                <ul className="space-y-4 text-xs text-gray-500 uppercase tracking-widest font-medium">
                    <li><Link href="/" onClick={(e) => handleNav(e, 'home')} className="hover:text-white transition-colors">Home</Link></li>
                    <li><Link href="/about" onClick={(e) => handleNav(e, 'about')} className="hover:text-white transition-colors">About</Link></li>
                    <li><Link href="/agents" onClick={(e) => handleNav(e, 'agents')} className="hover:text-white transition-colors">The Council</Link></li>
                    <li><Link href="/pricing" onClick={(e) => handleNav(e, 'pricing')} className="hover:text-white transition-colors">Membership</Link></li>
                </ul>
            </div>

             <div>
                 <h4 className="text-white font-display text-sm tracking-[0.2em] uppercase mb-8 font-bold text-[#6e683b]">Secure Comms</h4>
                 <ul className="space-y-4 text-xs text-gray-500 tracking-widest font-medium">
                    <li><Link href="/privacy" onClick={(e) => handleNav(e, 'privacy')} className="hover:text-white transition-colors uppercase">Privacy Policy</Link></li>
                    <li><Link href="/terms" onClick={(e) => handleNav(e, 'terms')} className="hover:text-white transition-colors uppercase">Terms of Service</Link></li>
                    <li className="hover:text-white transition-colors cursor-pointer pt-4 border-t border-white/5">info@aiaugmented.io</li>
                 </ul>
            </div>
        </div>
        
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-px bg-gradient-to-r from-transparent via-[#6e683b]/50 to-transparent"></div>
          <div className="text-[10px] text-gray-700 tracking-[0.3em] uppercase font-bold">
            AI-Augmented © 2025 // System Active
          </div>
        </div>
      </section>
  );
};