import { AxiosError } from "axios";
import { toast } from "sonner";

import { GET, POST, DELETE, PATCH } from "./apiService";

export interface Conversation {
  id: string;
  title: string;
  workspace?: string | null;  // Workspace ID
  is_pinned: boolean;
  message_count: number;
  last_message_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation: string;
  content: string;
  role: 'user' | 'assistant';
  agent_response?: string | null;  // Links to AgentResponse ID
  created_at: string;
}

export interface CreateConversationRequest {
  title: string;
  workspace_id?: string;  // Optional workspace
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Get all conversations
export const getConversations = async (): Promise<Conversation[]> => {
  try {
    const { data } = await GET<PaginatedResponse<Conversation>>("/api/conversations/");
    
    if (Array.isArray(data)) {
      return data;
    }
    
    if (data && typeof data === 'object' && 'results' in data) {
      return data.results || [];
    }
    
    return [];
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to fetch conversations. Please try again.";

    if (axiosError?.response?.status !== 404) {
      toast.error("Failed to load conversations", {
        description: errorMessage,
      });
    }

    return [];
  }
};

// Get conversations by workspace - FIXED
export const getWorkspaceConversations = async (workspaceId: string): Promise<Conversation[]> => {
  try {
    // Updated to match backend route: /api/workspaces/:id/conversations/
    const { data } = await GET<Conversation[]>(
      `/api/workspaces/${workspaceId}/conversations/`
    );
    
    // Backend returns array directly, not paginated for this endpoint
    if (Array.isArray(data)) {
      return data;
    }
    
    // Fallback if backend changes to paginated
    if (data && typeof data === 'object' && 'results' in data) {
      return (data as any).results || [];
    }
    
    return [];
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    
    // Don't show error toast for 404 (empty workspace)
    if (axiosError?.response?.status !== 404) {
      console.error('Failed to fetch workspace conversations:', error);
    }
    
    return [];
  }
};

// Get single conversation
export const getConversation = async (id: string): Promise<Conversation> => {
  try {
    const { data } = await GET<Conversation>(`/api/conversations/${id}/`);
    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to fetch conversation. Please try again.";

    toast.error("Failed to load conversation", {
      description: errorMessage,
    });

    throw error;
  }
};

// Get messages in a conversation
export const getConversationMessages = async (conversationId: string): Promise<Message[]> => {
  try {
    const { data } = await GET<PaginatedResponse<Message>>(
      `/api/messages/conversation/?conversation_id=${conversationId}`
    );
    
    if (Array.isArray(data)) {
      return data;
    }
    
    if (data && typeof data === 'object' && 'results' in data) {
      return data.results || [];
    }
    
    return [];
  } catch (error: unknown) {
    console.error('Failed to fetch messages:', error);
    return [];
  }
};

// Create conversation
export const createConversation = async (
  request: CreateConversationRequest
): Promise<Conversation> => {
  try {
    const { data } = await POST<Conversation, CreateConversationRequest>(
      "/api/conversations/",
      request
    );

    toast.success("Conversation created", {
      description: `${request.title} has been created successfully.`,
    });

    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string; errors?: unknown }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to create conversation. Please try again.";

    toast.error("Creation failed", {
      description: errorMessage,
    });

    throw error;
  }
};

// Delete conversation
export const deleteConversation = async (id: string): Promise<void> => {
  try {
    await DELETE(`/api/conversations/${id}/`);

    toast.success("Conversation deleted", {
      description: "Your conversation has been deleted successfully.",
    });
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to delete conversation. Please try again.";

    toast.error("Deletion failed", {
      description: errorMessage,
    });

    throw error;
  }
};

// Pin/unpin conversation
export const togglePinConversation = async (id: string): Promise<void> => {
  try {
    await POST(`/api/conversations/${id}/pin/`, {});
    toast.success("Conversation updated");
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to update conversation. Please try again.";

    toast.error("Update failed", {
      description: errorMessage,
    });

    throw error;
  }
};