'use client';

import React from 'react';
import { Footer } from './Footer';
import { OriginParticles } from './OriginParticles';
import { 
  Brain, Cpu, Shield, Zap, Terminal, 
  Target, Lock, 
  ChevronRight, Scale,
  FileText,
  Activity,
  Linkedin,
  Quote,
  Fingerprint
} from 'lucide-react';
import { motion } from 'framer-motion';

interface AboutPageProps {
  onNavigate?: (page: string) => void;
}

// Local GlassContainer to avoid circular dependencies and ensure stability
const GlassContainer = ({ children, className = "" }: { children?: React.ReactNode, className?: string }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.8 }}
    className={`p-8 md:p-12 bg-white/[0.02] backdrop-blur-xl border border-white/10 shadow-[0_0_50px_rgba(255,255,255,0.02)] rounded-sm ${className}`}
  >
    {children}
  </motion.div>
);

// Sub-components defined locally
const StatBox = ({ value, label }: { value: string, label: string }) => (
   <div className="p-8 bg-[#050505] flex flex-col justify-center items-center text-center group hover:bg-[#0a0a0a] transition-colors border border-white/5">
      <div className="text-4xl md:text-5xl font-light text-white mb-3 group-hover:text-[#6e683b] transition-colors font-display">{value}</div>
      <div className="text-sm text-gray-500 uppercase tracking-widest">{label}</div>
   </div>
);

const SymbiosisNode = ({ icon: Icon, title, subtitle, features }: any) => (
   <div className="p-8 bg-white/[0.01] border border-white/5 text-center h-full flex flex-col items-center justify-center hover:border-white/10 transition-all">
      <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-6 text-gray-400">
         <Icon size={22} strokeWidth={1} />
      </div>
      <h3 className="text-white font-display text-xl mb-2">{title}</h3>
      <p className="text-sm text-[#6e683b] uppercase tracking-widest mb-6 font-bold">{subtitle}</p>
      <ul className="text-base text-gray-500 space-y-4 font-light">
         {features.map((f: string, i: number) => (
            <li key={i} className="border-b border-white/5 pb-2 last:border-0 last:pb-0">{f}</li>
         ))}
      </ul>
   </div>
);

const ProtocolCard = ({ step, title, icon: Icon, desc }: any) => (
   <div className="p-10 bg-[#050505]/80 backdrop-blur-sm border border-white/10 hover:bg-[#050505] hover:border-white/20 transition-all duration-500 group relative overflow-hidden">
      <div className="absolute top-4 right-4 text-sm font-mono text-[#6e683b] opacity-50 font-bold">STEP {step}</div>
      <Icon className="w-8 h-8 text-gray-600 mb-8 group-hover:text-[#6e683b] transition-colors" strokeWidth={1} />
      <h3 className="text-xl font-display text-white mb-4">{title}</h3>
      <p className="text-base text-gray-400 font-light leading-loose group-hover:text-gray-300 transition-colors">
         {desc}
      </p>
   </div>
);

