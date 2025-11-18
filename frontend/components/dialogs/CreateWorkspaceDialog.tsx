"use client";

import { useState } from "react";
import { Loader2, Plus } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { createConversation } from "@/services/conversationService"; // Changed
import { Workspace } from "@/services/workspaceService"; // Added

interface CreateWorkspaceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: { name: string; description: string; icon: string }) => Promise<void>;
}

const DEFAULT_ICONS = ["📁", "📊", "🎯", "💼", "🚀", "💡", "📈", "🎨", "⚙️", "🔬"];

export function CreateWorkspaceDialog({
  open,
  onOpenChange,
  onSubmit,
}: CreateWorkspaceDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [selectedIcon, setSelectedIcon] = useState("📁");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) return;

    setIsLoading(true);
    try {
      await onSubmit({
        name: name.trim(),
        description: description.trim(),
        icon: selectedIcon,
      });
      
      // Reset form
      setName("");
      setDescription("");
      setSelectedIcon("📁");
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to create workspace:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create Workspace</DialogTitle>
            <DialogDescription>
              Create a new workspace to organize your conversations and files.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Icon Selector */}
            <div className="space-y-2">
              <Label>Icon</Label>
              <div className="flex flex-wrap gap-2">
                {DEFAULT_ICONS.map((icon) => (
                  <button
                    key={icon}
                    type="button"
                    onClick={() => setSelectedIcon(icon)}
                    className={`flex h-10 w-10 items-center justify-center rounded-lg border-2 text-xl transition-colors ${
                      selectedIcon === icon
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-primary/50"
                    }`}
                  >
                    {icon}
                  </button>
                ))}
              </div>
            </div>

            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="name">
                Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Q4 Product Launch"
                required
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What is this workspace for?"
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={!name.trim() || isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create Workspace"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

interface CreateChatDialogProps {
  workspaceId?: string | null;
  workspaces: Workspace[];
  isSidebarCollapsed?: boolean;
  onChatCreated?: () => void;
}

export function CreateChatDialog({ 
  workspaceId: initialWorkspaceId, 
  workspaces,
  isSidebarCollapsed = false,
  onChatCreated 
}: CreateChatDialogProps) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string>(initialWorkspaceId || "");
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    setLoading(true);
    try {
      await createConversation({
        title: title.trim() || "New Chat",
        workspace_id: selectedWorkspaceId || undefined,
      });
      setTitle("");
      setSelectedWorkspaceId("");
      setOpen(false);
      onChatCreated?.();
    } catch (error) {
      console.error('Failed to create chat:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          className={`w-full gap-2 ${isSidebarCollapsed ? "justify-center px-0" : "justify-start"}`}
          title={isSidebarCollapsed ? "New chat" : undefined}
        >
          <Plus className="h-4 w-4 shrink-0" />
          {!isSidebarCollapsed && <span>New Chat</span>}
        </Button>
      </DialogTrigger>
            <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Chat</DialogTitle>
          <DialogDescription>
            Start a new conversation
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="chat-title">Title (Optional)</Label>
            <Input
              id="chat-title"
              placeholder="Chat title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="workspace-select">Workspace (Optional)</Label>
            <select
              id="workspace-select"
              value={selectedWorkspaceId}
              onChange={(e) => setSelectedWorkspaceId(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">Quick Chat (No Workspace)</option>
              {workspaces.map((workspace) => (
                <option key={workspace.id} value={workspace.id}>
                  {workspace.icon} {workspace.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={loading}>
              {loading ? "Creating..." : "Create Chat"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}