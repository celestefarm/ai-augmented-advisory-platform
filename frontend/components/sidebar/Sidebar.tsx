// components/Sidebar.tsx - Add workspace management

"use client";

import { useEffect, useState } from "react";
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
  Folder,
  ChevronDown,
  ChevronUp,
  Home,
  MoreVertical,
  Trash2,
  Edit,
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
import { Badge } from "@/components/ui/badge";
import { CreateWorkspaceDialog, CreateChatDialog } from "@/components/dialogs/CreateWorkspaceDialog";
import { DeleteWorkspaceDialog } from "@/components/dialogs/DeleteWorkspaceDialog";

import { ROUTES, getChatRoute, getWorkspaceChatRoute } from "@/routes";

export function Sidebar() {
  const router = useRouter();
  const {
    user, 
    logout,
    workspaces,
    fetchWorkspaces,
    createWorkspace,
    deleteWorkspace,
    isLoadingWorkspaces,
    conversations,
    fetchConversations,
    deleteConversation,
    isLoadingConversations,
    setCurrentWorkspace,
    setCurrentConversation,
    currentConversationId,
    loadConversationMessages,
  } = useStore();
  
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [expandedWorkspaces, setExpandedWorkspaces] = useState<string[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [deleteWorkspaceId, setDeleteWorkspaceId] = useState<string | null>(null);

  // Fetch workspaces and conversations on mount
  useEffect(() => {
    if (user) {
      fetchWorkspaces();
      fetchConversations();
    }
  }, [user, fetchWorkspaces, fetchConversations]);

  const handleLogout = async () => {
    await logout();
    router.push(ROUTES.login);
  };


  const toggleWorkspace = async (workspaceId: string) => {
    // Close all other workspaces (only one open at a time)
    const isCurrentlyExpanded = expandedWorkspaces.includes(workspaceId);
    
    if (isCurrentlyExpanded) {
      // Close this workspace
      setExpandedWorkspaces([]);
    } else {
      // Close all others and open this one
      setExpandedWorkspaces([workspaceId]);
      
    }
  };

  const handleCreateWorkspace = async (data: {
    name: string;
    description: string;
    icon: string;
  }) => {
    await createWorkspace(data);
  };

  const handleDeleteWorkspace = async () => {
    if (deleteWorkspaceId) {
      await deleteWorkspace(deleteWorkspaceId);
      setDeleteWorkspaceId(null);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    if (confirm('Are you sure you want to delete this conversation?')) {
      await deleteConversation(conversationId);
    }
  };

  const handleSelectConversation = async (conversationId: string, workspaceId?: string | null) => {
    setCurrentConversation(conversationId);
    setCurrentWorkspace(workspaceId || null);
    
    // Load messages
    if (loadConversationMessages) {
      await loadConversationMessages(conversationId);
    }
    
    // Navigate to URL with conversation ID
    if (workspaceId) {
      router.push(getWorkspaceChatRoute(workspaceId, conversationId));
    } else {
      router.push(getChatRoute(conversationId));
    }
    
    setIsMobileOpen(false);
  };

  const workspaceToDelete = workspaces?.find(w => w.id === deleteWorkspaceId);

  // Get conversations for each workspace
  const getWorkspaceConversations = (workspaceId: string) => {
    return conversations.filter(c => c.workspace === workspaceId);
  };

  // Get quick chats (conversations without workspace)
  const getQuickChats = () => {
    return conversations.filter(c => !c.workspace);
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

        {/* Action Buttons */}
        <div className="shrink-0 space-y-2 p-3">
          <Button
            onClick={() => setIsCreateDialogOpen(true)}
            className={`w-full gap-2 ${isSidebarCollapsed ? "justify-center px-0" : "justify-start"}`}
            variant="default"
            title={isSidebarCollapsed ? "New workspace" : undefined}
            disabled={!user || (workspaces?.length || 0) >= (user?.workspace_limit || 3)}
          >
            <Folder className="h-4 w-4 shrink-0" />
            {!isSidebarCollapsed && <span>New Workspace</span>}

          </Button>

          <CreateChatDialog  workspaces={workspaces} isSidebarCollapsed={isSidebarCollapsed} onChatCreated={() => {
              fetchConversations();
              setIsMobileOpen(false);
            }}
          />
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto px-3">
          {!isSidebarCollapsed ? (
            <>
              {/* Home */}
              {/* <div className="space-y-1 py-2">
                <Button
                  variant="ghost"
                  className="w-full justify-start gap-3"
                  onClick={() => setIsMobileOpen(false)}
                >
                  <Home className="h-4 w-4 shrink-0" />
                  <span>Home</span>
                </Button>
              </div> */}

              {/* Workspaces Section */}
              <div className="mt-4 pb-4">
                <div className="mb-2 flex items-center justify-between px-3">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Workspaces
                  </h3>
                  <Badge variant="secondary" className="text-xs">
                    {workspaces.length}/{user?.workspace_limit || 3}
                  </Badge>
                </div>
                
                {isLoadingWorkspaces ? (
                  <div className="px-3 py-4 text-center text-sm text-muted-foreground">
                    Loading workspaces...
                  </div>
                ) : workspaces.length === 0 ? (
                  <div className="px-3 py-4 text-center text-sm text-muted-foreground">
                    No workspaces yet
                  </div>
                ) : (
                  <div className="space-y-1">
                    {workspaces?.map((workspace) => {
                      const workspaceConversations = getWorkspaceConversations(workspace.id);
                      const isExpanded = expandedWorkspaces.includes(workspace.id);
                      
                      return (
                        <div key={workspace.id}>
                          {/* Workspace Item */}
                          <div className="group relative">
                            <Button
                              variant="ghost"
                              className="h-auto w-full justify-between py-2 pr-8 text-left"
                              onClick={() => toggleWorkspace(workspace.id)}
                            >
                              <div className="flex items-center gap-2 overflow-hidden">
                                <span className="shrink-0 text-base">{workspace.icon}</span>
                                <span className="truncate text-sm font-medium">
                                  {workspace.name}
                                </span>
                              </div>
                              <div className="flex items-center gap-1 shrink-0">
                                <Badge variant="outline" className="text-xs h-5 px-1.5">
                                  {workspace.conversation_count}
                                </Badge>
                                {isExpanded ? (
                                  <ChevronUp className="h-3 w-3" />
                                ) : (
                                  <ChevronDown className="h-3 w-3" />
                                )}
                              </div>
                            </Button>

                            {/* Workspace Actions */}
                            <div className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-6 w-6"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    <MoreVertical className="h-3 w-3" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem>
                                    <Edit className="mr-2 h-4 w-4" />
                                    <span>Rename</span>
                                  </DropdownMenuItem>
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem
                                    onClick={() => setDeleteWorkspaceId(workspace.id)}
                                    className="text-destructive"
                                  >
                                    <Trash2 className="mr-2 h-4 w-4" />
                                    <span>Delete</span>
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </div>

                          {/* Conversations in Workspace */}
                          {isExpanded && (
                            <div className="ml-6 space-y-1 border-l border-border pl-2 mt-1">
                              {isLoadingConversations ? (
                                <div className="px-3 py-2 text-xs text-muted-foreground">
                                  Loading...
                                </div>
                              ) : workspaceConversations.length === 0 ? (
                                <div className="px-3 py-2 text-xs text-muted-foreground">
                                  No conversations yet
                                </div>
                              ) : (
                                workspaceConversations.map((conversation) => (
                                  <div key={conversation.id} className="group/conv relative">
                                    <Button
                                      variant="ghost"
                                      className={`w-full justify-start text-xs py-1.5 h-auto pr-8 ${
                                        currentConversationId === conversation.id
                                          ? "bg-primary/10"
                                          : ""
                                      }`}
                                      onClick={() => handleSelectConversation(conversation.id, workspace.id)}
                                    >
                                      <MessageSquare className="mr-2 h-3 w-3 shrink-0" />
                                      <span className="truncate">{conversation.title}</span>
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="icon"
                                      className="absolute right-1 top-1/2 -translate-y-1/2 h-5 w-5 opacity-0 group-hover/conv:opacity-100"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleDeleteConversation(conversation.id);
                                      }}
                                    >
                                      <Trash2 className="h-3 w-3 text-destructive" />
                                    </Button>
                                  </div>
                                ))
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Quick Chats Section */}
              <div className="mt-4 pb-4">
                <h3 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Quick Chats
                </h3>
                <div className="space-y-1">
                  {getQuickChats().length === 0 ? (
                    <div className="px-3 py-2 text-xs text-muted-foreground">
                      No quick chats yet
                    </div>
                  ) : (
                    getQuickChats().map((conversation) => (
                      <div key={conversation.id} className="group/conv relative">
                        <Button
                          variant="ghost"
                          className={`w-full justify-start text-xs py-1.5 h-auto pr-8 ${
                            currentConversationId === conversation.id
                              ? "bg-primary/10"
                              : ""
                          }`}
                          onClick={() => handleSelectConversation(conversation.id, null)}
                        >
                          <MessageSquare className="mr-2 h-3 w-3 shrink-0" />
                          <span className="truncate">{conversation.title}</span>
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="absolute right-1 top-1/2 -translate-y-1/2 h-5 w-5 opacity-0 group-hover/conv:opacity-100"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteConversation(conversation.id);
                          }}
                        >
                          <Trash2 className="h-3 w-3 text-destructive" />
                        </Button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </>
          ) : (
            // Collapsed sidebar - show icons only
            <div className="space-y-2 py-2">
              <Button
                variant="ghost"
                size="icon"
                className="mx-auto"
                title="Home"
                onClick={() => setIsMobileOpen(false)}
              >
                <Home className="h-4 w-4" />
              </Button>
              {workspaces.map((workspace) => (
                <Button
                  key={workspace.id}
                  variant="ghost"
                  size="icon"
                  className="mx-auto"
                  title={workspace.name}
                  onClick={() => setIsMobileOpen(false)}
                >
                  <span className="text-base">{workspace.icon}</span>
                </Button>
              ))}
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

      {/* Dialogs */}
      <CreateWorkspaceDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onSubmit={handleCreateWorkspace}
      />

      <DeleteWorkspaceDialog
        open={!!deleteWorkspaceId}
        onOpenChange={(open) => !open && setDeleteWorkspaceId(null)}
        workspaceName={workspaceToDelete?.name || ""}
        onConfirm={handleDeleteWorkspace}
      />
    </>
  );
}