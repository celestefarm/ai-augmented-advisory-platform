'use client';

import React from 'react';
import { ArrowDown, Shield, Zap, Activity, Users, FileText, Layout, Scale, Sword, BrainCircuit, Fingerprint, Anchor, Compass } from 'lucide-react';
import { Footer } from './Footer';
import Link from 'next/link';
import { motion } from 'framer-motion';

interface OverlaySectionsProps {
  onNavigate?: (page: string) => void;
}

// Exclusive White-Tinted Glass Container
export const GlassContainer = ({ children, className = "" }: { children?: React.ReactNode, className?: string }) => (
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

// Minimalist Card Component with White Glass
export const CleanCard = ({ title, icon: Icon, description }: { title: string, icon: any, description: string }) => (
  <div className="group relative p-8 border border-white/5 bg-white/[0.02] backdrop-blur-sm hover:border-[#6e683b]/30 transition-all duration-700 hover:bg-white/[0.05] overflow-hidden h-full">
    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
    <div className="absolute -inset-full top-0 block h-full w-1/2 -skew-x-12 bg-gradient-to-r from-transparent to-white opacity-0 group-hover:animate-shine" />
    
    <Icon className="w-5 h-5 text-gray-500 group-hover:text-[#6e683b] mb-6 transition-colors duration-500" />
    <h3 className="text-base font-display text-white mb-4 tracking-[0.15em] uppercase">{title}</h3>
    <p className="text-base text-gray-400 font-light leading-relaxed tracking-wide group-hover:text-gray-300 transition-colors">{description}</p>
  </div>
);

const IndustryTicker = () => (
  <div className="w-full overflow-hidden border-y border-white/10 bg-black py-6 relative z-20 select-none">
    {/* Soft fade edges for premium feel */}
    <div className="absolute top-0 left-0 h-full w-32 bg-gradient-to-r from-black to-transparent z-10 pointer-events-none"></div>
    <div className="absolute top-0 right-0 h-full w-32 bg-gradient-to-l from-black to-transparent z-10 pointer-events-none"></div>

    <motion.div 
      className="flex w-max"
      animate={{ x: "-50%" }}
      transition={{ 
        duration: 40, 
        ease: "linear", 
        repeat: Infinity 
      }}
    >
       {[...Array(2)].map((_, i) => (
         <div key={i} className="flex items-center">
            {[
              "ASYMMETRIC WARFARE",
              "CAPITAL PRESERVATION",
              "GAME THEORY",
              "SCENARIO MODELING",
              "RISK QUANTIFICATION",
              "STRATEGIC DOMINANCE"
            ].map((sector) => (
               <div key={sector} className="flex items-center gap-4 mr-16 md:mr-24">
                 <span className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full shadow-[0_0_10px_#00f0ff] animate-pulse"></span> 
                 <span className="text-sm uppercase tracking-[0.3em] font-bold whitespace-nowrap bg-clip-text text-transparent bg-gradient-to-r from-[#6e683b] via-[#9c9660] to-[#00f0ff]">
                   {sector}
                 </span>
               </div>
            ))}
         </div>
       ))}
    </motion.div>
  </div>
);

export const OverlaySections: React.FC<OverlaySectionsProps> = ({ onNavigate }) => {
  return (
    <div className="relative w-full pointer-events-none">
      
      {/* Scene 1: The Hook - The Solitude of Command */}
      <section className="h-screen flex flex-col items-center justify-center text-center px-6 mb-64 relative bg-black">
        
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5 }}
          className="pointer-events-auto z-10 flex flex-col items-center max-w-4xl mx-auto"
        >
          <div className="h-20 w-px bg-gradient-to-b from-transparent via-white/20 to-transparent mb-12 mx-auto"></div>
          
          <h1 className="text-4xl md:text-7xl font-display font-light tracking-tight text-white mb-10 leading-tight drop-shadow-2xl">
            To Lead Is To <span className="italic text-gray-400">Be Lied To.</span>
          </h1>
          
          <div className="flex items-center gap-4 mb-10">
             <div className="h-px w-12 bg-[#6e683b]/50"></div>
             <p className="text-base md:text-lg text-white uppercase tracking-[0.3em] font-light">
                The Last Honest Advisor
             </p>
             <div className="h-px w-12 bg-[#6e683b]/50"></div>
          </div>

          <p className="text-sm md:text-base text-gray-400 max-w-3xl mx-auto leading-loose tracking-wide font-light">
            The Board demands safety. The Team manufactures consensus. The Consultants bill time.
            <span className="text-white block mt-2 text-lg md:text-xl">We are the only voice in the room with nothing to lose.</span>
          </p>
        </motion.div>
        
        <div className="absolute bottom-12 opacity-20 animate-pulse delay-1000">
           <ArrowDown className="w-4 h-4 text-white" strokeWidth={1} />
        </div>
      </section>

      {/* Breathing Space for Animation - Extended */}
      <div className="h-[100vh] w-full"></div>

      {/* Scene 2: The Diagnosis - The Biology of Failure */}
      <section className="min-h-screen flex items-center py-64 px-6 pointer-events-auto relative z-10">
        <div className="max-w-7xl mx-auto w-full">
          <div className="max-w-xl">
            <GlassContainer>
               <div>
                     <div className="flex items-center gap-3 mb-6">
                        <Fingerprint className="w-5 h-5 text-[#6e683b]" />
                        <span className="text-gray-500 text-sm tracking-[0.3em] uppercase">The Human Glitch</span>
                     </div>
                     <h2 className="text-4xl md:text-5xl font-display font-light text-white mb-8 leading-tight">
                       The Architecture <br/> of <span className="italic text-gray-500">Consensus.</span>
                     </h2>
                     <div className="w-16 h-px bg-[#6e683b]/50 mb-8"></div>
                     <p className="text-gray-400 text-lg font-light leading-loose">
                       The fundamental flaw in your strategy room isn't lack of data. It is biology. Humans are social creatures wired for cohesion, not truth.
                       <br/><br/>
                       When you walk into a meeting, the dynamic shifts. Bad news gets softened. Risks get hidden in footnotes. Dissent is viewed as disloyalty. You aren't making decisions based on reality. You are making decisions based on a polite version of it.
                     </p>
               </div>
            </GlassContainer>
          </div>
        </div>
      </section>

      {/* Breathing Space for Animation - Extended */}
      <div className="h-[100vh] w-full"></div>

      {/* Scene 3: The Solution - Cold Logic */}
      <section className="min-h-screen flex items-center py-64 px-6 pointer-events-auto relative z-10">
        <div className="max-w-7xl mx-auto w-full">
           <div className="max-w-xl ml-auto">
             
              <GlassContainer>
                <div className="mb-10 text-left">
                   <h2 className="text-4xl md:text-5xl font-display font-light text-white mb-8 leading-tight">
                      Intelligence Without <br/><span className="text-[#6e683b]">Social Drag</span>
                   </h2>
                   <p className="text-gray-400 text-lg font-light leading-loose">
                      We have constructed a Council of AI agents designed with specific, opposing personalities. They do not collaborate to make you happy. They compete to find the truth.
                      <br/><br/>
                      One agent protects your cash. Another demands you spend it. One looks for expansion. Another looks for disaster. 
                      <span className="text-white"> Through this friction, the actual path forward is revealed.</span>
                   </p>
                </div>

                <div className="pt-8 border-t border-white/5 relative text-left">
                   <div className="absolute -top-4 -right-4 w-24 h-24 bg-[#6e683b]/5 blur-2xl rounded-full"></div>
                   <div className="flex items-center justify-start gap-4 mb-6">
                      <BrainCircuit className="w-6 h-6 text-gray-500" strokeWidth={1} />
                      <span className="text-sm uppercase tracking-widest text-gray-400">Synthetic Objectivity</span>
                   </div>
                   <p className="text-lg text-gray-300 leading-relaxed font-light italic relative z-10">
                      "You do not need another 'Yes Man' on your payroll. You need a machine that is indifferent to your ego. A system that will look at your life's work and tell you exactly where it is going to break."
                   </p>
                </div>
              </GlassContainer>

           </div>
        </div>
      </section>

      {/* Breathing Space for Animation - Extended */}
      <div className="h-[100vh] w-full"></div>

      {/* Scene 4: The Method - Conflict as a Service */}
      <section className="min-h-screen flex items-center py-64 px-6 pointer-events-auto relative z-10">
         <div className="w-full max-w-7xl mx-auto">
            <GlassContainer>
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-24">
                <div className="lg:col-span-5 flex flex-col justify-center">
                   <span className="text-[#6e683b] text-sm tracking-[0.3em] uppercase mb-6 block opacity-90">The Methodology</span>
                   <h2 className="text-4xl md:text-6xl font-display font-light mb-8 text-white leading-[1]">
                     We Weaponize <br/>
                     <span className="text-gray-500 italic">Dissent.</span>
                   </h2>
                   <p className="text-gray-300 text-lg font-light leading-[2] tracking-wide mb-8">
                     Great strategy is not born in a vacuum. It is forged in fire.
                     <br/><br/>
                     Most AI tools try to be "helpful." Ours are programmed to be "critical." We force your ideas to run a gauntlet of five adversarial intelligences. If your strategy survives The Council, it will survive the market.
                   </p>
                </div>
                
                <div className="lg:col-span-7 grid grid-cols-1 md:grid-cols-2 gap-8">
                   <CleanCard 
                     title="The Pessimist" 
                     icon={Shield} 
                     description="It assumes you are wrong. It assumes the market will crash. It forces you to build defenses for scenarios you are ignoring."
                   />
                   <CleanCard 
                     title="The Expansionist" 
                     icon={Compass} 
                     description="It ignores risk. It looks only for the asymmetric bet. It pushes you to capture territory while others retreat."
                   />
                   <CleanCard 
                     title="The Prosecutor" 
                     icon={Sword} 
                     description="It cross-examines your logic. It finds the gaps in your reasoning that a competitor would exploit."
                   />
                   <CleanCard 
                     title="The Architect" 
                     icon={Anchor} 
                     description="It ignores the 'why' and focuses on the 'how.' It demands timelines, resources, and concrete steps."
                   />
                </div>
              </div>
            </GlassContainer>
         </div>
      </section>

      {/* Breathing Space for Animation - Extended */}
      <div className="h-[100vh] w-full"></div>

      {/* Scene 5: The Output - The War Map */}
      <section className="min-h-screen flex items-center py-64 px-6 pointer-events-auto relative z-10">
         <div className="max-w-7xl mx-auto w-full">
           <GlassContainer>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
                
                {/* The Document Visual */}
                <div className="order-2 lg:order-1 relative group cursor-default">
                    <div className="absolute -inset-2 bg-[#6e683b] opacity-5 blur-2xl group-hover:opacity-10 transition-opacity duration-1000"></div>
                    
                    <div className="relative bg-[#0a0a0a]/80 backdrop-blur-xl border border-white/10 p-10 shadow-2xl">
                      <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-6">
                          <div className="flex items-center gap-2">
                            <FileText size={14} className="text-[#6e683b]" />
                            <span className="text-sm text-gray-400 uppercase tracking-widest">Strategic_Artifact_09.pdf</span>
                          </div>
                          <div className="flex gap-3">
                             <span className="text-xs text-green-500 font-mono">VERIFIED</span>
                          </div>
                      </div>
                      
                      <div className="space-y-6 opacity-90 group-hover:opacity-100 transition-opacity">
                          <div>
                            <h3 className="text-white font-display text-xl">Directive: Liquidity Preservation</h3>
                            <p className="text-sm text-gray-500 mt-2">Simulation Run: 10,000 Iterations</p>
                          </div>
                          
                          <div className="p-5 bg-red-900/10 border border-red-500/20">
                             <div className="flex items-center gap-2 mb-3">
                                <Activity size={14} className="text-red-400" />
                                <span className="text-xs text-red-400 uppercase tracking-widest">Critical Vulnerability Detected</span>
                             </div>
                             <p className="text-sm text-gray-300 leading-relaxed">
                                The Council detects a 64% probability of supply chain fracture in Q3. Current inventory buffers are insufficient.
                             </p>
                          </div>

                          <div className="p-5 bg-[#6e683b]/10 border border-[#6e683b]/20">
                             <div className="flex items-center gap-2 mb-3">
                                <Zap size={14} className="text-[#6e683b]" />
                                <span className="text-xs text-[#6e683b] uppercase tracking-widest">Recommended Action</span>
                             </div>
                             <p className="text-sm text-gray-300 leading-relaxed">
                                Secure forward contracts immediately. Diversify vendor base to LATAM region. Accept 5% margin hit to ensure continuity.
                             </p>
                          </div>
                      </div>
                    </div>
                </div>

                {/* The Narrative */}
                <div className="order-1 lg:order-2">
                    <div className="flex items-center gap-3 mb-6">
                      <Layout className="w-5 h-5 text-[#6e683b]" />
                      <span className="text-gray-500 text-sm tracking-[0.3em] uppercase">The Artifact</span>
                    </div>
                    <h2 className="text-4xl md:text-6xl font-display font-light text-white mb-8 leading-tight">
                      Clarity In <br/> <span className="italic text-gray-500">60 Seconds.</span>
                    </h2>
                    <div className="w-16 h-px bg-[#6e683b]/50 mb-8"></div>
                    <p className="text-gray-400 text-lg font-light leading-loose mb-10">
                      You do not have time to read another forty-page slide deck that says nothing.
                      <br/><br/>
                      We condense hours of strategic debate into a single, crystalline artifact. A document that tells you the risk, the probability, and the move. 
                      <span className="text-white"> Read it. Decide. Execute. Next.</span>
                    </p>
                    
                    <Link 
                       href="/pricing"
                       onClick={(e) => { if (onNavigate) { e.preventDefault(); onNavigate('pricing'); } }}
                       className="text-[#6e683b] uppercase text-sm tracking-[0.2em] border-b border-[#6e683b] pb-1 hover:text-white hover:border-white transition-colors font-bold"
                    >
                       View Sample Artifacts
                    </Link>
                </div>
              </div>
           </GlassContainer>
         </div>
      </section>

      {/* Breathing Space for Animation - Extended */}
      <div className="h-[100vh] w-full"></div>

      {/* Scene 6: The Price of Silence */}
      <section className="min-h-[80vh] flex items-center justify-center py-64 px-6 pointer-events-auto relative z-10">
         <div className="max-w-2xl mx-auto w-full">
            <GlassContainer className="text-center">
               <Scale className="w-8 h-8 text-[#6e683b] mx-auto mb-8" strokeWidth={1} />
               
               <h3 className="text-3xl md:text-4xl font-display text-white mb-8">The Cost of Being Wrong</h3>
               
               <p className="text-base text-gray-400 font-light leading-loose max-w-xl mx-auto mb-10">
                  A single strategic blind spot can cost you a quarter, a key employee, or the company itself. 
                  Compared to the cost of a bad decision, the price of this protocol is a rounding error.
                  <br/><br/>
                  <span className="text-white">For the price of a business lunch, you get the war room you deserve.</span>
               </p>
               
               <button 
                  onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLScph-EGBWK_FMyLzNIypqCA5IfJOcWdKFHOw0D-v1n8zgIWFA/viewform', '_blank')}
                  className="px-10 py-4 bg-[#6e683b] text-black text-xs font-bold uppercase tracking-[0.25em] hover:bg-white transition-all"
               >
                  Secure Protocol
               </button>
            </GlassContainer>
         </div>
      </section>
      
      {/* Social Proof Ticker */}
      <section className="pointer-events-auto">
         <IndustryTicker />
      </section>

      <Footer onNavigate={onNavigate} />
    </div>
  );
};