import { create } from "zustand";
import { persist } from "zustand/middleware";
import { toast } from "sonner";

import { setLogoutHandler } from "@/services/apiService";
import {
  login as authServiceLogin,
  logout as authServiceLogout,
  register as authServiceRegister,
  updateProfile as updateProfileService,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  UpdateProfileRequest,
  User,
} from "@/services/authService";
import {
  getWorkspaces,
  createWorkspace as createWorkspaceService,
  deleteWorkspace as deleteWorkspaceService,
  CreateWorkspaceRequest,
  Workspace,
} from "@/services/workspaceService";
import {
  getConversations,
  getWorkspaceConversations,
  createConversation,
  deleteConversation as deleteConversationService,
  Conversation,
} from "@/services/conversationService";
import { SSEConnection, SSEMessage } from "@/services/sseService";

import { Message, Theme } from "@/types";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  register: (userData: RegisterRequest) => Promise<RegisterResponse>;
  login: (credentials: LoginRequest) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  updateProfile: (data: UpdateProfileRequest) => Promise<LoginResponse>;
}

interface UIState {
  isProcessing: boolean;
  setIsProcessing: (processing: boolean) => void;
}

interface MessageState {
  messages: Message[];
  currentConversationId: string | null;
  currentWorkspaceId: string | null;
  addMessage: (message: Message) => Promise<void>;
  handleSendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
  loadConversationMessages: (conversationId: string) => Promise<void>;
  setCurrentConversation: (conversationId: string | null) => void;
  setCurrentWorkspace: (workspaceId: string | null) => void;
}

interface WorkspaceState {
  workspaces: Workspace[];
  isLoadingWorkspaces: boolean;
  fetchWorkspaces: () => Promise<void>;
  createWorkspace: (data: CreateWorkspaceRequest) => Promise<Workspace>;
  deleteWorkspace: (id: string) => Promise<void>;
}

