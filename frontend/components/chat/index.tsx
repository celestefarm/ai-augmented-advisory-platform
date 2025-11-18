
"use client";

import { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, Sparkles } from "lucide-react";

import { useStore } from "@/store";
import { Badge } from "@/components/ui/badge";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";

export default function Chat() {
  const { 
    messages, 
    currentConversationId,
    conversations,
    handleSendMessage, 
    isProcessing 
  } = useStore();

  // Debug logging
  useEffect(() => {
    console.log('🟡 [Chat] Re-rendered');
    console.log('🟡 [Chat] Messages count:', messages.length);
    console.log('🟡 [Chat] Current conversation:', currentConversationId);
    console.log('🟡 [Chat] Messages:', messages);
  }, [messages, currentConversationId]);

  // Get current conversation details
  const currentConversation = conversations.find(
    c => c.id === currentConversationId
  );

  // Scroll to bottom when messages change
  useEffect(() => {
    const timer = setTimeout(() => {
      const messagesContainer = document.getElementById('chat-messages-container');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [messages.length]);

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex h-14 items-center justify-between border-b border-border bg-card px-6">
        <div className="flex items-center gap-3">
          <MessageSquare className="h-5 w-5 text-muted-foreground" />
          <h1 className="text-lg font-semibold">
            {currentConversation?.title || "New Chat"}
          </h1>
          {messages.length > 0 && (
            <Badge variant="secondary" className="text-xs">
              {messages.length} {messages.length === 1 ? 'message' : 'messages'}
            </Badge>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div 
        id="chat-messages-container"
        className="flex-1 overflow-y-auto"
      >
        <AnimatePresence mode="wait">
          {messages.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex h-full items-center justify-center"
            >
              <div className="text-center max-w-md px-4">
                <div className="mb-4 flex justify-center">
                  <div className="rounded-full bg-primary/10 p-6">
                    <Sparkles className="h-12 w-12 text-primary" />
                  </div>
                </div>
                <h2 className="text-2xl font-semibold mb-2">
                  {currentConversation 
                    ? `Continue: ${currentConversation.title}`
                    : "Start a New Conversation"
                  }
                </h2>
                <p className="text-muted-foreground">
                  {currentConversation
                    ? "No messages yet in this conversation. Type below to continue."
                    : "Ask me anything! I'm here to help with strategic insights and analysis."}
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="messages"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <ChatMessages messages={messages} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Input Area */}
      <ChatInput 
        onSendMessage={handleSendMessage}
        disabled={isProcessing}
      />
    </div>
  );
}