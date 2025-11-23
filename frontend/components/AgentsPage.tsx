'use client';

import React, { useState } from 'react';
import { GlassContainer } from './OverlaySections';
import { Shield, Eye, Scale, Zap, Users, ArrowRight, Terminal, Activity, Crosshair, Cpu, Network, ChevronRight, Globe, Hourglass, Lock, Sparkles, AlertTriangle, TrendingUp, Shuffle } from 'lucide-react';
import { Footer } from './Footer';
import { OrchestratorParticles } from './OrchestratorParticles';

interface AgentsPageProps {
  onNavigate?: (page: string) => void;
}

// Agent Data Structure
const AGENTS = [
  {
    id: 'scanner',
    title: "Horizon Scanner",
    role: "The Watchman",
    icon: Eye,
    color: "#00C2FF",
    bgGradient: "from-[#00C2FF]/20",
    directive: "Detect signals of disruption before they become market consensus.",
    methodology: "Ingests global macro-economic data, geopolitical shifts, and patent filings. Filters noise to isolate asymmetric threats.",
    output: "Predictive intelligence on market direction and competitor movement.",
    quote: "By the time it's in the news, it's too late."
  },
  {
    id: 'sentinel',
    title: "Capital Sentinel",
    role: "The Paranoid Survivor",
    icon: Shield,
    color: "#FFD700",
    bgGradient: "from-[#FFD700]/20",
    directive: "Preserve the kingdom. Identify ruin scenarios others are too optimistic to see.",
    methodology: "Monte Carlo simulations of black swan events. Stress-tests liquidity against catastrophic failure modes.",
    output: "Defensive capital allocation strategies and risk asymmetry reports.",
    quote: "Optimism is not a strategy. Survival is."
  },
  {
    id: 'advocate',
    title: "The Devil's Advocate",
    role: "The Challenger",
    icon: Scale,
    color: "#FF3366",
    bgGradient: "from-[#FF3366]/20",
    directive: "Destroy the echo chamber. Dismantle the leader's thesis to prove its worth.",
    methodology: "Applies logical fallacies detection and bias inversion. Relentlessly attacks the proposed strategy's weakest links.",
    output: "A 'Red Team' report exposing confirmation bias and logical gaps.",
    quote: "The most dangerous person in the room is the one who always agrees with you."
  },
  {
    id: 'cipher',
    title: "Culture Cipher",
    role: "The Human Variable",
    icon: Users,
    color: "#BF5AF2",
    bgGradient: "from-[#BF5AF2]/20",
    directive: "Predict organizational friction. Ensure the strategy survives contact with humanity.",
    methodology: "Analyzes organizational hierarchy, morale drivers, and resistance patterns. Simulates the 'people cost' of change.",
    output: "Change management protocols and friction heatmaps.",
    quote: "Culture eats strategy for breakfast. I make sure it doesn't eat yours."
  },
  {
    id: 'bridge',
    title: "Operational Bridge",
    role: "The Architect",
    icon: Zap,
    color: "#00f0ff",
    bgGradient: "from-[#00f0ff]/20",
    directive: "Translate abstract vision into concrete reality. The 'How' behind the 'Why'.",
    methodology: "Breaks strategic intent into OKRs, KPIs, and rigid timelines. Identifies resource bottlenecks instantly.",
    output: "Execution roadmaps and operational dependencies.",
    quote: "Vision without execution is hallucination."
  }
];

