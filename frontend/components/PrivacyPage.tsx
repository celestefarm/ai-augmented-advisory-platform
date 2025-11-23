'use client';

import React from 'react';
import { GlassContainer } from './OverlaySections';
import { Footer } from './Footer';

interface PrivacyPageProps {
  onNavigate?: (page: string) => void;
}

export const PrivacyPage: React.FC<PrivacyPageProps> = ({ onNavigate }) => {
  return (
    <div className="relative w-full min-h-screen bg-[#050505]">
      <section className="pt-40 px-6 relative z-10">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <span className="inline-block py-1 px-3 border border-[#6e683b]/30 rounded-full bg-[#6e683b]/5 text-[#6e683b] text-sm tracking-[0.3em] uppercase mb-8 font-bold">
              Legal Protocols
            </span>
            <h1 className="text-4xl md:text-6xl font-display font-light text-white mb-6">Privacy Policy</h1>
            <p className="text-gray-400 text-base uppercase tracking-widest mb-2">Effective Date: October 19, 2025</p>
            <p className="text-gray-500 text-sm uppercase tracking-widest">
              Company: AI-Augmented | Service: AI-Augmented (The "Platform") | Contact: info@aiaugmented.io
            </p>
          </div>

          <GlassContainer className="space-y-16 text-lg font-light text-gray-300 leading-relaxed">
            
            {/* Intro */}
            <div>
              <h2 className="text-2xl font-display text-white mb-6">Our Core Commitment</h2>
              <p className="mb-4">Your strategic thinking is yours. Your proprietary content stays protected. Your decisions remain confidential.</p>
              <p className="mb-4">We use AI to help you think sharply. We improve our AI responsibly. We never compromise your privacy in the process.</p>
              <p>This privacy policy explains exactly how we do that.</p>
            </div>

            {/* 1. Proprietary Content */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">1. The Proprietary Content Protection Pledge</h2>
              
              <h3 className="text-white font-display text-xl mb-3 mt-6">What We Promise</h3>
              <p className="mb-4">Your strategic inputs, decisions, and proprietary business content will NEVER be used to train, fine-tune, or improve our core AI models.</p>
              
              <h3 className="text-white font-display text-xl mb-3 mt-6">Specifically</h3>
              <ul className="list-disc pl-5 space-y-2 marker:text-[#6e683b] mb-6">
                <li>Your strategic questions and decision frameworks stay private</li>
                <li>Your Decision Canvas and analysis outputs are yours alone</li>
                <li>Your uploaded documents and context files are protected</li>
                <li>Your competitive analysis remains confidential</li>
                <li>Your thinking process is never exposed to external parties</li>
              </ul>

              <h3 className="text-white font-display text-xl mb-3 mt-6">How We Keep This Promise</h3>
              <p className="mb-4">Your proprietary content is processed in isolation. It is used exclusively to:</p>
              <ul className="list-disc pl-5 space-y-2 marker:text-[#6e683b] mb-6">
                <li>Generate the insights and analysis you request</li>
                <li>Maintain your Permanent Memory within your account</li>
                <li>Improve your personal user experience (within your account only)</li>
              </ul>
              <p>Your content does NOT feed into our model training pipeline. Your competitors' agents don't learn from your strategic insights. Ever.</p>
            </section>

            {/* 2. How We Collect */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">2. How We Collect and Use Data</h2>
              <p className="mb-6 italic text-gray-500">To build trust, we're transparent about what data we collect and why.</p>

              <h3 className="text-white font-display text-xl mb-3 mt-6">Three Tiers of Data</h3>

              <div className="mb-8">
                <h3 className="text-[#6e683b] text-sm uppercase tracking-widest mb-4 font-bold">Tier 1: Proprietary Content (Your Strategic Thinking)</h3>
                <div className="pl-4 border-l border-white/10">
                    <p className="mb-2"><strong className="text-white">What We Collect:</strong> Strategic questions, Decision Canvas inputs, uploaded documents, conversation history, generated reports.</p>
                    <p className="mb-2"><strong className="text-white">Why:</strong> To analyze your decisions and maintain your strategic memory.</p>
                    <p className="mb-2"><strong className="text-white">What We DO NOT Do:</strong> Train our AI models on your content, share with competitors, or expose your thinking process.</p>
                    <p className="mb-2"><strong className="text-white">Control:</strong> You own all content. Export or delete anytime.</p>
                </div>
              </div>

              <div className="mb-8">
                <h3 className="text-[#6e683b] text-sm uppercase tracking-widest mb-4 font-bold">Tier 2: Interaction Patterns (How You Use AI-Augmented)</h3>
                <div className="pl-4 border-l border-white/10">
                    <p className="mb-2"><strong className="text-white">What We Collect:</strong> Valuable decision types, effective agent combinations, anonymized aggregate outcomes.</p>
                    <p className="mb-2"><strong className="text-white">Why:</strong> To make our agents smarter for all users.</p>
                    <p className="mb-2"><strong className="text-white">Anonymization:</strong> Proprietary content is removed. Identity is tokenized. We see "Financial analysis + Risk modeling works", not your specific deal details.</p>
                    <p className="mb-2"><strong className="text-white">Consent:</strong> You can opt-out of this pattern learning by emailing info@aiaugmented.io.</p>
                </div>
              </div>

              <div className="mb-8">
                <h3 className="text-[#6e683b] text-sm uppercase tracking-widest mb-4 font-bold">Tier 3: Technical Data (Platform Operations)</h3>
                <div className="pl-4 border-l border-white/10">
                    <p className="mb-2"><strong className="text-white">What We Collect:</strong> Login info, IP addresses, system metrics, error logs.</p>
                    <p className="mb-2"><strong className="text-white">Why:</strong> Security, fraud prevention, performance monitoring.</p>
                </div>
              </div>
            </section>

            {/* 3. Data Retention */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">3. Data Retention and Deletion</h2>
              
              <h3 className="text-white font-display text-xl mb-4">For Strategic Authority Plan (Paid Users)</h3>
              <div className="overflow-x-auto mb-8">
                <table className="w-full text-left text-base border border-white/10">
                    <thead className="bg-white/5">
                        <tr>
                            <th className="p-4 border-r border-white/10 text-[#6e683b]">Data Category</th>
                            <th className="p-4 border-r border-white/10 text-[#6e683b]">Retention</th>
                            <th className="p-4 text-[#6e683b]">Purpose</th>
                        </tr>
                    </thead>
                    <tbody className="text-gray-400">
                        <tr className="border-t border-white/5">
                            <td className="p-4 border-r border-white/5">Proprietary Content</td>
                            <td className="p-4 border-r border-white/5">Permanent (until you delete)</td>
                            <td className="p-4">Your Permanent Memory feature</td>
                        </tr>
                        <tr className="border-t border-white/5">
                            <td className="p-4 border-r border-white/5">Interaction Patterns</td>
                            <td className="p-4 border-r border-white/5">Indefinite (anonymized)</td>
                            <td className="p-4">Platform improvement</td>
                        </tr>
                        <tr className="border-t border-white/5">
                            <td className="p-4 border-r border-white/5">Technical Data</td>
                            <td className="p-4 border-r border-white/5">12 months</td>
                            <td className="p-4">Security and operations</td>
                        </tr>
                        <tr className="border-t border-white/5">
                            <td className="p-4 border-r border-white/5">Account Data</td>
                            <td className="p-4 border-r border-white/5">Until account deletion</td>
                            <td className="p-4">Service management</td>
                        </tr>
                    </tbody>
                </table>
              </div>

              <h3 className="text-white font-display text-xl mb-3">Upon Account Deletion</h3>
              <ul className="list-disc pl-5 space-y-2 marker:text-[#6e683b] mb-6">
                <li>Your proprietary content is permanently deleted within 30 days</li>
                <li>Your account data is removed</li>
                <li>Anonymized interaction patterns remain (cannot be traced to you)</li>
                <li>Technical logs are deleted after 12 months</li>
              </ul>

              <h3 className="text-white font-display text-xl mb-3">Data Export</h3>
              <p className="mb-4">You can export all your Strategic Content anytime. Download your Decision Canvas, reports, and conversation history. Take your thinking with you, in full.</p>
            </section>

            {/* 4. Security */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">4. How We Keep Your Data Secure</h2>
              <p className="mb-4"><strong className="text-white">Encryption Standards:</strong> Data in transit uses TLS. Data at rest uses enterprise-grade encryption. Access is role-based.</p>
              <p className="mb-4"><strong className="text-white">Third-Party Processors:</strong> We work with trusted partners (cloud, payment, backup) under strict data protection agreements.</p>
              <p className="mb-4"><strong className="text-white">Proprietary Protection:</strong> Our technical architecture, anonymization methods, and security protocols are proprietary.</p>
            </section>

            {/* 5. Incidents */}
            <section>
              <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">5. Data Security Incidents and Breach Notification</h2>
              <p className="mb-4">In the event of a breach, we commit to transparency. We investigate immediately and notify you promptly (within 72 hours under GDPR). We will detail what data was involved and steps taken.</p>
              <p className="mb-4">To report a vulnerability, email <span className="text-[#6e683b]">info@aiaugmented.io</span>.</p>
            </section>

            {/* 6. Third Party Uploads */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">6. Third-Party Data in User Uploads</h2>
                <p className="mb-4">You are responsible for ensuring any uploaded data complies with law. Do not upload personal data of others without consent. If found, we may delete it.</p>
            </section>

            {/* 7. Govt Requests */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">7. Government Requests and Law Enforcement</h2>
                <p className="mb-4">We require valid legal process (warrants/subpoenas) to disclose data. We evaluate legitimacy, resist broad requests, and notify you unless legally prohibited.</p>
            </section>

            {/* 8. Sensitive Data */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">8. Sensitive Personal Data Handling</h2>
                <p className="mb-4">We recommend redacting sensitive info (health, finance, IDs) before upload. If you must upload sensitive data, acknowledge responsibility. For enterprise needs, we can execute a Data Processing Agreement (DPA).</p>
            </section>

            {/* 9. Business Transfer */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">9. Business Transfer, Acquisition, or Merger</h2>
                <p className="mb-4">If AI-Augmented is acquired, you will be notified. You have 30 days to export/delete your data before transfer. Your "No-Training Pledge" remains protected during transfer.</p>
            </section>

            {/* 10. Enterprise */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">10. Enterprise Audit and Compliance</h2>
                <p className="mb-4">For enterprise customers, we offer DPAs, Security Certifications (SOC 2 avail upon request), Audit Rights, Subprocessor visibility, and Incident Response SLAs. Email <span className="text-[#6e683b]">info@aiaugmented.io</span> for enterprise compliance.</p>
            </section>

            {/* 11. Third Party Agents */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">11. Third-Party Agents and Data Processing</h2>
                <p className="mb-4">When using agents that access real-time external data, we transmit minimal anonymized context. Your proprietary identity is never included in third-party requests.</p>
            </section>

            {/* 12. Rights */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">12. Your Data Protection Rights</h2>
                <p className="mb-4">We respect GDPR, UK DPA, CCPA, and PDPA rights.</p>
                <ul className="list-disc pl-5 space-y-2 marker:text-[#6e683b] mb-6">
                    <li><strong>Right of Access:</strong> Request a copy of your data.</li>
                    <li><strong>Right to Rectification:</strong> Correct inaccurate info.</li>
                    <li><strong>Right to Erasure:</strong> Request deletion.</li>
                    <li><strong>Right to Data Portability:</strong> Export to portable format.</li>
                    <li><strong>Right to Restrict/Object:</strong> Limit processing or opt-out of pattern learning.</li>
                </ul>
                <p>Contact <span className="text-[#6e683b]">info@aiaugmented.io</span> to exercise these rights.</p>
            </section>

            {/* 13. International */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">13. International Data Transfers</h2>
                <p className="mb-4">We process data globally using legal safeguards (SCCs). We do not sell data to competitors.</p>
            </section>

            {/* 14-16 Misc */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">14-16. Tracking, Minors, Beta</h2>
                <p className="mb-2"><strong>14. Cookies:</strong> We use essential and analytics cookies. You can control them in your browser.</p>
                <p className="mb-2"><strong>15. Children:</strong> Service is for professionals 18+. We do not knowingly collect data from minors.</p>
                <p className="mb-2"><strong>16. Beta Status:</strong> Policies may evolve, but our core data protection promises remain stable.</p>
            </section>

            {/* 17. Request Procedure */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">17. Data Subject Rights Request Procedure</h2>
                <p className="mb-4">Email <span className="text-[#6e683b]">info@aiaugmented.io</span>. We verify identity before processing.</p>
                
                <div className="overflow-x-auto mb-8">
                    <table className="w-full text-left text-base border border-white/10">
                        <thead className="bg-white/5">
                            <tr>
                                <th className="p-4 border-r border-white/10 text-[#6e683b]">Request Type</th>
                                <th className="p-4 border-r border-white/10 text-[#6e683b]">Legal Basis</th>
                                <th className="p-4 text-[#6e683b]">SLA</th>
                            </tr>
                        </thead>
                        <tbody className="text-gray-400">
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Access/Portability</td><td className="p-4 border-r border-white/5">GDPR Art 15/20</td><td className="p-4">30 days</td></tr>
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Deletion/Erasure</td><td className="p-4 border-r border-white/5">GDPR Art 17</td><td className="p-4">30 days</td></tr>
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Rectification</td><td className="p-4 border-r border-white/5">GDPR Art 16</td><td className="p-4">10 days</td></tr>
                        </tbody>
                    </table>
                </div>
                <p className="text-sm text-gray-500">Requests are free unless unfounded/excessive. We accept authorized agent requests.</p>
            </section>

            {/* 18. CCPA */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">18. CCPA-Specific Privacy Rights (California Residents)</h2>
                <p className="mb-4">California residents have specific rights:</p>
                <ul className="list-disc pl-5 space-y-2 marker:text-[#6e683b] mb-6">
                    <li>Right to Know (categories, sources, purposes)</li>
                    <li>Right to Delete (subject to exceptions)</li>
                    <li>Right to Correct inaccurate information</li>
                    <li>Right to Opt-Out of Sale/Sharing (We do not sell data)</li>
                    <li>Right to Limit Use of sensitive info</li>
                    <li>Right to Non-Discrimination</li>
                </ul>
                <p>Email <span className="text-[#6e683b]">info@aiaugmented.io</span> for any CCPA requests.</p>
            </section>

            {/* 19-21 Rights Details */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">19-21. Additional Rights Details</h2>
                <p className="mb-4"><strong>19. Right to Withdraw Consent:</strong> You can withdraw consent for processing or pattern learning anytime by email.</p>
                <p className="mb-4"><strong>20. Anti-Discrimination:</strong> We will not discriminate against you for exercising privacy rights.</p>
                <p className="mb-4"><strong>21. Right to Restrict Processing:</strong> You can request we pause processing your data during disputes.</p>
            </section>

            {/* 22. Detailed Retention */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">22. Detailed Data Retention Schedule</h2>
                <div className="overflow-x-auto mb-8">
                    <table className="w-full text-left text-base border border-white/10">
                        <thead className="bg-white/5">
                            <tr>
                                <th className="p-4 border-r border-white/10 text-[#6e683b]">Data Category</th>
                                <th className="p-4 border-r border-white/10 text-[#6e683b]">Retention Period</th>
                                <th className="p-4 text-[#6e683b]">Purpose</th>
                            </tr>
                        </thead>
                        <tbody className="text-gray-400">
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Strategic Content</td><td className="p-4 border-r border-white/5">Until deletion + 30 days</td><td className="p-4">Memory</td></tr>
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Account Info</td><td className="p-4 border-r border-white/5">Until deletion + 2 years</td><td className="p-4">Legal</td></tr>
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Logs (Tech/IP)</td><td className="p-4 border-r border-white/5">6-12 months</td><td className="p-4">Security</td></tr>
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Backups</td><td className="p-4 border-r border-white/5">90 days</td><td className="p-4">Recovery</td></tr>
                        </tbody>
                    </table>
                </div>
            </section>

            {/* 23-27 Automated Decisions, Complaints, Purpose, Verification, Transparency */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">23-27. Operational Policies</h2>
                <div className="space-y-6">
                    <div>
                        <strong className="text-white block mb-2">23. Right to Restrict Automated Decision-Making</strong>
                        <p>Our agents provide recommendations; YOU make the final decision. We don't use automated profiling to significantly affect you legally.</p>
                    </div>
                    <div>
                        <strong className="text-white block mb-2">24. Right to Lodge a Complaint</strong>
                        <p>You can lodge complaints with ICO (UK), AG (California), or PDPC (Singapore). We recommend contacting us first to resolve issues.</p>
                    </div>
                    <div>
                        <strong className="text-white block mb-2">25. Purpose Limitation and Data Minimization</strong>
                        <p>We only use data for stated purposes. We do not repurpose data without consent.</p>
                    </div>
                    <div>
                        <strong className="text-white block mb-2">26. Verification and Third-Party Authorization</strong>
                        <p>We verify identity before processing data subject requests.</p>
                    </div>
                    <div>
                        <strong className="text-white block mb-2">27. Transparency Reporting</strong>
                        <p>We publish annual reports on security, government requests, and privacy compliance.</p>
                    </div>
                </div>
            </section>

            {/* 28. Contact & Support */}
            <section>
                <h2 className="text-3xl font-display text-white mb-6 border-b border-white/10 pb-4">28. Complaints, Inquiries, and Support</h2>
                <p className="mb-6">For all privacy matters, email <span className="text-[#6e683b]">info@aiaugmented.io</span>.</p>
                
                <div className="overflow-x-auto mb-8">
                    <table className="w-full text-left text-base border border-white/10">
                        <thead className="bg-white/5">
                            <tr>
                                <th className="p-4 border-r border-white/10 text-[#6e683b]">Request Type</th>
                                <th className="p-4 border-r border-white/10 text-[#6e683b]">Contact</th>
                                <th className="p-4 text-[#6e683b]">Response Time</th>
                            </tr>
                        </thead>
                        <tbody className="text-gray-400">
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Privacy Inquiries</td><td className="p-4 border-r border-white/5">info@aiaugmented.io</td><td className="p-4">5 days</td></tr>
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Security Issues</td><td className="p-4 border-r border-white/5">info@aiaugmented.io</td><td className="p-4">48 hours</td></tr>
                            <tr className="border-t border-white/5"><td className="p-4 border-r border-white/5">Data Requests</td><td className="p-4 border-r border-white/5">info@aiaugmented.io</td><td className="p-4">30-45 days</td></tr>
                        </tbody>
                    </table>
                </div>
                <p>We designate an independent DPO for escalations.</p>
            </section>

            {/* 29-31 Closing */}
            <section className="bg-white/5 p-8 rounded-sm border border-white/10">
                <h2 className="text-2xl font-display text-white mb-4">29-31. Summary & Definitions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-base">
                    <div>
                        <h4 className="text-[#6e683b] uppercase tracking-widest mb-2 font-bold">We Protect</h4>
                        <p className="mb-2">Your proprietary content and decision process.</p>
                        <p className="mb-2">Your business confidentiality.</p>
                        <p>Your right to export/delete anytime.</p>
                    </div>
                    <div>
                        <h4 className="text-[#6e683b] uppercase tracking-widest mb-2 font-bold">We Never</h4>
                        <p className="mb-2">Train models on your proprietary inputs.</p>
                        <p className="mb-2">Sell your personal or strategic content.</p>
                        <p>Compromise data protection for profit.</p>
                    </div>
                </div>
                <div className="mt-6 pt-4 border-t border-white/5 text-base text-gray-500">
                  <p className="mb-2"><strong>Definitions:</strong> "Strategic Content" refers to your inputs and decisions. "Interaction Patterns" refers to anonymized usage data.</p>
                  <p><strong>Governing Law:</strong> Applicable data protection laws globally.</p>
                </div>
            </section>

            <div className="text-center pt-12 border-t border-white/5">
                <p className="text-sm text-gray-500">Last Updated: October 19, 2025 | Next Review: October 19, 2026</p>
            </div>

          </GlassContainer>
        </div>
      </section>
      
      <Footer onNavigate={onNavigate} />
    </div>
  );
};