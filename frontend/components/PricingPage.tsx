'use client';

import React, { useState } from 'react';
import { GlassContainer } from './OverlaySections';
import { Check, Lock, Shield, Zap, Star, ChevronDown, ChevronUp, Award, X, TrendingUp, Clock, Users, Briefcase, Database, Layers, ArrowRight, UserCheck, ShieldCheck, Gem } from 'lucide-react';
import { Footer } from './Footer';
import { PricingParticles } from './PricingParticles';

interface PricingPageProps {
  onNavigate?: (page: string) => void;
}

// Local variant for this page to ensure consistent "sm" blur
const PricingGlass = ({ children, className = "" }: { children?: React.ReactNode, className?: string }) => (
  <div className={`p-8 md:p-12 bg-white/[0.02] backdrop-blur-sm border border-white/10 shadow-[0_0_50px_rgba(255,255,255,0.02)] rounded-sm ${className}`}>
    {children}
  </div>
);

export const PricingPage: React.FC<PricingPageProps> = ({ onNavigate }) => {
  const [annual, setAnnual] = useState(true);

  return (
    <div className="relative w-full min-h-screen bg-[#050505] overflow-x-hidden">
      
      {/* NEW: 3D Particle System for Strategic Asymmetry - Fixed position */}
      <PricingParticles />

      {/* 1. Hero: Strategic Asymmetry */}
      <section className="pt-48 pb-32 px-6 flex flex-col items-center text-center relative z-10 pointer-events-none">
        <div className="pointer-events-auto">
            <div className="flex items-center justify-center gap-3 mb-8 animate-fade-in">
                <div className="w-1 h-1 bg-[#6e683b]"></div>
                <span className="text-[#6e683b] text-sm tracking-[0.3em] uppercase font-bold">Invitation Only</span>
                <div className="w-1 h-1 bg-[#6e683b]"></div>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-display font-light text-white mb-8 leading-tight">
              Strategic <span className="italic text-gray-500">Asymmetry</span>
            </h1>
            <div className="h-16 w-px bg-gradient-to-b from-transparent via-white/20 to-transparent mb-8 mx-auto"></div>
            
            <p className="text-gray-400 text-base md:text-lg tracking-[0.1em] font-light max-w-xl mx-auto leading-loose">
              Acquire the capability of a 24/7 strategy firm for the price of a standard utility.
              <br className="hidden md:block"/>
              We are offering early adopters a permanent advantage before public pricing takes effect.
            </p>
        </div>
      </section>

      {/* BREATHING SPACE 1 */}
      <div className="h-[20vh] w-full"></div>

      {/* NEW: The Council Profile (Qualification) */}
      <section className="py-32 px-6 relative z-10">
        <div className="max-w-6xl mx-auto">
           <div className="text-center mb-16">
              <p className="text-sm text-gray-500 uppercase tracking-[0.2em] mb-3 font-bold">Member Qualification</p>
              <h3 className="text-2xl font-display text-white">Who We Are Looking For</h3>
           </div>
           
           <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <ProfileCard 
                icon={UserCheck}
                title="The Isolated Founder"
                desc="You are surrounded by employees who hesitate to challenge you. You need a ruthless, private sounding board to stress-test your vision before you present it."
              />
              <ProfileCard 
                icon={TrendingUp}
                title="The Wartime Executive"
                desc="You are navigating a pivot, a crisis, or an aggressive expansion. Speed is your currency. You cannot wait two weeks for a consultant's report."
              />
              <ProfileCard 
                icon={Gem}
                title="The Capital Allocator"
                desc="You place bets on the future. You need to see around corners, identify black swans, and model risk faster than the market can react."
              />
           </div>
        </div>
      </section>

      {/* BREATHING SPACE 2 */}
      <div className="h-[15vh] w-full"></div>

      {/* 2. The Monolith (Pricing Card) */}
      <section className="px-6 relative z-10 my-12">
        <div className="max-w-4xl mx-auto">
          
          {/* Toggle */}
          <div className="flex justify-center mb-12">
            <div className="bg-white/[0.05] border border-white/10 p-1 flex items-center relative backdrop-blur-sm">
              <div className={`absolute top-1 bottom-1 w-[calc(50%-4px)] bg-[#6e683b]/10 border border-[#6e683b]/30 transition-all duration-500 ${annual ? 'left-[calc(50%+2px)]' : 'left-[2px]'}`}></div>
              <button 
                onClick={() => setAnnual(false)}
                className={`relative z-10 px-10 py-3 text-sm uppercase tracking-[0.2em] transition-colors duration-300 ${!annual ? 'text-white' : 'text-gray-600'}`}
              >
                Monthly
              </button>
              <button 
                onClick={() => setAnnual(true)}
                className={`relative z-10 px-10 py-3 text-sm uppercase tracking-[0.2em] transition-colors duration-300 ${annual ? 'text-[#6e683b]' : 'text-gray-600'}`}
              >
                Yearly
              </button>
            </div>
          </div>

          {/* The Card */}
          <div className="relative group">
             {/* Glow Effect */}
             <div className="absolute -inset-1 bg-gradient-to-b from-[#6e683b] via-transparent to-[#6e683b] opacity-20 blur-xl group-hover:opacity-30 transition-opacity duration-1000"></div>
             
             <div className="relative bg-white/[0.02] backdrop-blur-sm border border-white/10 p-8 md:p-16 overflow-hidden shadow-2xl">
                {/* Decorative Background Elements */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-5"></div>
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#6e683b] to-transparent opacity-50"></div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    
                    {/* Left: The Value */}
                    <div className="flex flex-col justify-between">
                        <div>
                            <div className="flex items-center gap-3 mb-4">
                                <Star className="w-4 h-4 text-[#6e683b] fill-[#6e683b]" />
                                <span className="text-[#6e683b] text-sm uppercase tracking-[0.3em] font-bold">Founding Member</span>
                            </div>
                            <h3 className="text-4xl font-display text-white mb-2">Authority <span className="text-gray-600">Tier</span></h3>
                            <p className="text-sm text-gray-500 uppercase tracking-widest mb-8">Lifetime Rate Lock Active</p>
                            
                            <div className="flex items-baseline gap-2 mb-2">
                                <span className="text-5xl font-light text-white tracking-tight">${annual ? '1,490' : '149'}</span>
                                <span className="text-xl text-gray-600 line-through decoration-[#6e683b] decoration-1">$499</span>
                            </div>
                            <p className="text-sm text-gray-400 uppercase tracking-widest mb-10">
                                {annual ? 'Billed Annually (2 Months Free)' : 'Billed Monthly'}
                            </p>

                            <button 
                                onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLScph-EGBWK_FMyLzNIypqCA5IfJOcWdKFHOw0D-v1n8zgIWFA/viewform', '_blank')}
                                className="w-full py-5 bg-[#6e683b] hover:bg-[#8a824a] text-black font-bold text-sm uppercase tracking-[0.3em] transition-all flex items-center justify-center gap-4 group-hover:gap-6 mb-6"
                            >
                                <span>Secure Protocol</span>
                                <ArrowRight size={16} />
                            </button>
                            <p className="text-sm text-center text-gray-600">
                                14-day risk-free trial. Cancel anytime.
                            </p>
                        </div>
                    </div>

                    {/* Right: The Specs */}
                    <div className="border-l border-white/5 pl-0 lg:pl-12">
                        <div className="space-y-8">
                            
                            <div>
                                <h4 className="text-white font-display text-base mb-4 flex items-center gap-2">
                                    <Layers size={16} className="text-[#6e683b]" /> Core Capabilities
                                </h4>
                                <ul className="space-y-3">
                                    <FeatureItem text="Unlimited Strategic Sessions" />
                                    <FeatureItem text="Full Council Access (5 Agents)" />
                                    <FeatureItem text="The Decision Canvas Interface" />
                                </ul>
                            </div>

                            <div>
                                <h4 className="text-white font-display text-base mb-4 flex items-center gap-2">
                                    <Briefcase size={16} className="text-[#6e683b]" /> Executive Output
                                </h4>
                                <ul className="space-y-3">
                                    <FeatureItem text="Board-Ready Memo Export" />
                                    <FeatureItem text="Permanent Strategic Memory" />
                                    <FeatureItem text="Priority 'Red Phone' Processing" />
                                </ul>
                            </div>

                            <div>
                                <h4 className="text-white font-display text-base mb-4 flex items-center gap-2">
                                    <Database size={16} className="text-[#6e683b]" /> Sovereignty
                                </h4>
                                <ul className="space-y-3">
                                    <FeatureItem text="Zero-Retention AI Guarantee" />
                                    <FeatureItem text="Private Sandbox Environment" />
                                </ul>
                            </div>

                        </div>
                    </div>
                </div>
             </div>
          </div>
        </div>
      </section>

      {/* BREATHING SPACE 3 */}
      <div className="h-[20vh] w-full"></div>

      {/* 3. The Logic (ROI) */}
      <section className="py-32 px-6 bg-white/[0.02] backdrop-blur-sm border-y border-white/5 relative z-10">
         <div className="max-w-5xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
                <div>
                    <h2 className="text-3xl font-display text-white mb-6">The ROI of One Decision</h2>
                    <p className="text-lg text-gray-400 font-light leading-loose mb-8">
                        What is the cost of a strategy meeting that goes nowhere? What is the cost of entering a market three weeks late?
                        <br/><br/>
                        AI-Augmented costs less than a single hour of a junior consultant's billing time. If the system helps you avoid just <span className="text-white border-b border-[#6e683b]">one blind spot</span> in a year, the return on investment is infinite.
                    </p>
                    <div className="flex gap-8">
                        <div>
                            <span className="block text-3xl text-white font-light mb-1">90%</span>
                            <span className="text-sm text-gray-500 uppercase tracking-widest">Faster Consensus</span>
                        </div>
                        <div>
                            <span className="block text-3xl text-white font-light mb-1">100%</span>
                            <span className="text-sm text-gray-500 uppercase tracking-widest">Ownership</span>
                        </div>
                    </div>
                </div>
                
                <div className="space-y-4">
                    <ComparisonRow 
                        label="Strategy Consultant" 
                        price="$25,000 / week" 
                        time="6 Weeks" 
                        outcome="Outsourced Thinking" 
                        bad 
                    />
                    <ComparisonRow 
                        label="Executive Assistant" 
                        price="$6,000 / month" 
                        time="Organic" 
                        outcome="Admin Support" 
                        neutral
                    />
                    <ComparisonRow 
                        label="AI-Augmented" 
                        price="$149 / month" 
                        time="Instant" 
                        outcome="Augmented Authority" 
                        highlight
                    />
                </div>
            </div>
         </div>
      </section>

      {/* BREATHING SPACE 4 */}
      <div className="h-[20vh] w-full"></div>

      {/* 4. Sovereignty Protocol (Security) */}
      <section className="py-32 px-6 relative z-10">
        <PricingGlass className="max-w-4xl mx-auto border-l-2 border-l-[#6e683b] border-y-0 border-r-0">
            <div className="flex flex-col md:flex-row gap-12 items-start">
                <div className="md:w-1/3">
                    <Shield className="w-8 h-8 text-[#6e683b] mb-6" strokeWidth={1} />
                    <h3 className="text-2xl font-display text-white mb-2">Sovereignty Protocol</h3>
                    <p className="text-sm text-gray-500 uppercase tracking-[0.2em] font-bold">Enterprise Grade by Default</p>
                </div>
                <div className="md:w-2/3">
                    <p className="text-lg text-gray-300 font-light leading-loose mb-6">
                        We understand that your strategic IP is your most valuable asset. Our architecture is built on a "Zero-Training" pledge.
                    </p>
                    <ul className="space-y-4">
                        <li className="flex gap-4">
                            <Lock size={16} className="text-[#6e683b] mt-1" />
                            <div className="text-base text-gray-400 leading-relaxed">
                                <strong className="text-white block mb-1">Zero-Training Guarantee</strong>
                                Your data is never used to train our public models or shared with other users.
                            </div>
                        </li>
                        <li className="flex gap-4">
                            <Database size={16} className="text-[#6e683b] mt-1" />
                            <div className="text-base text-gray-400 leading-relaxed">
                                <strong className="text-white block mb-1">Isolated Context</strong>
                                Your strategic memory is siloed in your private instance.
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </PricingGlass>
      </section>
      
      {/* BREATHING SPACE 5 */}
      <div className="h-[15vh] w-full"></div>

      {/* NEW: Protocol Guarantee (Risk Reversal) */}
      <section className="py-24 px-6 border-t border-white/5 relative z-10 bg-white/[0.02] backdrop-blur-sm">
         <div className="max-w-3xl mx-auto text-center">
            <ShieldCheck className="w-8 h-8 text-[#6e683b] mx-auto mb-6" strokeWidth={1} />
            <h3 className="text-xl font-display text-white mb-4">The Protocol Guarantee</h3>
            <p className="text-base text-gray-400 font-light leading-loose max-w-xl mx-auto mb-0">
              We do not profit from hesitancy. If The Council does not radically sharpen your strategic clarity within 14 days, simply execute the cancellation protocol. We will refund your investment in full, no questions asked. We only want capital from leaders who are actively gaining an advantage.
            </p>
         </div>
      </section>

      {/* BREATHING SPACE 6 */}
      <div className="h-[20vh] w-full"></div>

      {/* NEW: Evolution Protocol (Replaces Enterprise) */}
      <section className="py-32 px-6 relative z-10">
        <PricingGlass className="max-w-5xl mx-auto border-[#6e683b]/20">
           <div className="flex flex-col md:flex-row items-center justify-between gap-12">
              <div className="flex gap-6 items-start">
                 <div className="p-4 border border-white/10 bg-white/[0.02]">
                    <TrendingUp className="w-6 h-6 text-[#6e683b]" strokeWidth={1} />
                 </div>
                 <div>
                    <h3 className="text-xl font-display text-white mb-2">The Evolution Protocol</h3>
                    <p className="text-sm text-gray-400 uppercase tracking-widest mb-4 font-bold">Future-Proof Your Advantage</p>
                    <p className="text-base text-gray-500 font-light leading-relaxed max-w-md">
                       The Council is not static. It evolves. We are currently training advanced modules for Q4 release. 
                       While future public tiers will pay separately for these capabilities, Founding Members secure <span className="text-gray-300 border-b border-white/20">all future upgrades</span> at their locked rate.
                    </p>
                 </div>
              </div>
              
              {/* Roadmap Micro-List */}
              <div className="space-y-3 min-w-[240px]">
                 <div className="flex items-center gap-3 opacity-50">
                    <Check size={14} className="text-[#6e683b]" />
                    <span className="text-sm text-gray-500 uppercase tracking-wider line-through">Foundation Models</span>
                 </div>
                 <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-[#6e683b] animate-pulse"></div>
                    <span className="text-sm text-white uppercase tracking-wider font-bold">Q4: Macro-Economic Sense</span>
                 </div>
                 <div className="flex items-center gap-3 opacity-80">
                    <div className="w-2 h-2 rounded-full border border-gray-600"></div>
                    <span className="text-sm text-gray-400 uppercase tracking-wider">Q1: Competitor Wargaming</span>
                 </div>
                 <div className="flex items-center gap-3 opacity-60">
                    <div className="w-2 h-2 rounded-full border border-gray-600"></div>
                    <span className="text-sm text-gray-500 uppercase tracking-wider">Q2: Auto-Execution</span>
                 </div>
              </div>
           </div>
        </PricingGlass>
      </section>

      {/* BREATHING SPACE 7 */}
      <div className="h-[20vh] w-full"></div>

      {/* 5. FAQ */}
      <section className="py-32 px-6 bg-white/[0.02] backdrop-blur-sm border-t border-white/5 relative z-10">
        <div className="max-w-3xl mx-auto">
           <div className="text-center mb-16">
             <h3 className="text-2xl font-display text-white mb-4">Executive Queries</h3>
           </div>
           <div className="space-y-2">
              <FAQItem q="Why is the price so low for an 'Executive' tool?" a="We are in Beta. This is a 'Founding Member' rate designed to reward early adopters who help us refine the dialectic engine. The public release price will be significantly higher ($499+/mo). Your rate is locked for life." />
              <FAQItem q="Can I invite my team?" a="Not yet. Currently, AI-Augmented is designed as a personal strategic weapon for the individual leader. Team features are on the roadmap for Q4." />
              <FAQItem q="How fast is the implementation?" a="Immediate. There is no setup time or lengthy onboarding. As soon as your access is initialized, the Council is online. You can run your first strategic simulation within 90 seconds of joining." />
              <FAQItem q="What happens to my data if I cancel?" a="You can export your entire strategic history (Decision Canvas, Chats, Reports) as a JSON or PDF package. Once your account is closed, your data is permanently purged from our servers within 30 days." />
           </div>
        </div>
      </section>

      {/* BREATHING SPACE 8 */}
      <div className="h-[15vh] w-full"></div>

      {/* 6. Final CTA */}
      <section className="py-40 px-6 text-center border-t border-white/5 relative z-10 overflow-hidden">
         {/* Background Image */}
         <div className="absolute inset-0 w-full h-full z-0">
             <div className="absolute inset-0 bg-[#050505] z-0"></div>
             <img 
               src="https://images.unsplash.com/photo-1529699211952-734e80c4d42b?q=80&w=2071&auto=format&fit=crop" 
               alt="Endgame Strategy"
               className="w-full h-full object-cover opacity-50 mix-blend-luminosity"
             />
             <div className="absolute inset-0 bg-gradient-to-b from-[#050505] via-transparent to-[#050505]"></div>
             <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#050505_100%)] opacity-90"></div>
         </div>

         <div className="max-w-2xl mx-auto relative z-10">
            <h2 className="text-4xl md:text-5xl font-display text-white mb-8 tracking-tight drop-shadow-lg">The Window is Closing.</h2>
            <p className="text-gray-300 text-base font-light mb-12 leading-loose uppercase tracking-widest drop-shadow-md">
                There are limited Founding Member spots available for this cohort. <br className="hidden md:block" />
                Secure your rate. Secure your advantage.
            </p>
            <button 
                onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLScph-EGBWK_FMyLzNIypqCA5IfJOcWdKFHOw0D-v1n8zgIWFA/viewform', '_blank')}
                className="px-12 py-5 bg-white text-black hover:bg-[#6e683b] hover:text-white transition-all uppercase text-sm tracking-[0.3em] font-bold shadow-2xl hover:shadow-[0_0_30px_rgba(110,104,59,0.3)]"
            >
                Initialize Access
            </button>
         </div>
      </section>

      <Footer onNavigate={onNavigate} />
    </div>
  );
};

// Helper Components

const ProfileCard = ({ icon: Icon, title, desc }: { icon: any, title: string, desc: string }) => (
   <div className="p-8 border border-white/5 bg-white/[0.02] hover:border-[#6e683b]/30 transition-colors group backdrop-blur-sm">
      <Icon className="w-8 h-8 text-[#6e683b] mb-6 opacity-70 group-hover:opacity-100" strokeWidth={1} />
      <h4 className="text-xl font-display text-white mb-3">{title}</h4>
      <p className="text-base text-gray-400 leading-loose font-light">
         {desc}
      </p>
   </div>
);

const FeatureItem = ({ text }: { text: string }) => (
  <div className="flex items-start gap-3 group cursor-default">
    <div className="w-1.5 h-1.5 mt-1.5 bg-[#6e683b] group-hover:scale-150 transition-transform rounded-full"></div>
    <span className="text-base text-gray-400 font-light group-hover:text-gray-200 transition-colors">{text}</span>
  </div>
);

const ComparisonRow = ({ label, price, time, outcome, bad = false, neutral = false, highlight = false }: any) => (
    <div className={`grid grid-cols-12 gap-4 p-5 border items-center transition-all duration-300 ${
        highlight 
        ? 'bg-[#6e683b]/10 border-[#6e683b] scale-105 shadow-2xl' 
        : 'bg-white/[0.02] border-white/5 hover:bg-white/[0.04]'
    }`}>
        <div className="col-span-4">
            <span className={`text-base font-display ${highlight ? 'text-white' : 'text-gray-400'}`}>{label}</span>
        </div>
        <div className="col-span-3 text-right">
            <span className="text-sm text-gray-500 uppercase tracking-wider">{price}</span>
        </div>
        <div className="col-span-2 text-right hidden md:block">
             <span className="text-sm text-gray-500 uppercase tracking-wider">{time}</span>
        </div>
        <div className="col-span-3 text-right">
            <span className={`text-sm uppercase tracking-wider font-bold ${
                bad ? 'text-red-400' : highlight ? 'text-[#6e683b]' : 'text-gray-500'
            }`}>{outcome}</span>
        </div>
    </div>
);

const FAQItem = ({ q, a }: { q: string, a: string }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="border-b border-white/5">
       <button 
         onClick={() => setIsOpen(!isOpen)}
         className="w-full py-6 flex justify-between items-center text-left hover:text-[#6e683b] transition-colors group"
       >
          <span className="text-lg font-light text-gray-300 group-hover:text-white transition-colors">{q}</span>
          {isOpen ? <ChevronUp size={16} className="text-[#6e683b]" /> : <ChevronDown size={16} className="text-gray-600 group-hover:text-[#6e683b]" />}
       </button>
       <div className={`overflow-hidden transition-all duration-500 ease-in-out ${isOpen ? 'max-h-48 opacity-100 pb-8' : 'max-h-0 opacity-0'}`}>
          <p className="text-base text-gray-500 leading-loose pr-8 pl-4 border-l border-white/10">{a}</p>
       </div>
    </div>
  );
};