// Simulation Data
const SCENARIOS = [
  {
    id: 'crisis',
    title: 'Market Shock',
    icon: AlertTriangle,
    description: 'A competitor unexpectedly launches a product at 50% of your price point.',
    logs: [
      { agentId: 'scanner', text: 'ALERT: Patent filing detected 48h ago matches competitor capabilities. Supply chain data suggests they are loss-leading to bleed us out.' },
      { agentId: 'sentinel', text: 'RISK: Cash runway drops to 9 months if we match price. Recommended Hold: Do not engage in price war. Preserve liquidity.' },
      { agentId: 'advocate', text: 'CHALLENGE: The "premium" brand defense is weak. If we don\'t respond, we lose 30% market share by Q4. Prove our utility justifies the premium.' },
      { agentId: 'cipher', text: 'INTERNAL: Sales team confidence is plummeting. They need a narrative to defend the price point immediately, or attrition will spike.' },
      { agentId: 'bridge', text: 'ACTION: Deploy "Value-Stack" campaign in 48 hours. Re-train sales on ROI selling vs Price selling. Halt all non-essential hiring.' }
    ]
  },
  {
    id: 'expansion',
    title: 'New Market Entry',
    icon: Globe,
    description: 'Entering the APAC region with our flagship enterprise solution.',
    logs: [
      { agentId: 'scanner', text: 'SIGNAL: APAC regulatory environment shifting on data sovereignty (Law 44-B). Competitors B and C are withdrawing.' },
      { agentId: 'sentinel', text: 'RISK: Currency volatility in the region exceeds our risk tolerance threshold. Mandatory hedging required before capital deployment.' },
      { agentId: 'advocate', text: 'CHALLENGE: We are assuming our Western GTM strategy translates. Evidence suggests relationship-based sales cycles are 3x longer there.' },
      { agentId: 'cipher', text: 'CULTURE: Local leadership requires autonomy. If we manage from HQ, the satellite office will fail. Hire local GM first.' },
      { agentId: 'bridge', text: 'ACTION: Establish legal entity in Singapore (Hub). Partnership model for Japan. 18-month timeline to positive contribution margin.' }
    ]
  },
  {
    id: 'pivot',
    title: 'Strategic Pivot',
    icon: Shuffle,
    description: 'Shifting from Service-based revenue to SaaS recurring revenue.',
    logs: [
      { agentId: 'scanner', text: 'DATA: Service valuations compressing (2x revenue). SaaS valuations holding (8x revenue). The window to re-rate the company is now.' },
      { agentId: 'sentinel', text: 'RISK: Cash flow trough ("J-Curve") will be deeper than modeled. We need a bridge loan to survive the revenue dip.' },
      { agentId: 'advocate', text: 'CHALLENGE: You claim to be a product company, but 80% of revenue is custom dev. The product is not ready for self-serve.' },
      { agentId: 'cipher', text: 'FRICTION: The current team are consultants, not product builders. Expect 40% staff turnover. We need different DNA.' },
      { agentId: 'bridge', text: 'ACTION: Sunset custom dev contracts <$50k immediately. Restructure comp plans to incentivize ARR, not one-off fees.' }
    ]
  }
];

