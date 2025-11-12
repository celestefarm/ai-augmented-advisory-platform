"use client";

import { Sidebar } from "@/components/sidebar/Sidebar";
import Chat from "@/components/chat";

export default function Dashboard() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      
      {/* Add left padding on mobile to account for the menu button */}
      <div className="flex flex-1 flex-col lg:pl-0">
        <Chat />
      </div>
    </div>
  );
}