interface ConversationState {
  conversations: Conversation[];
  isLoadingConversations: boolean;
  fetchConversations: (workspaceId?: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
}

interface StoreState extends ThemeState, AuthState, UIState, MessageState, WorkspaceState, ConversationState {}

export const useStore = create(
  persist<StoreState, [], [], Partial<StoreState>>(
    (set, get) => ({
      /* ---------------- THEME STATE ---------------- */
      theme: "system",
      setTheme: (theme: Theme) => {
        set({ theme });
        const root = window.document.documentElement;
        root.classList.remove("light", "dark");

        if (theme === "system") {
          const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
            .matches
            ? "dark"
            : "light";
          root.classList.add(systemTheme);
        } else {
          root.classList.add(theme);
        }
      },
      toggleTheme: () => {
        const currentTheme = get().theme;
        const newTheme = currentTheme === "light" ? "dark" : "light";
        get().setTheme(newTheme);
      },

      /* ---------------- AUTH STATE ---------------- */
      isAuthenticated: false,
      user: null,
      
      register: async (userData: RegisterRequest) => {
        const response = await authServiceRegister(userData);
        return response;
      },
      
      login: async (credentials: LoginRequest) => {
        const response = await authServiceLogin(credentials);
        set({ 
          isAuthenticated: true,
          user: response.user 
        });
        return response;
      },
      
      logout: async () => {
        try {
          await authServiceLogout();
        } catch (error) {
          console.error('Logout API error:', error);
        } finally {
          const currentTheme = get().theme;
          
          set({
            theme: currentTheme,
            isAuthenticated: false,
            user: null,
            isProcessing: false,
            messages: [],
            workspaces: [],
            conversations: [],
            currentConversationId: null,
            currentWorkspaceId: null,
          });
          
          useStore.persist.clearStorage();
          window.location.reload();
        }
      },

      updateProfile: async (data: UpdateProfileRequest) => {
        try {
          const response = await updateProfileService(data);
          set({ user: response.user });
          return response;
        } catch (error) {
          throw error;
        }
      },

      /* ---------------- WORKSPACE STATE ---------------- */
      workspaces: [],
      isLoadingWorkspaces: false,

      fetchWorkspaces: async () => {
        set({ isLoadingWorkspaces: true });
        try {
          const workspaces = await getWorkspaces();
          set({ workspaces: Array.isArray(workspaces) ? workspaces : [] });
        } catch (error) {
          console.error('Failed to fetch workspaces:', error);
          set({ workspaces: [] });
        } finally {
          set({ isLoadingWorkspaces: false });
        }
      },

      createWorkspace: async (data: CreateWorkspaceRequest) => {
        try {
          const workspace = await createWorkspaceService(data);
          set(state => ({ 
            workspaces: [...(state.workspaces || []), workspace] 
          }));
          return workspace;
        } catch (error) {
          throw error;
        }
      },

      deleteWorkspace: async (id: string) => {
        try {
          await deleteWorkspaceService(id);
          set(state => ({ 
            workspaces: (state.workspaces || []).filter(w => w.id !== id),
            // Clear current workspace if it was deleted
            currentWorkspaceId: state.currentWorkspaceId === id ? null : state.currentWorkspaceId,
          }));
          // Refresh conversations
          await get().fetchConversations();
        } catch (error) {
          throw error;
        }
      },

      /* ---------------- CONVERSATION STATE ---------------- */
      conversations: [],
      isLoadingConversations: false,

      fetchConversations: async (workspaceId?: string) => {
        set({ isLoadingConversations: true });
        try {
          const conversations = workspaceId
            ? await getWorkspaceConversations(workspaceId)
            : await getConversations();
          
          // Sort by: 1) last_message_at (recent activity), 2) created_at (newest first)
          const sorted = Array.isArray(conversations) 
            ? conversations.sort((a, b) => {
                // Get last activity time (last_message_at or created_at as fallback)
                const activityA = a.last_message_at || a.created_at;
                const activityB = b.last_message_at || b.created_at;
                
                const dateA = new Date(activityA).getTime();
                const dateB = new Date(activityB).getTime();
                
                return dateB - dateA; // Descending order (newest/most recent first)
              })
            : [];
          
          set({ conversations: sorted });
        } catch (error) {
          console.error('Failed to fetch conversations:', error);
          set({ conversations: [] });
        } finally {
          set({ isLoadingConversations: false });
        }
      },

      deleteConversation: async (id: string) => {
        try {
          await deleteConversationService(id);
          set(state => ({
            conversations: (state.conversations || []).filter(c => c.id !== id),
            // Clear current conversation if it was deleted
            currentConversationId: state.currentConversationId === id ? null : state.currentConversationId,
            // Clear messages if current conversation was deleted
            messages: state.currentConversationId === id ? [] : state.messages,
          }));
        } catch (error) {
          throw error;
        }
      },

      /* ---------------- UI STATE ---------------- */
      isProcessing: false,
      setIsProcessing: isProcessing => set({ isProcessing }),

      /* ---------------- MESSAGE STATE ---------------- */
      messages: [],
      currentConversationId: null,
      currentWorkspaceId: null,

      setCurrentConversation: (conversationId: string | null) => {
        set({ currentConversationId: conversationId });
      },

      setCurrentWorkspace: (workspaceId: string | null) => {
        set({ currentWorkspaceId: workspaceId });
      },

      addMessage: async (message: Message) => {
        const messageWithId = {
          ...message,
          id: message.id || `msg-${Date.now()}-${Math.random()}`,
        };

        set(state => ({ messages: [...state.messages, messageWithId] }));
      },
      
      handleSendMessage: async (userMessage: string) => {
        const state = get();
        
        if (state.isProcessing) return;

        // Create or get conversation
        let conversationId = state.currentConversationId;
        let workspaceId = state.currentWorkspaceId;

        // If no conversation exists, create one (first message)
        if (!conversationId && state.messages.length === 0) {
          try {
            const title = userMessage.slice(0, 50) + (userMessage.length > 50 ? '...' : '');
            const newConversation = await createConversation({
              title,
              workspace_id: workspaceId || undefined,
            });
            conversationId = newConversation.id;
            set({ currentConversationId: conversationId });
            
            // Refresh conversations list
            await get().fetchConversations(workspaceId || undefined);
          } catch (error) {
            console.error('Failed to create conversation:', error);
          }
        }

        // Add user message immediately
        const userMessageObj: Message = {
          id: crypto.randomUUID(),
          sender: "user",
          content: userMessage,
          timestamp: new Date().toISOString(),
        };

        set({
          messages: [...state.messages, userMessageObj],
          isProcessing: true,  // ← Typing indicator shows NOW
        });

        // Prepare AI message ID but DON'T add to messages yet
        const aiMessageId = crypto.randomUUID();
        let aiContent = "";
        let assistantMessageAdded = false;  // ← NEW FLAG

        try {
          // Create SSE connection
          const sseConnection = new SSEConnection();

          // Handle incoming chunks
          sseConnection.onMessage((message: SSEMessage) => {
            const currentMessages = get().messages;

            if (message.type === 'start') {
              console.log('Stream started:', message.model);
              
              // Update conversation ID if returned
              if (message.conversation_id) {
                set({ currentConversationId: message.conversation_id });
              }
            } 
            else if (message.type === 'chunk') {
              // ← ADD ASSISTANT MESSAGE ON FIRST CHUNK
              if (!assistantMessageAdded) {
                const aiMessageObj: Message = {
                  id: aiMessageId,
                  sender: "assistant",
                  content: "",
                  timestamp: new Date().toISOString(),
                  isStreaming: true,
                };
                
                set({
                  messages: [...currentMessages, aiMessageObj],
                });
                
                assistantMessageAdded = true;
              }

              // Find the message index
              const messageIndex = currentMessages.findIndex(m => m.id === aiMessageId);
              if (messageIndex === -1) return;

              // Append chunk to AI message
              aiContent += message.content || '';
              
              const updatedMessages = [...get().messages];
              const aiMessageIndex = updatedMessages.findIndex(m => m.id === aiMessageId);
              
              if (aiMessageIndex !== -1) {
                updatedMessages[aiMessageIndex] = {
                  ...updatedMessages[aiMessageIndex],
                  content: aiContent,
                  isStreaming: true,
                };

                set({ messages: updatedMessages });
              }
            } 
            else if (message.type === 'complete') {
              // Mark streaming complete
              const updatedMessages = [...get().messages];
              const messageIndex = updatedMessages.findIndex(m => m.id === aiMessageId);

              if (messageIndex !== -1) {
                updatedMessages[messageIndex] = {
                  ...updatedMessages[messageIndex],
                  content: aiContent,
                  isStreaming: false,
                  metadata: message.metadata,
                  confidence: message.confidence,
                  responseId: message.response_id,
                };

                set({ 
                  messages: updatedMessages,
                  isProcessing: false,
                });
              }

              console.log('Stream completed:', message.metadata);

              // Refresh conversations to update message count
              get().fetchConversations(workspaceId || undefined);
            }
          });

          // Handle errors
          sseConnection.onError((error: Error) => {
            console.error('SSE Error:', error);
            
            // If assistant message was added, update it with error
            if (assistantMessageAdded) {
              const currentMessages = get().messages;
              const messageIndex = currentMessages.findIndex(m => m.id === aiMessageId);

              if (messageIndex !== -1) {
                const updatedMessages = [...currentMessages];
                updatedMessages[messageIndex] = {
                  ...updatedMessages[messageIndex],
                  content: "Sorry, I encountered an error processing your request. Please try again.",
                  isStreaming: false,
                  error: true,
                };

                set({ 
                  messages: updatedMessages,
                  isProcessing: false,
                });
              }
            } else {
              // No assistant message yet, just clear processing
              set({ isProcessing: false });
            }

            toast.error("Failed to get response", {
              description: error.message,
            });
          });

          // Handle completion
          sseConnection.onComplete(() => {
            set({ isProcessing: false });
          });

          // Start connection
          await sseConnection.connect(
            userMessage,
            conversationId || undefined,
            workspaceId || undefined
          );

        } catch (error) {
          console.error('Failed to send message:', error);
          
          // Remove failed AI message if it was added
          if (assistantMessageAdded) {
            set({
              messages: get().messages.filter(m => m.id !== aiMessageId),
              isProcessing: false,
            });
          } else {
            set({ isProcessing: false });
          }

          toast.error("Failed to send message", {
            description: error instanceof Error ? error.message : "Unknown error",
          });
        }
      },
      
      clearChat: () => {
        set({ 
          messages: [],
          currentConversationId: null,
        });
      },
      
      loadConversationMessages: async (conversationId: string) => {
        try {
          // Import here to avoid circular dependency
          const { getConversationMessages } = await import('@/services/conversationService');
          
          const messages = await getConversationMessages(conversationId);
          
          // Convert backend messages to frontend format
          const formattedMessages = messages.map(msg => ({
            id: msg.id,
            sender: msg.role === 'user' ? 'user' : 'assistant',
            content: msg.content,
            timestamp: msg.created_at,
          }));
          
          set({ 
            messages: formattedMessages,
            currentConversationId: conversationId,
          });
        } catch (error) {
          console.error('Failed to load conversation messages:', error);
          toast.error('Failed to load conversation');
        }
      },
    }),
    {
      name: "app-store",
      partialize: (state: StoreState): Partial<StoreState> => ({
        theme: state.theme,
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        workspaces: state.workspaces,
        currentWorkspaceId: state.currentWorkspaceId,
        // Don't persist messages or conversations
      }),
    },
  ),
);

// Set logout handler for automatic logout on 401
setLogoutHandler(async () => {
  await useStore.getState().logout();
});