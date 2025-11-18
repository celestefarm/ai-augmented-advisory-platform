"use client";

import { MessageSquare } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface ChatHeaderProps {
  conversationTitle?: string;
  messageCount?: number;
}

export function ChatHeader({ conversationTitle, messageCount = 0 }: ChatHeaderProps) {
  return (
    <div className="flex h-14 items-center justify-between border-b border-border bg-card px-6">
      <div className="flex items-center gap-3">
        <MessageSquare className="h-5 w-5 text-muted-foreground" />
        <h1 className="text-lg font-semibold">
          {conversationTitle || "New Chat"}
        </h1>
        {messageCount > 0 && (
          <Badge variant="secondary" className="text-xs">
            {messageCount} {messageCount === 1 ? 'message' : 'messages'}
          </Badge>
        )}
      </div>
    </div>
  );
}