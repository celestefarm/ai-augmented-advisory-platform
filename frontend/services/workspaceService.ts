import { AxiosError } from "axios";
import { toast } from "sonner";

import { GET, POST, DELETE, PATCH } from "./apiService";

export interface Workspace {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  is_pinned: boolean;
  conversation_count: number;
  artifact_count: number;
  last_activity: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateWorkspaceRequest {
  name: string;
  description?: string;
  icon?: string;
  color?: string;
}

export interface UpdateWorkspaceRequest {
  name?: string;
  description?: string;
  icon?: string;
  color?: string;
  is_pinned?: boolean;
  order?: number;
}

export interface WorkspaceResponse {
  message?: string;
  workspace?: Workspace;
}

// Paginated response type
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Get all workspaces
export const getWorkspaces = async (): Promise<Workspace[]> => {
  try {
    const { data } = await GET<PaginatedResponse<Workspace>>("/api/workspaces/");
    
    // Handle various response structures
    if (Array.isArray(data)) {
      // If API returns array directly (no pagination)
      return data;
    }
    
    if (data && typeof data === 'object' && 'results' in data) {
      // If API returns paginated response
      return data.results || [];
    }
    
    // Fallback to empty array
    return [];
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to fetch workspaces. Please try again.";

    // Don't show error toast for empty results
    if (axiosError?.response?.status !== 404) {
      toast.error("Failed to load workspaces", {
        description: errorMessage,
      });
    }

    // Return empty array instead of throwing
    return [];
  }
};

// Get single workspace
export const getWorkspace = async (id: string): Promise<Workspace> => {
  try {
    const { data } = await GET<Workspace>(`/api/workspaces/${id}/`);
    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to fetch workspace. Please try again.";

    toast.error("Failed to load workspace", {
      description: errorMessage,
    });

    throw error;
  }
};

// Create workspace
export const createWorkspace = async (
  request: CreateWorkspaceRequest
): Promise<Workspace> => {
  try {
    const { data } = await POST<Workspace, CreateWorkspaceRequest>(
      "/api/workspaces/",
      request
    );

    toast.success("Workspace created", {
      description: `${request.name} has been created successfully.`,
    });

    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string; errors?: unknown }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to create workspace. Please try again.";

    toast.error("Creation failed", {
      description: errorMessage,
    });

    throw error;
  }
};

// Update workspace
export const updateWorkspace = async (
  id: string,
  request: UpdateWorkspaceRequest
): Promise<Workspace> => {
  try {
    const { data } = await PATCH<Workspace, UpdateWorkspaceRequest>(
      `/api/workspaces/${id}/`,
      request
    );

    toast.success("Workspace updated", {
      description: "Your workspace has been updated successfully.",
    });

    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to update workspace. Please try again.";

    toast.error("Update failed", {
      description: errorMessage,
    });

    throw error;
  }
};

// Delete (archive) workspace
export const deleteWorkspace = async (id: string): Promise<void> => {
  try {
    await DELETE(`/api/workspaces/${id}/`);

    toast.success("Workspace deleted", {
      description: "Your workspace has been deleted successfully.",
    });
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to delete workspace. Please try again.";

    toast.error("Deletion failed", {
      description: errorMessage,
    });

    throw error;
  }
};

// Pin/unpin workspace
export const togglePinWorkspace = async (id: string): Promise<WorkspaceResponse> => {
  try {
    const { data } = await POST<WorkspaceResponse, {}>(
      `/api/workspaces/${id}/pin/`,
      {}
    );

    toast.success(data.message || "Workspace updated");

    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to update workspace. Please try again.";

    toast.error("Update failed", {
      description: errorMessage,
    });

    throw error;
  }
};