import { AxiosError } from "axios";
import { toast } from "sonner";

import { endpoints, POST, PATCH } from "./apiService";

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
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
  industry?: string;
  region?: string;
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
    const axiosError = error as AxiosError<{ 
      message: string; 
      email_verified?: boolean; 
    }>;
    
    // Handle unverified email specifically
    if (axiosError?.response?.status === 403 && 
        axiosError?.response?.data?.email_verified === false) {
      toast.error("Email not verified", {
        description: "Please check your email and click the verification link.",
      });
      throw error;
    }
    
    // Handle other errors
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Login failed. Please try again.";
    
    toast.error("Login failed", {
      description: errorMessage,
    });
    
    throw error;
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
    // If no refresh token, just clear local storage
    if (!refreshToken) {
      if (!isServer) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      }
      return { message: 'Logged out successfully' };
    }

    const { data } = await POST<LogoutResponse, { refresh_token: string }>(
      endpoints.auth.logout,
      { refresh_token: refreshToken },
    );
    
    if (!isServer) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
    
    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string }>;
    
    // If 401, token is already invalid - just clear local storage
    if (axiosError?.response?.status === 401) {
      if (!isServer) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      }
      return { message: 'Logged out successfully' };
    }
    
    // For any other error, still clear storage
    if (!isServer) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
    
    throw error;
  }
};


/* ----------------------------------------
   Update profile Service
----------------------------------------- */
export interface UpdateProfileRequest {
  first_name?: string;
  last_name?: string;
  industry?: string;
  region?: string;
  role?: string;
}

export const updateProfile = async (
  request: UpdateProfileRequest
): Promise<LoginResponse> => {
  try {
    const { data } = await PATCH<LoginResponse, UpdateProfileRequest>(
      endpoints.auth.profile, // Make sure this endpoint exists
      request
    );

    // Update user in localStorage
    if (!isServer) {
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        const user = JSON.parse(storedUser);
        const updatedUser = { ...user, ...data.user };
        localStorage.setItem("user", JSON.stringify(updatedUser));
      }
    }

    toast.success("Profile updated", {
      description: "Your profile has been updated successfully.",
    });

    return data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError<{ message: string; errors?: unknown }>;
    const errorMessage =
      axiosError?.response?.data?.message ||
      "Failed to update profile. Please try again.";

    toast.error("Update failed", {
      description: errorMessage,
    });

    throw error;
  }
};