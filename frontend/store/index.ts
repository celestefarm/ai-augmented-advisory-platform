import { create } from "zustand";
import { persist } from "zustand/middleware";

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
import { sendMessage } from "@/services/chatService";

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
  addMessage: (message: Message) => Promise<void>;
  handleSendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
}

interface StoreState extends ThemeState, AuthState, UIState, MessageState {}

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
        // Don't auto-login - user must verify email first
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
          // Continue with logout even if API call fails
          console.error('Logout API error:', error);
        } finally {
          const currentTheme = get().theme;
          
          set({
            theme: currentTheme,
            isAuthenticated: false,
            user: null,
            isProcessing: false,
            messages: [],
          });
          
          useStore.persist.clearStorage();
          window.location.reload();
        }
      },

      updateProfile: async (data: UpdateProfileRequest) => {
        try {
          const response = await updateProfileService(data);
          
          // Update user in store
          set({ user: response.user });
          
          return response;
        } catch (error) {
          throw error;
        }
      },

      /* ---------------- UI STATE ---------------- */
      isProcessing: false,
      setIsProcessing: isProcessing => set({ isProcessing }),

      /* ---------------- MESSAGE STATE ---------------- */
      messages: [],
      addMessage: async (message: Message) => {
        const messageWithId = {
          ...message,
          id: message.id || `msg-${Date.now()}-${Math.random()}`,
        };

        if (message.sender === "bot" && message.content) {
          const streamingMessage: Message = {
            ...messageWithId,
            content: "",
            isStreaming: true,
          };
          set(state => ({ messages: [...state.messages, streamingMessage] }));

          try {
            const words = message.content.split(" ");
            for (let i = 0; i < words?.length; i++) {
              const chunk = (i === 0 ? "" : " ") + words[i];
              set(state => ({
                messages: state?.messages?.map(msg =>
                  msg.id === messageWithId.id && msg.isStreaming
                    ? { ...msg, content: msg.content + chunk }
                    : msg,
                ),
              }));
              if (i < words?.length - 1)
                await new Promise(resolve => setTimeout(resolve, 75));
            }
            set(state => ({
              messages: state?.messages?.map(msg =>
                msg.id === messageWithId.id
                  ? { ...msg, isStreaming: false }
                  : msg,
              ),
            }));
          } catch {
            set(state => ({
              messages: state?.messages?.map(msg =>
                msg.id === messageWithId.id
                  ? {
                      ...msg,
                      content: "An error occurred while streaming this message.",
                      isStreaming: false,
                    }
                  : msg,
              ),
            }));
          }
        } else {
          set(state => ({ messages: [...state.messages, messageWithId] }));
        }
      },
      
      handleSendMessage: async message => {
        get().addMessage({ sender: "user", content: message });
        set({ isProcessing: true });

        try {
          const response = await sendMessage({ user_message: message });
          get().addMessage({
            sender: "bot",
            content: response.data?.ai_response || response.message,
          });
        } catch (error) {
          const errMsg = error instanceof Error ? error.message : "Unknown error occurred";
          get().addMessage({
            sender: "bot",
            content: `I encountered an error: ${errMsg}. Please try again.`,
          });
        } finally {
          set({ isProcessing: false });
        }
      },
      
      clearChat: () => {
        set({ messages: [] });
      },
    }),
    {
      name: "app-store",
      partialize: (state: StoreState): Partial<StoreState> => ({
        theme: state.theme,
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        isProcessing: state.isProcessing,
        messages: state.messages,
      }),
    },
  ),
);

setLogoutHandler(async () => {
  await useStore.getState().logout();
});