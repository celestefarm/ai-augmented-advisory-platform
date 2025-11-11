import { AxiosError } from "axios";
import { toast } from "sonner";

import { endpoints, POST } from "./apiService";

// Detect if we’re on the server or client
const isServer = typeof window === "undefined";

/*
 * Auth Service provides methods for user authentication.
 * It uses the POST method from apiService to interact with the backend.
 */

/* ----------------------------------------
   Register Service
----------------------------------------- */
export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
  company?: string;
  role?: string;
}

export interface RegisterResponse {
  email: string;
  message: string;
}

export const register = async (
  request: RegisterRequest,
): Promise<RegisterResponse> => {
  try {
    const { data } = await POST<RegisterResponse, RegisterRequest>(
      endpoints.auth.register,
      request,
    );
    
    toast.success("Registration successful", {
      description: data.message,
    });
    
    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string; errors?: unknown }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Registration failed. Please try again.";
    
    toast.error("Registration failed", {
      description: errorMessage,
    });
    
    throw error;
  }
};

/* ----------------------------------------
   Login Service
----------------------------------------- */
export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  company: string;
  role: string;
  subscription_tier: string;
  workspace_limit: number;
}

export interface LoginResponse {
  message: string;
  user: User;
  access_token: string;
  refresh_token: string;
}

export const login = async (request: LoginRequest): Promise<LoginResponse> => {
  try {
    const { data } = await POST<LoginResponse, LoginRequest>(
      endpoints.auth.login,
      request,
    );
    // Store tokens in localStorage
    if (!isServer) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // SET COOKIE for middleware
      document.cookie = `auth-token=${data.access_token}; path=/; max-age=${60 * 60 * 24}; SameSite=Strict`;
    }
    
    toast.success("Login successful", {
      description: "Welcome back!",
    });
    
    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Login failed. Please try again.";
    
    toast.error("Login failed", {
      description: errorMessage,
    });
    
    throw error; // Re-throw to handle in component
  }
};

/* ----------------------------------------
   Logout Service
----------------------------------------- */
export interface LogoutResponse {
  message: string;
}

export const logout = async (): Promise<LogoutResponse> => {
  const refreshToken = !isServer ? localStorage.getItem('refresh_token') : null;
  
  try {
    const { data } = await POST<LogoutResponse, { refresh_token: string }>(
      endpoints.auth.logout,
      { refresh_token: refreshToken! },  // Backend expects this
    );
    
    if (!isServer) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');

      // Clear auth-token cookie
      // document.cookie = `auth-token=; path=/; max-age=0; SameSite=Strict`;
    }
    
    return data;
  } catch (error) {
    if (!isServer) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
    throw error;
  }
};