export const AboutPage: React.FC<AboutPageProps> = ({ onNavigate }) => {
  return (
    <div className="relative w-full min-h-screen bg-[#050505] overflow-x-hidden text-white isolate">
      
      {/* 1. HERO: THE MANIFESTO */}
      <section className="relative pt-48 pb-32 px-6 flex flex-col items-center text-center z-10 min-h-[80vh] justify-center overflow-hidden">
        
        {/* Background Visual */}
        <div className="absolute inset-0 w-full h-full pointer-events-none select-none z-0">
           <img 
             src="https://images.unsplash.com/photo-1586165368502-1bad197a6461?q=80&w=2600&auto=format&fit=crop"
             alt="Strategic Chess Game" 
             className="w-full h-full object-cover opacity-80 grayscale scale-[1.6] -translate-y-[20%] object-center"
           />
           <div className="absolute inset-0 bg-gradient-to-b from-[#050505] via-[#050505]/60 to-[#050505]"></div>
           <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#050505_100%)] opacity-80"></div>
        </div>

        <div className="mb-12 animate-fade-in relative z-10">
          <div className="absolute -left-4 -top-4 w-2 h-2 border-t border-l border-[#6e683b]/50"></div>
          <div className="absolute -right-4 -bottom-4 w-2 h-2 border-b border-r border-[#6e683b]/50"></div>
          <span className="inline-block py-2 px-6 bg-white/[0.02] border border-white/5 backdrop-blur-sm text-[#6e683b] text-sm tracking-[0.4em] uppercase font-bold shadow-[0_0_25px_rgba(110,104,59,0.5)]">
            The Second Mind
          </span>
        </div>

        <h1 className="text-5xl md:text-7xl font-display font-light text-white mb-12 leading-tight tracking-tight max-w-6xl mx-auto relative z-10">
          We do not replace the executive. <span className="italic text-gray-500">We weaponize them.</span>
        </h1>

        <p className="text-gray-400 text-lg md:text-xl font-light leading-loose max-w-3xl mx-auto tracking-wide border-l-2 border-[#6e683b]/30 pl-6 text-left md:text-center md:border-l-0 md:pl-0 relative z-10">
          You are not a processor of data. You are an architect of strategy. We do not replace your judgment. We purify it. We strip away the noise and the hesitation, leaving you with the absolute clarity to command.
        </p>
      </section>

      {/* 2. THE REALITY */}
      <section className="py-32 px-6 relative z-20 bg-[#050505]">
         <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
            <div className="relative z-10">
               <span className="text-[#6e683b] text-sm uppercase tracking-[0.3em] mb-6 block font-bold">The Biological Limit</span>
               <h2 className="text-4xl md:text-5xl font-display text-white mb-8 leading-tight">The Cognitive <br/> Ceiling</h2>
               <div className="space-y-6 text-lg text-gray-400 font-light leading-loose">
                 <p>
                    The modern executive is operating in a theater of infinite noise. Market signals, geopolitical fractures, and operational data now flow faster than human cognition can synthesize.
                 </p>
                 <p>
                    Expanding your team only multiplies the friction. You do not need more opinions; you need aggressive filtering. You need an architecture that strips away the irrelevant.
                 </p>
               </div>
            </div>
            
            <div className="relative">
                <div className="grid grid-cols-2 gap-px bg-white/10 border border-white/10">
                   <StatBox value="2.5 EB" label="Daily Data Creation" />
                   <StatBox value="40%" label="Decision Paralysis" />
                   <StatBox value="< 24h" label="News Relevance" />
                   <StatBox value="Zero" label="Error Tolerance" />
                </div>
                {/* Decorative elements behind */}
                <div className="absolute -z-10 -inset-4 bg-gradient-to-tr from-[#6e683b]/10 to-transparent blur-xl"></div>
            </div>
         </div>
      </section>

      {/* 3. THE ARCHITECTURE: SYMBIOSIS */}
      <section className="py-40 px-6 bg-[#080808] relative overflow-hidden z-20">
         {/* Subtle Grid Background */}
         <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)', backgroundSize: '60px 60px' }}></div>

         <div className="max-w-6xl mx-auto relative z-10">
            <div className="text-center mb-24">
               <h2 className="text-4xl font-display text-white mb-6">The Architecture of Symbiosis</h2>
               <p className="text-base text-gray-500 uppercase tracking-[0.3em]">Silicon Speed + Carbon Wisdom</p>
            </div>

            <div className="relative grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
               {/* Connection Lines */}
               <div className="hidden md:block absolute top-1/2 left-0 w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent -z-10"></div>
               
               {/* Node 1: Machine */}
               <SymbiosisNode 
                 icon={Cpu} 
                 title="The Engine" 
                 subtitle="AI & Compute"
                 features={["Infinite Pattern Matching", "Zero Emotional Bias", "24/7 Processing"]}
               />

               {/* Node 2: Bridge (Center) */}
               <div className="relative z-10 transform scale-110">
                 <div className="aspect-square flex flex-col items-center justify-center bg-[#0a0a0a] border border-[#6e683b]/30 shadow-[0_0_50px_rgba(110,104,59,0.1)] p-8 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-[#6e683b]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                    <Zap className="w-14 h-14 text-[#6e683b] mb-6" strokeWidth={1} />
                    <h3 className="text-white font-display text-xl mb-2 tracking-widest uppercase">Synthesis</h3>
                    <p className="text-sm text-center text-gray-400 leading-relaxed">
                       Where raw computation meets strategic intent.
                    </p>
                 </div>
               </div>

               {/* Node 3: Human */}
               <SymbiosisNode 
                 icon={Brain} 
                 title="The Architect" 
                 subtitle="Executive Mind"
                 features={["Moral & Ethical Weight", "Nuanced Context", "Final Accountability"]}
               />
            </div>
         </div>
      </section>

      {/* STICKY WRAPPER REFACTOR */}
      <div className="relative w-full">
         
         {/* Sticky Background - z-0 allows it to be seen above the root background but below z-10 content */}
         <div className="sticky top-0 left-0 h-screen w-full z-0 overflow-hidden">
             <OriginParticles />
             {/* Gradient fade to blend seamlessly with black sections above and below */}
             <div className="absolute inset-0 bg-gradient-to-b from-[#050505] via-transparent to-[#050505] opacity-80 pointer-events-none"></div>
         </div>

         {/* Content that scrolls over the sticky background */}
         <div className="relative z-10 -mt-[100vh] pointer-events-none">
            
            {/* 4. THE ORIGIN: FOUNDER STORY */}
            <section className="min-h-screen flex items-end pb-24 px-6 pointer-events-auto">
                <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2">
                   <div className="max-w-md bg-black/40 backdrop-blur-md border border-white/10 p-8 shadow-[0_0_60px_rgba(0,0,0,0.5)] relative overflow-hidden rounded-sm transition-all duration-1000 hover:bg-black/60">
                      <div className="absolute inset-0 bg-gradient-to-b from-white/[0.03] to-transparent pointer-events-none"></div>
                      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#6e683b] to-transparent opacity-50"></div>

                      <div className="mb-6">
                          <h2 className="text-2xl md:text-3xl font-display text-white leading-tight">The Origin</h2>
                      </div>

                      <div className="relative mb-6">
                         <Quote size={24} className="absolute -top-4 -left-2 text-[#6e683b]/30 transform -scale-x-100" />
                         <p className="text-lg font-light text-white italic leading-relaxed pl-6 border-l-2 border-[#6e683b]">
                            "I built the advisor I couldn't hire."
                         </p>
                      </div>

                      <div className="space-y-4 text-sm md:text-base text-white/80 font-light leading-relaxed mb-6">
                         <p>
                            "As a strategist, I found myself in a paradox. The higher I climbed, the more isolated my decision-making became. 
                            Consultants gave me generic playbooks. My team gave me what they thought I wanted to hear."
                         </p>
                         <p>
                            "I needed a partner that was ruthless, sleepless, and unburdened by politics."
                         </p>
                      </div>

                      <div className="flex items-center gap-6 pt-6 border-t border-white/10">
                         <div className="flex flex-col">
                            <span className="font-display text-white text-base tracking-widest uppercase">Celeste Farm</span>
                            <span className="text-xs text-white/60 uppercase tracking-[0.2em]">Founder & Architect</span>
                         </div>
                          <a 
                            href="https://www.linkedin.com/in/celestefarm" 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="p-2 border border-white/10 hover:bg-white hover:text-black transition-all duration-300"
                          >
                            <Linkedin size={16} strokeWidth={1.5} />
                          </a>
                      </div>
                   </div>
                </div>
            </section>

            {/* 5. THE PROTOCOL */}
            <section className="py-32 px-6 pointer-events-auto bg-gradient-to-b from-transparent to-[#050505]">
               <div className="max-w-6xl mx-auto">
                  <div className="flex flex-col md:flex-row justify-between items-end mb-20 border-b border-white/10 pb-8 bg-black/40 backdrop-blur-md p-8 rounded-sm border border-white/5">
                     <div>
                       <span className="text-[#6e683b] text-sm uppercase tracking-[0.3em] mb-4 block font-bold">The Daily Workflow</span>
                       <h2 className="text-3xl font-display text-white">Structured for Command</h2>
                     </div>
                     <p className="text-base text-gray-500 uppercase tracking-widest mt-6 md:mt-0">From Ingest to Execution</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                     <ProtocolCard 
                       step="01"
                       title="Ingest"
                       icon={FileText}
                       desc="Upload board decks, P&Ls, or raw strategic memos. The system parses context instantly, building a private knowledge graph."
                     />
                     <ProtocolCard 
                       step="02"
                       title="Stress Test"
                       icon={Scale}
                       desc="The 'Devil's Advocate' agent relentlessly attacks your assumptions. It identifies liquidity risks, cultural friction, and market blindspots."
                     />
                     <ProtocolCard 
                       step="03"
                       title="Refine"
                       icon={Target}
                       desc="You receive a fortified strategy. Pre-defended against skepticism. Ready for the board. Ready for the market."
                     />
                  </div>
               </div>
            </section>
         </div>
      </div>

      {/* 6. SOVEREIGNTY: PRIVACY */}
      <section className="py-32 px-6 relative z-10 bg-[#050505]">
         <GlassContainer className="max-w-5xl mx-auto border border-white/10 bg-gradient-to-br from-white/[0.02] to-transparent">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
                 <div>
                    <div className="flex items-center gap-3 mb-6">
                       <Shield className="w-6 h-6 text-[#6e683b]" strokeWidth={1} />
                       <span className="text-sm text-white uppercase tracking-[0.3em] font-bold">Sovereignty Architecture</span>
                    </div>
                    <h2 className="text-3xl font-display text-white mb-6">Zero-Retention Guarantee</h2>
                    <p className="text-lg text-gray-300 font-light leading-loose mb-8">
                       The greatest risk to the modern enterprise is IP leakage. 
                       We have built a "Zero-Retention" architecture. 
                       Your strategic data is processed in a transient state and <span className="text-white border-b border-white/20">never used to train our public models</span>.
                    </p>
                    
                    <div className="grid grid-cols-2 gap-6">
                       <div className="p-5 border border-white/5 bg-black/20">
                          <Lock size={18} className="text-[#6e683b] mb-3" />
                          <h4 className="text-sm text-white uppercase tracking-widest mb-2">Air-Gapped</h4>
                          <p className="text-sm text-gray-500">Isolated Context</p>
                       </div>
                       <div className="p-5 border border-white/5 bg-black/20">
                          <Activity size={18} className="text-[#6e683b] mb-3" />
                          <h4 className="text-sm text-white uppercase tracking-widest mb-2">Transient</h4>
                          <p className="text-sm text-gray-500">No Long-Term Storage</p>
                       </div>
                    </div>
                 </div>
                 
                 {/* Visual representation of isolation */}
                 <div className="flex justify-center">
                    <div className="relative w-64 h-64">
                       <div className="absolute inset-0 border border-[#6e683b]/20 rounded-full animate-spin" style={{ animationDuration: '12s' }}></div>
                       <div className="absolute inset-4 border border-dashed border-white/10 rounded-full"></div>
                       <div className="absolute inset-0 flex items-center justify-center">
                          <Shield className="w-16 h-16 text-white opacity-80" strokeWidth={0.5} />
                       </div>
                       <div className="absolute inset-0 animate-spin" style={{ animationDuration: '8s' }}>
                          <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2">
                              <div className="w-3 h-3 bg-[#6e683b] rounded-full shadow-[0_0_25px_#6e683b] animate-pulse"></div>
                          </div>
                       </div>
                    </div>
                 </div>
              </div>
         </GlassContainer>
      </section>

      {/* 7. CTA: THE INVITATION */}
      <section className="py-40 px-6 relative overflow-hidden text-center bg-[#050505] z-10">
         <div className="relative z-10 max-w-3xl mx-auto">
            <h2 className="text-5xl md:text-7xl font-display text-white mb-8 tracking-tight">Command the Future</h2>
            <div className="h-px w-24 bg-gradient-to-r from-transparent via-[#6e683b] to-transparent mx-auto mb-8"></div>
            <p className="text-lg text-gray-400 leading-loose mb-12 font-light max-w-xl mx-auto">
               The era of the lone genius is over. <br/> The era of the Augmented Executive has begun. 
            </p>
            
            <button 
               onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLScph-EGBWK_FMyLzNIypqCA5IfJOcWdKFHOw0D-v1n8zgIWFA/viewform', '_blank')}
               className="group relative inline-flex items-center gap-4 px-12 py-6 bg-white text-black overflow-hidden hover:bg-[#6e683b] hover:text-white transition-all duration-500"
            >
               <span className="relative z-10 text-base font-bold uppercase tracking-[0.3em]">Initiate Protocol</span>
               <ChevronRight size={16} className="relative z-10 group-hover:translate-x-1 transition-transform" />
            </button>
         </div>
      </section>

      <Footer onNavigate={onNavigate} />
    </div>
  );
};