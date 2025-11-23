'use client';

import React from 'react';
import { GlassContainer } from './OverlaySections';
import { Footer } from './Footer';

interface TermsPageProps {
  onNavigate?: (page: string) => void;
}

export const TermsPage: React.FC<TermsPageProps> = ({ onNavigate }) => {
  return (
    <div className="relative w-full min-h-screen bg-[#050505]">
      <section className="pt-40 px-6 relative z-10">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <span className="inline-block py-1 px-3 border border-[#6e683b]/30 rounded-full bg-[#6e683b]/5 text-[#6e683b] text-sm tracking-[0.3em] uppercase mb-8 font-bold">
              Service Protocols
            </span>
            <h1 className="text-4xl md:text-6xl font-display font-light text-white mb-6">Terms of Service</h1>
            <p className="text-gray-400 text-base uppercase tracking-widest mb-2">Effective Date: October 19, 2025</p>
            <p className="text-gray-500 text-sm uppercase tracking-widest">
              Company: AI-Augmented | Service: AI-Augmented Platform (The "Service") | Contact: info@aiaugmented.io
            </p>
          </div>

          <GlassContainer className="space-y-16 text-lg font-light text-gray-300 leading-relaxed">

            {/* Table of Contents */}
            <div className="p-8 border border-white/10 bg-white/[0.02]">
              <h2 className="text-2xl font-display text-white mb-6">Table of Contents</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-2 text-sm text-gray-400">
                 <ul className="space-y-2">
                    <li>1. Acceptance of Terms</li>
                    <li>2. Service Description</li>
                    <li>3. User Eligibility and Account Registration</li>
                    <li>4. Subscription and Billing</li>
                    <li>5. User Responsibilities and Acceptable Use</li>
                    <li>6. Prohibited Activities</li>
                    <li>7. Intellectual Property Rights</li>
                    <li>8. User Content Ownership</li>
                    <li>9. Your Use of Our Agents</li>
                    <li>10. Limitation of Liability and Disclaimers</li>
                    <li>11. Indemnification</li>
                    <li>12. Service Availability and Support</li>
                    <li>13. End-of-Life and Service Discontinuation</li>
                    <li>14. Rate Limiting and Usage Restrictions</li>
                    <li>15. Beta Status and Early-Stage Features</li>
                    <li>16. Competitive Use and Acceptable Restrictions</li>
                    <li>17. Support and Response SLAs</li>
                    <li>18. Enterprise/GDPR Data Processing Agreement</li>
                    <li>19. Regulated Industries Disclaimer</li>
                    <li>20. Account Limits and Resource Allocation</li>
                 </ul>
                 <ul className="space-y-2">
                    <li>21. Content Removal and Moderation</li>
                    <li>22. User Feedback and Suggestions Ownership</li>
                    <li>23. Account Inactivity and Cleanup</li>
                    <li>24. Backups and Data Recovery</li>
                    <li>25. Third-Party Integrations and Webhooks</li>
                    <li>26. Benchmarking and Competitive Analysis</li>
                    <li>27. Audit Trail and Account Activity Logging</li>
                    <li>28. Platform Features and API Stability</li>
                    <li>29. Suspension and Termination</li>
                    <li>30. Dispute Resolution and Governing Law</li>
                    <li>31. Modifications to Terms</li>
                    <li>32. Entire Agreement and Severability</li>
                    <li>33. Contact Information</li>
                    <li>34. Acknowledgments and Agreements</li>
                    <li>35. Definitions</li>
                    <li>36. Severability and Survival</li>
                    <li>37. Third-Party Links and Services</li>
                    <li>38. Accessibility</li>
                    <li>39. Export Controls</li>
                    <li>40. Government Use</li>
                    <li>41. Quick Reference: Key Points</li>
                 </ul>
              </div>
            </div>

            {/* 1. Acceptance */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">1. Acceptance of Terms</h2>
              <p className="mb-4">By accessing or using AI-Augmented ("The Service"), you agree to be bound by these Terms. If you do not agree, you may not use the Service. Your use constitutes acknowledgment that you have read, understood, and agree to be legally bound.</p>
              <p className="mb-4">If you represent an organization, you warrant that you have authority to bind that organization. Continued use after modifications constitutes acceptance of updated Terms.</p>
            </section>

            {/* 2. Service Description */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">2. Service Description</h2>
              <p className="mb-4">AI-Augmented synthesizes market, financial, and competitive intelligence to help leaders make strategic decisions. We provide specialized agent analysis, decision frameworks, and a permanent record of strategic thinking.</p>
              <h3 className="text-white font-display text-xl mb-2">What We Are NOT</h3>
              <ul className="list-disc pl-5 space-y-2 marker:text-[#6e683b] mb-4">
                <li><strong>Not Guaranteed Accuracy:</strong> Agents provide analysis based on available data; you must verify outputs.</li>
                <li><strong>Not Professional Advice:</strong> We do not provide legal, financial, or medical advice.</li>
                <li><strong>Not Automation:</strong> You always make the final decision.</li>
              </ul>
              <h3 className="text-white font-display text-xl mb-2">Subscription Includes</h3>
              <p>Unlimited strategic decisions, five specialized agents, Decision Canvas, executive reports, and permanent memory.</p>
            </section>

            {/* 3. Eligibility */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">3. User Eligibility and Account Registration</h2>
              <p className="mb-4">You must be 18+ and authorized to enter this agreement. You are responsible for maintaining the confidentiality of your credentials and for all activity under your account.</p>
              <p>We are not responsible for unauthorized access resulting from your failure to secure your device or credentials.</p>
            </section>

            {/* 4. Subscription */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">4. Subscription and Billing</h2>
              <div className="p-6 border border-[#6e683b]/30 bg-[#6e683b]/5 mb-6">
                 <h3 className="text-[#6e683b] font-display text-xl mb-2">Founding User Rate Lock</h3>
                 <p>Your $149/month rate is locked indefinitely for the lifetime of your continuous subscription, even if we raise pricing later.</p>
              </div>
              <p className="mb-2"><strong>Plans:</strong> $149/month or $1,490/year.</p>
              <p className="mb-2"><strong>Payment:</strong> Charged automatically. Failed payments result in suspension after 5 days.</p>
              <p><strong>Taxes:</strong> You are responsible for applicable taxes based on your billing address.</p>
            </section>

            {/* 5. Responsibilities */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">5. User Responsibilities and Acceptable Use</h2>
              <p className="mb-4">You are responsible for all content you upload. You warrant you have rights to it. All decisions made using the platform are ultimately YOUR decisions.</p>
              <p className="mb-4">Do not upload third-party personal data without consent. You indemnify us if you violate these restrictions.</p>
            </section>

            {/* 6. Prohibited */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">6. Prohibited Activities</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <div>
                    <h3 className="text-white font-display text-xl mb-2">Strictly Prohibited</h3>
                    <ul className="list-disc pl-5 space-y-2 marker:text-red-500 text-gray-400">
                       <li>Using for illegal activities or fraud</li>
                       <li>Reverse-engineering agent logic</li>
                       <li>Bulk extraction for model training</li>
                       <li>Scraping or automated extraction</li>
                       <li>Sharing confidential data you don't own</li>
                    </ul>
                 </div>
                 <div>
                    <h3 className="text-white font-display text-xl mb-2">Also Prohibited</h3>
                    <ul className="list-disc pl-5 space-y-2 marker:text-red-500 text-gray-400">
                       <li>Account sharing or reselling access</li>
                       <li>Uploading harmful/hate content</li>
                       <li>Misrepresenting your identity</li>
                       <li>Using for regulated decisions without advice</li>
                    </ul>
                 </div>
              </div>
            </section>

            {/* 7. IP */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">7. Intellectual Property Rights</h2>
              <p className="mb-4"><strong>We Own:</strong> The platform code, design, AI models, algorithms, and branding.</p>
              <p className="mb-4"><strong>Your License:</strong> Limited, non-transferable license to use the Service for your personal strategic decisions.</p>
            </section>

            {/* 8. Content Ownership */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">8. User Content Ownership</h2>
              <p className="mb-4"><strong>You Own:</strong> Your strategic inputs, Decision Canvas, uploaded files, and generated reports. We process this solely to provide the Service.</p>
              <p><strong>Pattern Learning:</strong> We analyze anonymized usage patterns (Tier 2) to improve agents unless you opt-out. Your specific content is never included in this learning.</p>
            </section>

            {/* 9. Use of Agents */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">9. Your Use of Our Agents</h2>
              <p className="mb-4">Agents synthesize information to test your decisions. They are NOT replacements for human judgment or professional advisors. You must independently verify all outputs.</p>
              <p>Agent logic changes over time; identical questions may yield different answers as the system improves.</p>
            </section>

            {/* 10. Liability */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">10. Limitation of Liability and Disclaimers</h2>
              <div className="p-6 border border-white/10 bg-white/5 mb-6">
                 <p className="uppercase tracking-widest text-sm text-[#6e683b] mb-2 font-bold">Disclaimer</p>
                 <p className="italic text-white">The Service is provided "AS-IS". We make no warranties regarding accuracy, reliability, or fitness for purpose.</p>
              </div>
              <p className="mb-4">We are NOT liable for direct, indirect, consequential, or special damages, including lost profits or data. Our maximum liability is capped at the amount you paid in the preceding 12 months.</p>
            </section>

            {/* 11. Indemnification */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">11. Indemnification</h2>
              <p>You agree to indemnify and hold us harmless from claims arising from your violation of these Terms, your illegal use, your data breaches, or decisions you made using the Service.</p>
            </section>

            {/* 12. Availability */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">12. Service Availability and Support</h2>
              <p className="mb-4"><strong>Commitment:</strong> 99.5% monthly uptime. Excludes scheduled maintenance and force majeure.</p>
              <p><strong>Remedy:</strong> Service credit up to 1 month subscription for uptime breaches.</p>
            </section>

            {/* 13. End of Life */}
            <section>
               <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">13. End-of-Life and Service Discontinuation</h2>
               <p>If we discontinue the Service, we provide 90 days notice. You will have full access to export your data during this wind-down period. We will provide prorated refunds for unused time.</p>
            </section>

            {/* 14. Rate Limiting */}
            <section>
               <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">14. Rate Limiting and Usage Restrictions</h2>
               <p className="mb-4">To ensure fair access, we enforce limits (e.g., 60 queries/hour, 50GB storage). Exceeding limits results in throttling. Automated abuse may lead to suspension.</p>
            </section>

            {/* 15. Beta */}
            <section>
               <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">15. Beta Status and Early-Stage Features</h2>
               <p>The Service is in Beta. Features may change, agents may be updated, and bugs may occur. You waive claims related to the Beta nature of the Service (e.g., feature changes).</p>
            </section>

            {/* 16. Competitive Use */}
            <section>
               <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">16. Competitive Use and Acceptable Restrictions</h2>
               <p className="mb-4">You may NOT use the service to train competing AI models, reverse-engineer our agents, or scrape data. We monitor for bulk extraction patterns.</p>
               <p>Legitimate benchmarking and individual usage is permitted.</p>
            </section>

            {/* 17. SLAs */}
            <section>
               <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">17. Support and Response SLAs</h2>
               <div className="overflow-x-auto mb-6">
                <table className="w-full text-left text-base border border-white/10">
                    <thead className="bg-white/5">
                        <tr>
                            <th className="p-4 border-r border-white/10 text-[#6e683b]">Severity</th>
                            <th className="p-4 border-r border-white/10 text-[#6e683b]">Definition</th>
                            <th className="p-4 border-r border-white/10 text-[#6e683b]">Response SLA</th>
                            <th className="p-4 text-[#6e683b]">Resolution (Best Effort)</th>
                        </tr>
                    </thead>
                    <tbody className="text-gray-400">
                        <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Critical</td><td className="p-4 border-r border-white/5">Service down, data loss</td><td className="p-4 border-r border-white/5">1 hour</td><td className="p-4">4 hours</td></tr>
                        <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">High</td><td className="p-4 border-r border-white/5">Core feature broken</td><td className="p-4 border-r border-white/5">4 hours</td><td className="p-4">24 hours</td></tr>
                        <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Medium</td><td className="p-4 border-r border-white/5">Partial issue, workaround</td><td className="p-4 border-r border-white/5">8 hours</td><td className="p-4">48 hours</td></tr>
                        <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Low</td><td className="p-4 border-r border-white/5">General question, cosmetic</td><td className="p-4 border-r border-white/5">24 hours</td><td className="p-4">5 days</td></tr>
                    </tbody>
                </table>
               </div>
               <p>Support Hours: M-F 9am-5pm PT. Critical issues prioritized 24/7.</p>
            </section>

            {/* 18. Enterprise/DPA */}
            <section>
               <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">18. Enterprise/GDPR Data Processing Agreement Reference</h2>
               <p>For enterprise or GDPR-regulated customers, we offer a formal Data Processing Agreement (DPA) incorporating SCCs. Email info@aiaugmented.io to request.</p>
            </section>

            {/* 19. Regulated Industries */}
            <section>
               <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">19. Regulated Industries Disclaimer and Restrictions</h2>
               <div className="p-6 border-l-2 border-red-900 bg-white/[0.02]">
                  <strong className="block text-white mb-2">IMPORTANT:</strong>
                  <p className="mb-4">This Service CANNOT provide legal, financial, or medical advice. If you work in a regulated industry (Finance, Healthcare, Law), you MUST consult licensed professionals and verify all outputs.</p>
                  <p>We are not liable for penalties resulting from your reliance on our agents for regulated decisions.</p>
               </div>
            </section>

            {/* 20. Limits */}
            <section>
               <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">20. Account Limits and Resource Allocation</h2>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <table className="text-left text-base border border-white/10 w-full">
                      <thead className="bg-white/5"><tr><th className="p-3 text-[#6e683b]" colSpan={2}>Storage</th></tr></thead>
                      <tbody className="text-gray-400">
                          <tr className="border-t border-white/5"><td className="p-3 border-r border-white/5">Total Storage</td><td className="p-3">50GB</td></tr>
                          <tr className="border-t border-white/5"><td className="p-3 border-r border-white/5">File Upload</td><td className="p-3">100MB / file</td></tr>
                          <tr className="border-t border-white/5"><td className="p-3 border-r border-white/5">File Count</td><td className="p-3">1,000 files</td></tr>
                      </tbody>
                  </table>
                  <table className="text-left text-base border border-white/10 w-full">
                      <thead className="bg-white/5"><tr><th className="p-3 text-[#6e683b]" colSpan={2}>Query Limits</th></tr></thead>
                      <tbody className="text-gray-400">
                          <tr className="border-t border-white/5"><td className="p-3 border-r border-white/5">Rate Limit</td><td className="p-3">60 queries / hour</td></tr>
                          <tr className="border-t border-white/5"><td className="p-3 border-r border-white/5">Concurrency</td><td className="p-3">5 simultaneous</td></tr>
                          <tr className="border-t border-white/5"><td className="p-3 border-r border-white/5">Exports</td><td className="p-3">10 per day</td></tr>
                      </tbody>
                  </table>
               </div>
            </section>

            {/* 21-24 Content, Feedback, Inactivity, Backup */}
            <section>
               <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">21-24. Operations Policies</h2>
               <p className="mb-2"><strong>Content Removal:</strong> We may remove illegal or violating content. You can appeal.</p>
               <p className="mb-2"><strong>Feedback:</strong> You grant us rights to use your suggestions.</p>
               <p className="mb-2"><strong>Inactivity:</strong> Accounts inactive for 12 months may be archived.</p>
               <p className="mb-2"><strong>Backups:</strong> We maintain rolling 90-day backups. We are not a permanent archive service.</p>
            </section>

            <div className="text-center pt-12 border-t border-white/5">
                <p className="text-sm text-gray-500">Last Updated: October 19, 2025</p>
            </div>

          </GlassContainer>
        </div>
      </section>
      
      <Footer onNavigate={onNavigate} />
    </div>
  );
};