export const AgentsPage: React.FC<AgentsPageProps> = ({ onNavigate }) => {
  const [activeAgentIndex, setActiveAgentIndex] = useState(0);
  const [activeScenario, setActiveScenario] = useState(0);
  const activeAgent = AGENTS[activeAgentIndex];

  return (
    <div className="relative w-full bg-[#050505] min-h-screen overflow-x-hidden text-white">
      
      {/* SECTION 1: TACTICAL SPLIT INTERFACE */}
      <section className="relative min-h-screen flex flex-col lg:flex-row pt-24 lg:pt-0">
        
        {/* LEFT PANEL: THE ROSTER */}
        <div className="lg:w-[45%] h-auto lg:h-screen flex flex-col justify-center px-8 lg:pl-24 lg:pr-12 relative z-20 bg-[#050505] border-r border-white/5">
          
          {/* Ambient Grid */}
          <div className="absolute inset-0 opacity-[0.03] pointer-events-none" 
            style={{ backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
          </div>

          <div className="relative z-10">
             <div className="flex items-center gap-3 mb-8 opacity-0 animate-fade-in">
                <div className="w-2 h-2 bg-[#6e683b] rounded-full animate-pulse"></div>
                <span className="text-sm text-[#6e683b] uppercase tracking-[0.3em] font-bold">Private Council Online</span>
             </div>
             
             <h1 className="text-5xl lg:text-6xl font-display font-light mb-6 leading-tight tracking-tight">
               Construct Your <br/> <span className="text-gray-600 italic">War Room</span>
             </h1>
             
             <p className="text-lg text-gray-400 leading-loose max-w-md font-light tracking-wide mb-12 border-l border-white/10 pl-6">
               An autonomous cabinet of specialized intelligences. They do not sleep. They do not seek approval. They exist solely to sharpen your command.
             </p>

             {/* Agent List */}
             <div className="flex flex-col gap-1 w-full max-w-md">
                {AGENTS.map((agent, idx) => (
                  <button 
                    key={agent.id}
                    onClick={() => setActiveAgentIndex(idx)}
                    className={`group relative flex items-center justify-between p-5 transition-all duration-500 border border-transparent ${
                      idx === activeAgentIndex 
                        ? 'bg-white/[0.03] border-white/10' 
                        : 'hover:bg-white/[0.01] hover:border-white/5 opacity-60 hover:opacity-100'
                    }`}
                  >
                    {/* Active Indicator Line */}
                    {idx === activeAgentIndex && (
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#6e683b]" />
                    )}

                    <div className="flex items-center gap-4">
                       <span className={`text-sm font-mono transition-colors ${idx === activeAgentIndex ? 'text-[#6e683b]' : 'text-gray-600'}`}>
                         0{idx + 1}
                       </span>
                       <span className={`text-lg font-display tracking-widest uppercase ${idx === activeAgentIndex ? 'text-white' : 'text-gray-400'}`}>
                         {agent.title}
                       </span>
                    </div>
                    
                    {idx === activeAgentIndex ? (
                      <ChevronRight size={16} className="text-[#6e683b]" />
                    ) : (
                      <div className="w-1.5 h-1.5 rounded-full bg-white/10 group-hover:bg-white/30 transition-colors" />
                    )}
                  </button>
                ))}
             </div>
          </div>
        </div>

        {/* RIGHT PANEL: THE DOSSIER */}
        <div className="lg:w-[55%] h-auto lg:h-screen relative z-10 flex flex-col justify-center px-8 lg:px-24 overflow-hidden transition-colors duration-1000 bg-black/50">
           
           {/* Dynamic Background Gradient based on Agent Color */}
           <div className={`absolute inset-0 bg-gradient-to-br ${activeAgent.bgGradient} to-transparent opacity-10 transition-all duration-1000`}></div>
           
           {/* Giant Watermark Icon */}
           <div className="absolute right-[-10%] bottom-[-10%] opacity-[0.03] pointer-events-none transition-all duration-1000 transform scale-150 rotate-12">
              <activeAgent.icon strokeWidth={0.5} size={600} className="text-white" />
           </div>

           {/* Content Container */}
           <div className="relative z-20 max-w-xl">
              
              {/* Header */}
              <div className="flex items-center gap-6 mb-12">
                 <div className="p-5 border border-white/10 bg-white/[0.02] backdrop-blur-sm">
                    <activeAgent.icon 
                      className="w-8 h-8 transition-all duration-500" 
                      style={{ 
                        color: activeAgent.color,
                        filter: `drop-shadow(0 0 12px ${activeAgent.color})`
                      }} 
                      strokeWidth={1} 
                    />
                 </div>
                 <div>
                    <div className="flex items-center gap-3 mb-2">
                       <div className="h-px w-10 bg-white/20"></div>
                       <span className="text-sm text-gray-400 uppercase tracking-[0.3em]">Designation</span>
                    </div>
                    <h2 className="text-3xl md:text-5xl font-display text-white leading-tight">{activeAgent.role}</h2>
                 </div>
              </div>

              {/* Data Grid */}
              <div className="space-y-10">
                 <div className="group">
                    <h3 className="text-sm text-[#6e683b] uppercase tracking-widest mb-3 flex items-center gap-2 font-bold">
                       <Crosshair size={12} /> Primary Directive
                    </h3>
                    <p className="text-xl font-light text-gray-200 leading-relaxed border-l-2 border-white/10 pl-6 group-hover:border-[#6e683b] transition-colors duration-500">
                       {activeAgent.directive}
                    </p>
                 </div>

                 <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    <div>
                       <h3 className="text-sm text-gray-500 uppercase tracking-widest mb-4">Cognitive Methodology</h3>
                       <p className="text-base text-gray-400 leading-loose font-light">
                          {activeAgent.methodology}
                       </p>
                    </div>
                    <div>
                       <h3 className="text-sm text-gray-500 uppercase tracking-widest mb-4">Strategic Output</h3>
                       <p className="text-base text-white leading-loose font-light">
                          {activeAgent.output}
                       </p>
                    </div>
                 </div>

                 {/* Quote */}
                 <div className="pt-10 border-t border-white/5 mt-4">
                    <div className="flex gap-4 items-start">
                       <Terminal size={18} className="text-[#6e683b] mt-1 opacity-50" />
                       <p className="text-lg font-mono text-gray-500 italic leading-relaxed">
                         "{activeAgent.quote}"
                       </p>
                    </div>
                 </div>
              </div>

           </div>
        </div>
      </section>

      {/* SPACER */}
      <div className="h-[15vh] md:h-[25vh] w-full pointer-events-none"></div>

      {/* NEW: THE ERA OF HIGH-FREQUENCY HISTORY */}
      <section className="py-32 px-6 bg-[#0a0a0a] relative z-10">
         <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div className="relative">
               <div className="absolute -top-12 -left-12 w-24 h-24 border-t border-l border-white/10"></div>
               <h2 className="text-3xl font-display text-white mb-6">The Era of <br/> <span className="italic text-gray-500">High-Frequency History</span></h2>
               <p className="text-lg text-gray-400 font-light leading-loose text-justify">
                  We have exited the era of the Five-Year Plan. We have entered the age of the Five-Minute Shock. 
                  Supply chains fracture overnight. Narratives shift in hours. Capital flows change direction before the market opens.
                  <br/><br/>
                  The leader relying on quarterly reports is navigating a storm with a map from last year. 
                  The Council does not look backward. It ingests the volatility of the present to stabilize your future.
               </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
               <div className="p-8 bg-white/[0.02] border border-white/5">
                  <Globe className="w-8 h-8 text-[#6e683b] mb-4" strokeWidth={1} />
                  <h4 className="text-white font-display text-base mb-2">Global Asymmetry</h4>
                  <p className="text-sm text-gray-500 leading-relaxed">Local events now have instant global liquidity consequences.</p>
               </div>
               <div className="p-8 bg-white/[0.02] border border-white/5">
                  <Hourglass className="w-8 h-8 text-[#6e683b] mb-4" strokeWidth={1} />
                  <h4 className="text-white font-display text-base mb-2">Decay of Consensus</h4>
                  <p className="text-sm text-gray-500 leading-relaxed">By the time your board agrees, the opportunity is gone.</p>
               </div>
            </div>
         </div>
      </section>

      {/* NEW SECTION: ORCHESTRATOR VISUALIZATION */}
      {/* Increased Vertical Presence for Immersion */}
      <section className="relative z-10 py-12">
         <OrchestratorParticles />
      </section>

      {/* SECTION 2: THE DIALECTIC ENGINE (Process Flow) */}
      <section className="py-48 px-6 bg-[#080808] border-y border-white/5 relative overflow-hidden">
         {/* Ambient Grid Background */}
         <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
         
         <div className="max-w-6xl mx-auto relative z-10">
            <div className="text-center mb-24">
               <h2 className="text-4xl font-display text-white mb-4">The Dialectic Engine</h2>
               <p className="text-base text-gray-500 uppercase tracking-[0.3em]">From Chaos to Crystalized Strategy</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-12 lg:gap-0 relative">
               {/* Connecting Line (Desktop) */}
               <div className="hidden lg:block absolute top-8 left-[12%] w-[76%] h-px bg-gradient-to-r from-transparent via-white/10 to-transparent border-t border-dashed border-white/10"></div>

               <ProcessNode 
                  step="01" 
                  icon={Crosshair} 
                  title="Inquiry Injection" 
                  desc="You input the raw strategic ambiguity. The system parses variables."
               />
               <ProcessNode 
                  step="02" 
                  icon={Network} 
                  title="Adversarial Debate" 
                  desc="Agents debate autonomously. Risk argues with Optimism. Culture argues with Profit."
               />
               <ProcessNode 
                  step="03" 
                  icon={Cpu} 
                  title="Synthesis" 
                  desc="The core AI arbiter resolves conflicts, discarding weak logic and compounding strengths."
               />
               <ProcessNode 
                  step="04" 
                  icon={Terminal} 
                  title="Executive Output" 
                  desc="A singular, defensible strategic directive is presented for your command."
                  isLast
               />
            </div>
         </div>
      </section>

      {/* SPACER */}
      <div className="h-[20vh] w-full pointer-events-none"></div>

      {/* NEW: INTERACTIVE SCENARIO SIMULATOR */}
      <section className="py-32 px-6 bg-[#050505] relative z-10 border-b border-white/5">
        <div className="max-w-6xl mx-auto">
          <div className="mb-16 flex flex-col md:flex-row justify-between items-end gap-6">
             <div>
               <span className="text-[#6e683b] text-sm uppercase tracking-[0.3em] mb-4 block font-bold">Protocol Simulations</span>
               <h2 className="text-3xl md:text-4xl font-display text-white">The Council in Action</h2>
             </div>
             <p className="text-base text-gray-500 max-w-md text-right">
               Real-time strategic conflict resolution. See how the agents synthesize divergent data into a unified battle plan.
             </p>
          </div>

          {/* Scenario Selector */}
          <div className="flex flex-wrap gap-4 mb-12">
            {SCENARIOS.map((scenario, idx) => {
              const Icon = scenario.icon;
              return (
                <button
                  key={scenario.id}
                  onClick={() => setActiveScenario(idx)}
                  className={`flex items-center gap-3 px-6 py-4 border transition-all duration-300 ${
                    idx === activeScenario 
                    ? 'bg-[#6e683b]/10 border-[#6e683b] text-white' 
                    : 'bg-white/[0.02] border-white/5 text-gray-500 hover:bg-white/[0.05] hover:text-gray-300'
                  }`}
                >
                  <Icon size={18} className={idx === activeScenario ? 'text-[#6e683b]' : 'opacity-50'} />
                  <span className="text-base font-display tracking-widest uppercase">{scenario.title}</span>
                </button>
              )
            })}
          </div>

          {/* Console Window */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
             {/* Context */}
             <div className="lg:col-span-4 space-y-6">
                <div className="p-8 border border-white/10 bg-white/[0.02] h-full">
                   <h3 className="text-white font-display text-xl mb-4">Scenario Parameters</h3>
                   <div className="h-px w-12 bg-[#6e683b] mb-6"></div>
                   <p className="text-lg text-gray-300 leading-relaxed font-light mb-8">
                     {SCENARIOS[activeScenario].description}
                   </p>
                   <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-gray-500 uppercase tracking-widest">Urgency: Critical</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-[#6e683b] rounded-full"></div>
                        <span className="text-sm text-gray-500 uppercase tracking-widest">Data Sources: 142</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span className="text-sm text-gray-500 uppercase tracking-widest">Agents Active: 5/5</span>
                      </div>
                   </div>
                </div>
             </div>

             {/* Output Log */}
             <div className="lg:col-span-8">
                <div className="border border-white/10 bg-black p-6 font-mono text-sm h-full relative overflow-hidden">
                   {/* Header decoration */}
                   <div className="flex justify-between items-center mb-6 border-b border-white/10 pb-4">
                      <span className="text-[#6e683b] text-base">COUNCIL_LOG_STREAM_V.0.9</span>
                      <span className="text-gray-600 text-sm">ENCRYPTED</span>
                   </div>
                   
                   <div className="space-y-6 relative z-10">
                      {SCENARIOS[activeScenario].logs.map((log, i) => {
                         const agent = AGENTS.find(a => a.id === log.agentId);
                         return (
                           <div key={i} className="flex gap-4 animate-fade-in" style={{ animationDelay: `${i * 100}ms` }}>
                              <div className="min-w-[100px] text-right">
                                 <span className="block text-sm uppercase tracking-widest mb-1 font-bold" style={{ color: agent?.color }}>{agent?.title}</span>
                              </div>
                              <div className="w-px bg-white/10"></div>
                              <div className="text-gray-300 leading-relaxed text-base">
                                 {log.text}
                              </div>
                           </div>
                         )
                      })}
                   </div>

                   {/* Scanline effect */}
                   <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.5)_50%)] bg-[length:100%_4px] pointer-events-none opacity-20"></div>
                </div>
             </div>
          </div>
        </div>
      </section>

      {/* NEW: COGNITIVE ARBITRAGE (The Internal Truth) */}
      <section className="py-48 px-6 bg-[#050505] relative z-10">
        <GlassContainer className="max-w-4xl mx-auto border-l-2 border-l-[#6e683b] border-y-0 border-r-0">
           <div className="flex flex-col md:flex-row gap-12">
              <div className="md:w-1/3">
                 <span className="text-[#6e683b] text-sm uppercase tracking-[0.3em] mb-4 block font-bold">The Silent Asset</span>
                 <h2 className="text-3xl font-display text-white mb-6">The Sanctuary of Command</h2>
              </div>
              <div className="md:w-2/3">
                 <p className="text-lg text-gray-300 font-light leading-loose mb-6">
                    Leadership is, by definition, an act of isolation. You cannot show doubt to your investors. You cannot show weakness to your employees. You cannot show confusion to your board.
                 </p>
                 <p className="text-lg text-gray-300 font-light leading-loose mb-8">
                    So where do you go to be wrong?
                 </p>
                 <div className="p-6 bg-white/[0.02] border border-white/5 flex gap-4">
                    <Lock className="w-6 h-6 text-[#6e683b] flex-shrink-0 mt-1" />
                    <div>
                       <h4 className="text-white font-display text-lg mb-2">The Permission to Iterate</h4>
                       <p className="text-base text-gray-400 leading-relaxed">
                          AI-Augmented gives you the most valuable asset in the c-suite: <span className="text-gray-300">A safe space to test bad ideas so you only present the brilliant ones.</span> No political fallout. No judgment. Just rigorous, private optimization.
                       </p>
                    </div>
                 </div>
              </div>
           </div>
        </GlassContainer>
      </section>

      {/* SECTION 3: USE CASES (The "Why") */}
      <section className="py-48 px-6 relative z-10 bg-[#050505]">
         <GlassContainer className="max-w-5xl mx-auto border-[#6e683b]/20">
             <div className="flex flex-col md:flex-row gap-16 items-center">
                <div className="md:w-1/2">
                   <h3 className="text-3xl font-display text-white mb-6">Why You Need The Council</h3>
                   <p className="text-lg text-gray-400 leading-loose mb-8 font-light">
                     Traditional advisors operate on hourly incentives and fear of offending you. Your internal team operates on organizational politics. <br/><br/>
                     The Council has no ego. It has no fear. It has only one function: To ensure your decision is mathematically, financially, and strategically sound before you execute it.
                   </p>
                   <ul className="space-y-4">
                      <CheckItem text="Eliminate Executive Blindspots" />
                      <CheckItem text="Reduce Decision Latency by 90%" />
                      <CheckItem text="Create Permanent Strategic Memory" />
                   </ul>
                </div>
                <div className="md:w-1/2 w-full">
                   <div className="p-8 bg-[#6e683b]/5 border border-[#6e683b]/20 relative">
                      <div className="absolute top-0 left-0 w-2 h-2 bg-[#6e683b]"></div>
                      <div className="absolute top-0 right-0 w-2 h-2 bg-[#6e683b]"></div>
                      <div className="absolute bottom-0 left-0 w-2 h-2 bg-[#6e683b]"></div>
                      <div className="absolute bottom-0 right-0 w-2 h-2 bg-[#6e683b]"></div>
                      
                      <h4 className="text-[#6e683b] font-display text-xl mb-6 text-center uppercase tracking-widest">System Status</h4>
                      <div className="space-y-6">
                         <StatusRow label="Model Capacity" value="Optimal" />
                         <StatusRow label="Latency" value="< 200ms" />
                         <StatusRow label="Security" value="Enterprise/Encrypted" />
                         <StatusRow label="Bias Detection" value="Active" />
                      </div>
                      
                      <button 
                        onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLScph-EGBWK_FMyLzNIypqCA5IfJOcWdKFHOw0D-v1n8zgIWFA/viewform', '_blank')}
                        className="w-full mt-8 py-4 bg-[#6e683b] text-black font-bold uppercase text-sm tracking-[0.3em] hover:bg-[#8a824a] transition-all"
                      >
                        Deploy Council
                      </button>
                   </div>
                </div>
             </div>
         </GlassContainer>
      </section>

      <Footer onNavigate={onNavigate} />

    </div>
  );
};

