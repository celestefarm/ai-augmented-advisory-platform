import { AxiosError } from "axios";
import { toast } from "sonner";

import { GET } from "./apiService";
import { getApiUrl } from "./apiService";

export interface AgentResponse {
  id: string;
  question: string;
  response: string;
  confidence_level: 'high' | 'medium' | 'low' | 'speculative';
  confidence_percentage: number;
  classification?: {
    type: string;
    domains: string[];
    urgency: string;
    complexity: string;
    confidence: number;
  };
  emotional_state?: {
    state: string;
    confidence: number;
  };
  model?: {
    name: string;
    estimated_cost: number;
  };
  quality?: {
    passed: boolean;
    checks: Record<string, boolean>;
  };
  metadata: {
    response_time: number;
    total_tokens: number;
    cost: number;
    model: string;
  };
  created_at: string;
}

export interface AgentAnalytics {
  total_responses: number;
  total_cost: number;
  total_tokens: number;
  average_response_time: number;
  confidence_distribution: {
    high: number;
    medium: number;
    low: number;
  };
  question_types: Record<string, number>;
}

// SSE event types
export type SSEEventType = 'status' | 'start' | 'chunk' | 'complete' | 'error';

export interface SSEEvent {
  type: SSEEventType;
  stage?: number;
  message?: string;
  content?: string;
  chunk_number?: number;
  response_id?: string;
  workspace_id?: string;
  conversation_id?: string;
  model?: string;
  confidence?: {
    level: string;
    percentage: number;
    explanation: string;
  };
  quality?: {
    passed: boolean;
    checks: Record<string, boolean>;
    failures?: string[];
  };
  metadata?: {
    response_time: number;
    total_tokens: number;
    cost: number;
    model: string;
    chunks_sent: number;
  };
  error?: string;
  error_type?: string;
  timestamp: string;
}

// Ask agent with streaming SSE
export const askAgent = async (
  question: string,
  conversationId?: string,
  workspaceId?: string,
  onEvent?: (event: SSEEvent) => void
): Promise<void> => {
  const isServer = typeof window === 'undefined';
  const token = !isServer ? localStorage.getItem('access_token') : null;
  
  if (!token) {
    toast.error("Authentication required");
    throw new Error("No access token");
  }

  try {
    const url = getApiUrl('/api/agents/ask');
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        question,
        conversation_id: conversationId,
        workspace_id: workspaceId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6); // Remove 'data: ' prefix
            const event = JSON.parse(jsonStr) as SSEEvent;
            
            if (onEvent) {
              onEvent(event);
            }
            
            // Handle errors
            if (event.type === 'error') {
              toast.error('AI Error', {
                description: event.error || 'An error occurred',
              });
            }
          } catch (e) {
            console.error('Failed to parse SSE event:', e);
          }
        }
      }
    }
  } catch (error: unknown) {
    console.error('Agent request failed:', error);
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to get AI response. Please try again.";

    toast.error("AI request failed", {
      description: errorMessage,
    });

    throw error;
  }
};

// Get agent response history
export const getAgentResponses = async (
  limit = 20,
  offset = 0
): Promise<{ results: AgentResponse[]; total: number; has_more: boolean }> => {
  try {
    const { data } = await GET<{
      results: AgentResponse[];
      total: number;
      has_more: boolean;
    }>(`/api/agents/responses?limit=${limit}&offset=${offset}`);

    return data;
  } catch (error: unknown) {
    console.error('Failed to fetch agent responses:', error);
    return { results: [], total: 0, has_more: false };
  }
};

// Get single agent response
export const getAgentResponse = async (responseId: string): Promise<AgentResponse> => {
  try {
    const { data } = await GET<AgentResponse>(`/api/agents/responses/${responseId}`);
    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to fetch response. Please try again.";

    toast.error("Failed to load response", {
      description: errorMessage,
    });

    throw error;
  }
};

// Get analytics
export const getAgentAnalytics = async (): Promise<AgentAnalytics> => {
  try {
    const { data } = await GET<AgentAnalytics>('/api/agents/analytics');
    return data;
  } catch (error: unknown) {
    console.error('Failed to fetch analytics:', error);
    return {
      total_responses: 0,
      total_cost: 0,
      total_tokens: 0,
      average_response_time: 0,
      confidence_distribution: { high: 0, medium: 0, low: 0 },
      question_types: {},
    };
  }
};