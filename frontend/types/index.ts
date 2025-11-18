export type Theme = "light" | "dark" | "system";

export interface Message {
  id?: string;
  sender: "user" | "ai";
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  error?: boolean;
  metadata?: {
    response_time: number;
    total_tokens: number;
    cost: number;
    model: string;
    chunks_sent: number;
  };
  confidence?: {
    level: string;
    percentage: number;
    explanation: string;
  };
  responseId?: string;
}