'use client';

import React, { useState } from 'react';
import { Footer } from './Footer';
import { DemoParticles } from './DemoParticles';
import { Terminal, Activity, Lock, Globe, Shield, Zap, FileText, Cpu, ArrowRight } from 'lucide-react';
import Link from 'next/link';

interface DemoPageProps {
  onNavigate?: (page: string) => void;
}

// Simulation Scenarios (Keep for background visuals)
const SCENARIOS = [
  {
    id: 'hostile_takeover',
    title: 'Hostile Takeover Defense',
    description: 'Competitor (Market Cap: $40B) is accumulating stock. Volume +400% vs avg.',
    urgency: 'CRITICAL',
  },
  {
    id: 'supply_chain',
    title: 'Supply Chain Collapse',
    description: 'Key chip supplier in Taiwan signals 8-week delay due to geopolitical blockade.',
    urgency: 'HIGH',
  },
  {
    id: 'pr_crisis',
    title: 'Data Leak Crisis',
    description: 'Ransomware group claims to have user database. Proof sample verified.',
    urgency: 'EXTREME',
  }
];

export const DemoPage: React.FC<DemoPageProps> = ({ onNavigate }) => {
  // Static state for background preview
  const [selectedScenario] = useState(SCENARIOS[0]);

  return (
    <div className="relative w-full min-h-screen bg-[#050505] overflow-x-hidden text-white">
      
      <DemoParticles />

      {/* 1. Hero / Context */}
      <section className="pt-48 pb-20 px-6 relative z-10 flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 border border-[#00f0ff]/30 bg-[#00f0ff]/5 rounded-full mb-8 animate-fade-in">
           <div className="w-2 h-2 bg-[#00f0ff] rounded-full animate-pulse"></div>
           <span className="text-[#00f0ff] text-xs font-mono tracking-[0.2em] uppercase">System Preview</span>
        </div>
        
        <h1 className="text-4xl md:text-6xl font-display font-light text-white mb-8 leading-tight">
          Live Strategic <span className="text-gray-500 italic">Simulation</span>
        </h1>
        
        <p className="text-gray-400 text-lg font-light max-w-2xl mx-auto leading-relaxed mb-12">
           Experience the Council's asynchronous processing. Observe how five distinct AI agents deconstruct risk, opportunity, and execution in milliseconds.
        </p>
      </section>

      {/* 2. The Interface (LOCKED) */}
      <section className="pb-32 px-6 relative z-10">
         <div className="max-w-6xl mx-auto relative">
            
            {/* OVERLAY */}
            <div className="absolute inset-0 z-50 flex items-center justify-center">
                <div className="p-1 bg-gradient-to-br from-[#6e683b]/50 via-transparent to-[#6e683b]/10 rounded-sm">
                    <div className="bg-[#050505]/90 backdrop-blur-xl border border-[#6e683b]/30 p-10 md:p-16 text-center shadow-[0_0_50px_rgba(110,104,59,0.15)] max-w-lg relative overflow-hidden">
                        {/* Premium Shine Effect */}
                        <div className="absolute top-0 left-[-100%] w-full h-full bg-gradient-to-r from-transparent via-white/5 to-transparent animate-[shine_3s_infinite]"></div>

                        <Lock className="w-12 h-12 text-[#6e683b] mx-auto mb-6 opacity-80" strokeWidth={1} />
                        
                        <h2 className="text-3xl md:text-4xl font-display text-white mb-4 tracking-widest">COMING SOON</h2>
                        
                        <div className="h-px w-16 bg-[#6e683b]/50 mx-auto mb-6"></div>
                        
                        <p className="text-gray-400 text-sm leading-loose uppercase tracking-widest mb-8">
                            This module is currently restricted to internal testing and Founding Members.
                        </p>
                        
                        <button 
                            onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLScph-EGBWK_FMyLzNIypqCA5IfJOcWdKFHOw0D-v1n8zgIWFA/viewform', '_blank')}
                            className="group relative inline-flex items-center gap-3 px-8 py-4 bg-[#6e683b] text-black text-sm font-bold uppercase tracking-[0.2em] hover:bg-white transition-all duration-500"
                        >
                            <span className="relative z-10">Join Beta</span>
                            <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform relative z-10" />
                        </button>
                    </div>
                </div>
            </div>

            {/* BACKGROUND UI (BLURRED) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 blur-sm opacity-30 pointer-events-none select-none">
                
                {/* Left: Scenario Selector */}
                <div className="lg:col-span-1 space-y-4">
                   <div className="p-6 bg-[#0a0a0a]/80 border border-white/10 rounded-sm">
                      <div className="flex items-center gap-3 mb-6">
                         <Activity size={18} className="text-[#6e683b]" />
                         <span className="text-sm font-display text-white tracking-[0.2em] uppercase">Active Threats</span>
                      </div>
                      <div className="space-y-3">
                         {SCENARIOS.map((scenario) => (
                            <div key={scenario.id} className={`w-full text-left p-4 border ${selectedScenario.id === scenario.id ? 'bg-[#6e683b]/10 border-[#6e683b] text-white' : 'border-white/5 text-gray-500'}`}>
                               <div className="flex justify-between items-center mb-2">
                                  <span className="text-xs font-mono opacity-70 uppercase tracking-wider">{scenario.urgency}</span>
                               </div>
                               <h4 className="font-display text-sm tracking-wide">{scenario.title}</h4>
                            </div>
                         ))}
                      </div>
                   </div>

                   {/* System Status */}
                   <div className="p-6 bg-[#0a0a0a]/80 border border-white/10 rounded-sm">
                       <div className="space-y-4 font-mono text-xs text-gray-500">
                           <div className="flex justify-between"><span>CPU_LOAD</span><span className="text-[#00f0ff]">14%</span></div>
                           <div className="flex justify-between"><span>LATENCY</span><span className="text-[#00f0ff]">42ms</span></div>
                           <div className="flex justify-between"><span>ENCRYPTION</span><span className="text-green-500">AES-256</span></div>
                       </div>
                   </div>
                </div>

                {/* Right: The Terminal */}
                <div className="lg:col-span-2">
                   <div className="h-[600px] flex flex-col bg-[#050505] border border-white/20 shadow-2xl relative overflow-hidden rounded-sm">
                       <div className="bg-[#0a0a0a] border-b border-white/10 p-4 flex justify-between items-center">
                           <div className="flex items-center gap-3">
                               <Terminal size={16} className="text-gray-400" />
                               <span className="text-xs font-mono text-gray-400">COUNCIL_V.2.0 // OFFLINE</span>
                           </div>
                           <div className="flex gap-2">
                               <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50"></div>
                               <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
                               <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50"></div>
                           </div>
                       </div>

                       <div className="flex-1 p-6 md:p-8 font-mono text-sm relative">
                           <div className="mb-8 pb-6 border-b border-white/10">
                               <h3 className="text-[#6e683b] mb-2 text-lg tracking-widest uppercase">Mission Context</h3>
                               <p className="text-gray-300 leading-relaxed text-base">{selectedScenario.description}</p>
                           </div>
                           <div className="text-gray-500 italic">System currently in standby mode. Authorization required to initialize simulation logic.</div>
                       </div>

                       <div className="bg-[#0a0a0a] border-t border-white/10 p-3 flex justify-between items-center text-xs font-mono text-gray-600">
                           <span>STATUS: STANDBY</span>
                           <span>LINK STABLE</span>
                       </div>
                   </div>
                </div>
            </div>

         </div>
      </section>

      {/* 3. Capabilities Grid */}
      <section className="py-20 px-6 bg-[#0a0a0a] border-t border-white/10 relative z-10">
         <div className="max-w-5xl mx-auto text-center mb-16">
             <h2 className="text-2xl font-display text-white mb-4">Beyond Simulation</h2>
             <p className="text-gray-500 uppercase tracking-widest text-sm">Real world capabilities included in the protocol</p>
         </div>
         <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-px bg-white/10 border border-white/10">
             <CapabilityBox icon={Globe} title="Global Macro Ingest" desc="Real-time parsing of 50,000+ news sources and geopolitical feeds." />
             <CapabilityBox icon={Shield} title="Risk Quantification" desc="Monte Carlo simulations to predict probability of ruin." />
             <CapabilityBox icon={FileText} title="Board-Ready Memos" desc="One-click generation of defended strategic artifacts." />
             <CapabilityBox icon={Zap} title="Scenario War-Gaming" desc="Adversarial stress-testing of your strategic assumptions." />
             <CapabilityBox icon={Cpu} title="Bias Removal" desc="Algorithmic stripping of 'Group Think' and cognitive bias." />
             <CapabilityBox icon={Lock} title="Zero-Retention" desc="Your data is processed in a transient state. No training." />
         </div>
      </section>

      <Footer onNavigate={onNavigate} />
    </div>
  );
};

const CapabilityBox = ({ icon: Icon, title, desc }: any) => (
   <div className="bg-[#050505] p-8 group hover:bg-[#0a0a0a] transition-colors">
       <Icon className="w-8 h-8 text-[#6e683b] mb-6 opacity-60 group-hover:opacity-100 transition-opacity" strokeWidth={1} />
       <h3 className="text-white font-display text-base mb-3">{title}</h3>
       <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
   </div>
);