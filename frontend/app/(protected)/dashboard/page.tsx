"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Sidebar } from "@/components/sidebar/Sidebar";
import Chat from "@/components/chat";
import { useStore } from "@/store";

export default function Dashboard() {
  const searchParams = useSearchParams();
  const conversationId = searchParams.get('conversation');
  const workspaceId = searchParams.get('workspace');
  
  const { loadConversationMessages, setCurrentConversation, setCurrentWorkspace } = useStore();

  useEffect(() => {
    if (conversationId) {
      setCurrentConversation(conversationId);
      setCurrentWorkspace(workspaceId);
      loadConversationMessages(conversationId);
    }
  }, [conversationId, workspaceId]);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      
      <div className="flex flex-1 flex-col lg:pl-0">
        <Chat />
      </div>
    </div>
  );
}