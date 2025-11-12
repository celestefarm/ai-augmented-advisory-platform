"use client";

import { useState } from "react";

import { motion } from "framer-motion";
import {
  MessageSquare,
  Plus,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Menu,
  X,
} from "lucide-react";
import { useRouter } from "next/navigation";

import { useStore } from "@/store";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { ROUTES } from "@/routes";

export function Sidebar() {
  const router = useRouter();
  const { clearChat, user, logout } = useStore();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    router.push(ROUTES.login);
  };

  const handleNewChat = () => {
    clearChat();
    setIsMobileOpen(false);
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="fixed top-3 left-3 z-50 lg:hidden"
      >
        {isMobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          width: isSidebarCollapsed ? "60px" : "260px",
        }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className={`fixed inset-y-0 left-0 z-40 flex flex-col border-r border-border bg-card transition-transform lg:static lg:translate-x-0 ${
          isMobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        {/* Sidebar Header */}
        <div className="flex h-14 shrink-0 items-center justify-between border-b border-border px-4">
          {!isSidebarCollapsed && (
            <motion.h2
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-lg font-semibold"
            >
              AI-Augmented
            </motion.h2>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className={`shrink-0 ${isSidebarCollapsed ? "mx-auto" : "ml-auto"} hidden lg:flex`}
          >
            {isSidebarCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* New Chat Button */}
        <div className="shrink-0 p-3">
          <Button
            onClick={handleNewChat}
            className={`w-full gap-2 ${isSidebarCollapsed ? "justify-center px-0" : "justify-start"}`}
            variant="default"
            title={isSidebarCollapsed ? "New chat" : undefined}
          >
            <Plus className="h-4 w-4 shrink-0" />
            {!isSidebarCollapsed && <span>New chat</span>}
          </Button>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto px-3">
          <div className="space-y-1 py-2">
            <Button
              variant="ghost"
              className={`w-full gap-3 ${isSidebarCollapsed ? "justify-center px-0" : "justify-start"}`}
              onClick={() => setIsMobileOpen(false)}
              title={isSidebarCollapsed ? "Chats" : undefined}
            >
              <MessageSquare className="h-4 w-4 shrink-0" />
              {!isSidebarCollapsed && <span>Chats</span>}
            </Button>
          </div>

          {/* Recent Chats */}
          {!isSidebarCollapsed && (
            <div className="mt-6 pb-4">
              <h3 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Recent
              </h3>
              <div className="space-y-1">
                <Button
                  variant="ghost"
                  className="h-auto w-full justify-start py-2 text-left text-sm"
                  onClick={() => setIsMobileOpen(false)}
                >
                  <span className="truncate">Sample conversation 1</span>
                </Button>
                <Button
                  variant="ghost"
                  className="h-auto w-full justify-start py-2 text-left text-sm"
                  onClick={() => setIsMobileOpen(false)}
                >
                  <span className="truncate">Sample conversation 2</span>
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* User Profile */}
        <div className="shrink-0 border-t border-border p-3">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className={`h-auto w-full gap-3 py-2 ${isSidebarCollapsed ? "justify-center px-0" : "justify-start"}`}
                title={isSidebarCollapsed ? user?.full_name || user?.email || "User" : undefined}
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                  {user?.first_name?.[0] || user?.email?.[0] || "U"}
                </div>
                {!isSidebarCollapsed && (
                  <div className="flex flex-col items-start overflow-hidden">
                    <span className="truncate text-sm font-medium">
                      {user?.full_name || user?.email || "User"}
                    </span>
                    <span className="truncate text-xs text-muted-foreground">
                      {user?.subscription_tier || "Free"}
                    </span>
                  </div>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuItem onClick={() => router.push(ROUTES.settings)}>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </motion.aside>
    </>
  );
}