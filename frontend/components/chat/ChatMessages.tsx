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

// Streaming text with blinking cursor
const StreamingText = ({ text }: { text: string }) => {
  return (
    <div className="prose prose-sm prose-headings:text-current prose-p:text-current prose-li:text-current prose-strong:text-current max-w-none dark:prose-invert">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => (
            <p className="mb-3 leading-relaxed last:mb-0">{children}</p>
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
          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
          strong: ({ children }) => (
            <strong className="font-semibold">{children}</strong>
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
            <h3 className="mb-2 mt-4 text-base font-semibold">{children}</h3>
          ),
          blockquote: ({ children }) => (
            <blockquote className="my-3 border-l-2 border-border pl-4 italic">
              {children}
            </blockquote>
          ),
        }}
      >
        {preprocessMarkdown(text)}
      </ReactMarkdown>
      {/* Blinking cursor for streaming */}
      <motion.span
        className="inline-block h-4 w-[2px] bg-primary ml-0.5"
        animate={{ opacity: [1, 0, 1] }}
        transition={{ duration: 0.8, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
};

// Typing indicator - Shows while waiting for response
const TypingIndicator = () => (
  <motion.div
    key="typing-indicator"
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    transition={{ duration: 0.2 }}
    className="flex justify-start"
  >
    <div className="flex gap-3 max-w-[85%]">
      {/* AI Avatar */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
        AI
      </div>

      {/* Bouncing dots bubble */}
      <div className="flex items-center gap-1.5 rounded-2xl bg-muted px-4 py-3">
        {[0, 1, 2].map((dot) => (
          <motion.span
            key={dot}
            className="h-2 w-2 rounded-full bg-foreground/40"
            animate={{
              y: [0, -8, 0],
              opacity: [0.4, 1, 0.4],
            }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
              delay: dot * 0.15,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
    </div>
  </motion.div>
);

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

  const scrollToBottom = (smooth = true) => {
    messagesEndRef.current?.scrollIntoView({
      behavior: smooth ? "smooth" : "auto",
    });
  };

  // Auto-scroll on new messages
  useEffect(() => {
    const hasStreamingMessage = messages.some((m) => m.isStreaming);

    if (!hasStreamingMessage) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage?.sender === "user") {
        scrollToBottom();
        setShowScrollButton(false);
      }
    }
  }, [messages.length]);

  // Smooth auto-scroll during typing
  useEffect(() => {
    const isTyping = messages.some((m) => m.isStreaming);

    if (isTyping) {
      const interval = setInterval(() => {
        const container = messagesContainerRef.current;
        if (container) {
          const { scrollHeight, scrollTop, clientHeight } = container;
          const isNearBottom = scrollHeight - scrollTop - clientHeight < 150;

          if (isNearBottom) {
            scrollToBottom();
          }
        }
      }, 100);

      return () => clearInterval(interval);
    }
  }, [messages]);

  // Auto-scroll when typing indicator appears
  useEffect(() => {
    if (isProcessing) {
      scrollToBottom();
    }
  }, [isProcessing]);

  // Show typing indicator when:
  // 1. isProcessing is true (question sent)
  // 2. AND no assistant message exists yet (waiting for first chunk)
  const hasAssistantMessage = messages.some((m) => m.sender === "assistant");
  const shouldShowTypingIndicator = isProcessing && !hasAssistantMessage;

  return (
    <div className="relative flex flex-1 flex-col overflow-hidden">
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto scroll-smooth"
      >
        <div className="mx-auto max-w-3xl space-y-6 px-4 py-8">
          {/* Empty State */}
          {messages.length === 0 && !isProcessing && (
            <div className="flex h-[60vh] items-center justify-center">
              <div className="text-center">
                <motion.div
                  className="mb-4 inline-flex rounded-full bg-primary/10 p-4"
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                >
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
                </motion.div>
                <h2 className="mb-2 text-2xl font-semibold">
                  How can I help you today?
                </h2>
                <p className="text-sm text-muted-foreground">
                  Ask me anything to get started
                </p>
              </div>
            </div>
          )}

          {/* Messages */}
          <AnimatePresence mode="popLayout">
            {messages?.map((message, index) => {
              const isUser = message.sender === "user";
              const isLastMessage = index === messages.length - 1;
              const isStreaming = isLastMessage && !isUser && message.isStreaming;

              return (
                <motion.div
                  key={message.id || index}
                  {...messageAnimation}
                  className={`flex ${isUser ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`flex gap-3 ${
                      isUser ? "flex-row-reverse" : "flex-row"
                    } max-w-[85%]`}
                  >
                    {/* Avatar */}
                    <motion.div
                      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.1 }}
                    >
                      {isUser ? "U" : "AI"}
                    </motion.div>

                    {/* Message Content */}
                    <div
                      className={`flex flex-col gap-2 ${
                        isUser ? "items-end" : "items-start"
                      }`}
                    >
                      <motion.div
                        className={`rounded-2xl px-4 py-3 ${
                          isUser
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        }`}
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.15 }}
                      >
                        {isUser ? (
                          <p className="whitespace-pre-wrap text-sm leading-relaxed">
                            {message.content}
                          </p>
                        ) : isStreaming ? (
                          // STREAMING: Show content with blinking cursor
                          <StreamingText text={message.content} />
                        ) : (
                          // COMPLETE: Normal markdown rendering
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
                                  const isInline = !className?.includes(
                                    "language-"
                                  );
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
                      </motion.div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>

          {/* TYPING INDICATOR - Shows while waiting for first chunk */}
          <AnimatePresence>
            {shouldShowTypingIndicator && <TypingIndicator />}
          </AnimatePresence>

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Scroll to Bottom Button */}
      <AnimatePresence>
        {showScrollButton && (
          <motion.button
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.9 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => scrollToBottom()}
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