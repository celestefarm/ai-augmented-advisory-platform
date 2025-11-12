"use client";

import { useEffect, useRef, useState } from "react";

import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { useStore } from "@/store";

const messageAnimation = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 },
};

const preprocessMarkdown = (content: string) => {
  return content.replace(/^• /gm, "- ");
};

export const ChatMessages = () => {
  const { messages, isProcessing } = useStore();

  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);

  const handleScroll = () => {
    if (!messagesContainerRef.current) return;

    const { scrollHeight, scrollTop, clientHeight } =
      messagesContainerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
    setShowScrollButton(!isNearBottom);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const hasStreamingMessage = messages.some(m => m.isStreaming);

    if (!hasStreamingMessage) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage?.sender === "user") {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        setShowScrollButton(false);
      }
    }
  }, [messages]);

  return (
    <div className="relative flex flex-1 flex-col overflow-hidden">
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
      >
        {/* Centered Container */}
        <div className="mx-auto max-w-3xl space-y-6 px-4 py-8">
          {messages.length === 0 && (
            <div className="flex h-[60vh] items-center justify-center">
              <div className="text-center">
                <div className="mb-4 inline-flex rounded-full bg-primary/10 p-4">
                  <svg
                    className="h-8 w-8 text-primary"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
                </div>
                <h2 className="mb-2 text-2xl font-semibold">
                  How can I help you today?
                </h2>
                <p className="text-sm text-muted-foreground">
                  Ask me anything to get started
                </p>
              </div>
            </div>
          )}

          <AnimatePresence mode="popLayout">
            {messages?.map((message, index) => {
              const isUser = message.sender === "user";
              return (
                <motion.div
                  key={message.id || index}
                  {...messageAnimation}
                  className={`flex ${isUser ? "justify-end" : "justify-start"}`}
                >
                  <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"} max-w-[85%]`}>
                    {/* Avatar */}
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                      {isUser ? "U" : "AI"}
                    </div>

                    {/* Message Content */}
                    <div
                      className={`flex flex-col gap-2 ${
                        isUser
                          ? "items-end"
                          : "items-start"
                      }`}
                    >
                      <div
                        className={`rounded-2xl px-4 py-3 ${
                          isUser
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        }`}
                      >
                        {isUser ? (
                          <p className="whitespace-pre-wrap text-sm leading-relaxed">
                            {message.content}
                          </p>
                        ) : (
                          <div className="prose prose-sm prose-headings:text-current prose-p:text-current prose-li:text-current prose-strong:text-current max-w-none dark:prose-invert">
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                p: ({ children }) => (
                                  <p className="mb-3 leading-relaxed last:mb-0">
                                    {children}
                                  </p>
                                ),
                                ul: ({ children }) => (
                                  <ul className="mb-3 ml-4 list-disc space-y-1 last:mb-0">
                                    {children}
                                  </ul>
                                ),
                                ol: ({ children }) => (
                                  <ol className="mb-3 ml-4 list-decimal space-y-1 last:mb-0">
                                    {children}
                                  </ol>
                                ),
                                li: ({ children }) => (
                                  <li className="leading-relaxed">{children}</li>
                                ),
                                strong: ({ children }) => (
                                  <strong className="font-semibold">
                                    {children}
                                  </strong>
                                ),
                                code: ({ children, className }) => {
                                  const isInline = !className?.includes("language-");
                                  return isInline ? (
                                    <code className="rounded bg-background/50 px-1.5 py-0.5 font-mono text-xs">
                                      {children}
                                    </code>
                                  ) : (
                                    <code className="my-2 block rounded-lg bg-background/50 p-4 font-mono text-xs">
                                      {children}
                                    </code>
                                  );
                                },
                                h3: ({ children }) => (
                                  <h3 className="mb-2 mt-4 text-base font-semibold">
                                    {children}
                                  </h3>
                                ),
                                blockquote: ({ children }) => (
                                  <blockquote className="my-3 border-l-2 border-border pl-4 italic">
                                    {children}
                                  </blockquote>
                                ),
                              }}
                            >
                              {preprocessMarkdown(message.content)}
                            </ReactMarkdown>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>

          {/* Typing Indicator */}
          <AnimatePresence>
            {isProcessing && !messages.some(m => m.isStreaming) && (
              <motion.div {...messageAnimation} className="flex justify-start">
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                    AI
                  </div>
                  <div className="flex items-center gap-1 rounded-2xl bg-muted px-4 py-3">
                    {[0, 1, 2].map(dot => (
                      <span
                        key={dot}
                        className="h-2 w-2 animate-bounce rounded-full bg-foreground/40"
                        style={{ animationDelay: `${dot * 0.15}s` }}
                      />
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Scroll to Bottom Button */}
      <AnimatePresence>
        {showScrollButton && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            onClick={scrollToBottom}
            className="absolute bottom-6 left-1/2 flex -translate-x-1/2 items-center justify-center rounded-full bg-primary p-2.5 text-primary-foreground shadow-lg transition-all hover:bg-primary/90 hover:shadow-xl"
            aria-label="Scroll to bottom"
          >
            <ChevronDown className="h-5 w-5" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
};