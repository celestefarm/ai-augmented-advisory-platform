import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from "axios";

// Detect if we're on the server or client
const isServer = typeof window === "undefined";

// API base URL
const baseURL = isServer
  ? process.env.API_URL || "http://localhost:8000" // server → Django directly
  : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; // client → Next.js proxy (removed trailing slash)

// Global API timeout (2 mins)
const timeout = 1000 * 60 * 2;

// API endpoints
export const endpoints = {
  auth: {
    register: "/api/auth/register/",
    login: "/api/auth/login/",
    logout: "/api/auth/logout/",
    verifyEmail: "/api/auth/verify-email/",
    resendVerification: "/api/auth/resend-verification/",
    refresh: "/api/auth/token/refresh/",
    profile: "/api/auth/profile/",
  },
  workspaces: {
    list: "/api/workspaces/",
    detail: (id: string) => `/api/workspaces/${id}/`,
    pin: (id: string) => `/api/workspaces/${id}/pin/`,
  },
  assistant: {
    chat: "/assistant/chat",
  },
};

// Helper to build full URLs (only needed for server-side direct calls)
export function getApiUrl(endpoint: string) {
  return `${baseURL}${endpoint}`;
}

// Create Axios instance with credentials to include cookies
export const apiService = axios.create({
  baseURL,
  timeout,
  withCredentials: true,
});

// Import logout function - will be set by store
let logoutUser: (() => Promise<void>) | null = null;

// Function to set the logout handler (called by store)
export const setLogoutHandler = (handler: () => Promise<void>) => {
  logoutUser = handler;
};

// Request interceptor to add JWT token
apiService.interceptors.request.use(
  (config) => {
    // Get token from localStorage (you'll set this after login)
    const token = !isServer ? localStorage.getItem('access_token') : null;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Token refresh logic
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token!);
    }
  });
  
  failedQueue = [];
};

apiService.interceptors.response.use(
  response => response,
  async (error: AxiosError) => {
    const originalRequest: any = error.config;

    // If 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue failed requests
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiService(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = !isServer ? localStorage.getItem('refresh_token') : null;

      if (!refreshToken) {
        // No refresh token, logout
        if (logoutUser) await logoutUser();
        return Promise.reject(error);
      }

      try {
        // Call Django refresh endpoint with trailing slash
        const { data } = await axios.post(
          `${baseURL}/api/auth/token/refresh/`,
          { refresh: refreshToken }
        );
        
        const newAccessToken = data.access;
        
        if (!isServer) {
          localStorage.setItem('access_token', newAccessToken);
        }
        
        apiService.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        
        processQueue(null, newAccessToken);
        
        return apiService(originalRequest);
      } catch (err) {
        processQueue(err, null);
        if (logoutUser) await logoutUser();
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// Generic Helpers

export const GET = <Response>(url: string, config?: AxiosRequestConfig) =>
  apiService.get<Response>(url, config);

export const POST = <Response, Request>(
  url: string,
  body: Request,
  config?: AxiosRequestConfig<Request>,
) =>
  apiService.post<Response, AxiosResponse<Response>, Request>(
    url,
    body,
    config,
  );

export const PUT = <Response, Request>(
  url: string,
  body: Request,
  config?: AxiosRequestConfig<Request>,
) =>
  apiService.put<Response, AxiosResponse<Response>, Request>(url, body, config);

export const PATCH = <Response, Request>(
  url: string,
  body: Request,
  config?: AxiosRequestConfig<Request>,
) =>
  apiService.patch<Response, AxiosResponse<Response>, Request>(
    url,
    body,
    config,
  );

export const DELETE = <Response>(url: string, config?: AxiosRequestConfig) =>
  apiService.delete<Response>(url, config);