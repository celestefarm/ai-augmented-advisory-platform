"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

import { ArrowUp } from "lucide-react";

import { useStore } from "@/store";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export const ChatInput = () => {
  const { handleSendMessage, isProcessing } = useStore();
  const [inputValue, setInputValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus textarea on mount
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleSubmit = (e?: FormEvent) => {
    if (e) e.preventDefault();
    if (inputValue.trim() && !isProcessing) {
      handleSendMessage(inputValue.trim());
      setInputValue("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.focus();
        }
      }, 0);
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className=" border-border bg-background">
      <div className="mx-auto max-w-3xl px-4 py-4 sm:py-6">
        <form onSubmit={handleSubmit} className="relative">
          <div className="group relative flex items-end gap-2 rounded-2xl border border-border bg-card shadow-sm transition-shadow hover:shadow-md focus-within:border-primary focus-within:shadow-md">
            <Textarea
              ref={textareaRef}
              value={inputValue}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder="How can I Help you today..."
              className="max-h-100 min-h-[52px] flex-1 resize-none border-none bg-transparent px-4 py-3 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-0 sm:py-3.5"
              disabled={isProcessing}
              rows={1}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!inputValue.trim() || isProcessing}
              className="mb-2 mr-2 h-8 w-8 shrink-0 rounded-lg sm:h-9 sm:w-9"
            >
              <ArrowUp className="h-4 w-4" />
            </Button>
          </div>
          
          {/* Character hint */}
          <p className="mt-2 px-1 text-center text-xs text-muted-foreground sm:text-left">
            Press <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">Enter</kbd> to send, <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">Shift + Enter</kbd> for new line
          </p>
        </form>
      </div>
    </div>
  );
};