// --- Sub-Components ---

const ProcessNode = ({ step, icon: Icon, title, desc, isLast = false }: any) => (
   <div className="relative group text-center flex flex-col items-center">
      {/* Icon Container */}
      <div className="w-16 h-16 bg-[#0a0a0a] border border-white/10 rounded-sm flex items-center justify-center mb-8 group-hover:border-[#6e683b]/50 group-hover:shadow-[0_0_20px_rgba(110,104,59,0.15)] transition-all duration-500 z-10 relative">
         <Icon className="w-8 h-8 text-gray-400 group-hover:text-[#6e683b] transition-colors" strokeWidth={1} />
         {/* Step Indicator */}
         <div className="absolute -top-2 -right-2 bg-[#0a0a0a] border border-white/10 text-sm px-1.5 py-0.5 text-[#6e683b] font-mono opacity-0 group-hover:opacity-100 transition-all font-bold">
           {step}
         </div>
      </div>
      
      <h3 className="text-xl font-display text-white mb-4">{title}</h3>
      <p className="text-base text-gray-400 leading-relaxed max-w-[240px] mx-auto font-light group-hover:text-gray-300 transition-colors">
        {desc}
      </p>

      {!isLast && (
         <div className="lg:hidden my-8 text-white/10 flex justify-center">
            <ArrowRight className="rotate-90" />
         </div>
      )}
   </div>
);

const CheckItem = ({ text }: { text: string }) => (
   <div className="flex items-start gap-4 p-4 border border-white/5 bg-white/[0.01] hover:border-white/10 transition-colors">
      <div className="w-1.5 h-1.5 bg-[#6e683b] mt-2 rounded-full"></div>
      <span className="text-base text-gray-300 font-light tracking-wide">{text}</span>
   </div>
);

const StatusRow = ({ label, value }: { label: string, value: string }) => (
  <div className="flex justify-between items-center border-b border-[#6e683b]/20 pb-2">
     <span className="text-sm uppercase tracking-widest text-gray-500">{label}</span>
     <span className="text-base font-mono text-[#6e683b]">{value}</span>
  </div>
);