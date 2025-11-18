import { endpoints, POST } from "./apiService";

export interface SendMessageRequest {
  user_message: string;
}

export interface SendMessageResponse {
  success: boolean;
  message: string;
  data: {
    ai_response: string;
  };
}

export const sendMessage = async (
  request: SendMessageRequest,
): Promise<SendMessageResponse> => {
  const { data } = await POST<SendMessageResponse, SendMessageRequest>(
    endpoints.assistant.chat,
    request,
  );
  return data;
};

export const createChat = async (
  workspaceId: string,
  title: string,
): Promise<{ id: string; title: string }> => {
  const { data } = await POST(
    `/api/conversations/`,
    { workspace_id: workspaceId, title }
  );
  return data;
};
