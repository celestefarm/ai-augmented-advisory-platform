// services/sseService.ts
import { getApiUrl } from "./apiService";

export interface SSEMessage {
  type: 'start' | 'chunk' | 'complete' | 'error';
  content?: string;
  model?: string;
  response_id?: string;
  workspace_id?: string;
  conversation_id?: string;
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
  timestamp?: string;
}

export class SSEConnection {
  private eventSource: EventSource | null = null;
  private onMessageCallback: ((message: SSEMessage) => void) | null = null;
  private onErrorCallback: ((error: Error) => void) | null = null;
  private onCompleteCallback: (() => void) | null = null;

  /**
   * Start SSE connection to Django backend
   */
  async connect(
    question: string,
    conversationId?: string,
    workspaceId?: string
  ): Promise<void> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }

    // Build query params
    const params = new URLSearchParams();
    if (conversationId) params.append('conversation_id', conversationId);
    if (workspaceId) params.append('workspace_id', workspaceId);

    // Django expects POST body as JSON, but EventSource only supports GET
    // We'll use fetch with ReadableStream instead
    return this.connectWithFetch(question, conversationId, workspaceId, token);
  }

  /**
   * Use fetch API with ReadableStream for SSE (supports POST)
   */
  private async connectWithFetch(
    question: string,
    conversationId: string | undefined,
    workspaceId: string | undefined,
    token: string
  ): Promise<void> {
    try {
      const response = await fetch(getApiUrl('/api/agents/ask'), {
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
        throw new Error('Response body is not readable');
      }

      // Read stream
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          this.onCompleteCallback?.();
          break;
        }

        // Decode chunk
        const chunk = decoder.decode(value, { stream: true });
        
        // Parse SSE format: "data: {...}\n\n"
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6); // Remove "data: " prefix
              const message: SSEMessage = JSON.parse(jsonStr);
              
              // Handle message
              this.onMessageCallback?.(message);
              
              // Auto-complete on error
              if (message.type === 'error') {
                this.onErrorCallback?.(new Error(message.error || 'Unknown error'));
                this.close();
                break;
              }
              
              // Auto-complete on complete
              if (message.type === 'complete') {
                this.onCompleteCallback?.();
                this.close();
                break;
              }
            } catch (parseError) {
              console.error('Failed to parse SSE message:', parseError);
            }
          }
        }
      }
    } catch (error) {
      this.onErrorCallback?.(error as Error);
      throw error;
    }
  }

  /**
   * Set callback for incoming messages
   */
  onMessage(callback: (message: SSEMessage) => void): void {
    this.onMessageCallback = callback;
  }

  /**
   * Set callback for errors
   */
  onError(callback: (error: Error) => void): void {
    this.onErrorCallback = callback;
  }

  /**
   * Set callback for connection complete
   */
  onComplete(callback: () => void): void {
    this.onCompleteCallback = callback;
  }

  /**
   * Close connection
   */
  close(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}