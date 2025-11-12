export const PUBLIC_ROUTES = {
  home: "/",
  about: "/about",
  agents: "/agents",
  pricing: "/pricing",
  login: "/auth/login",
  register: "/auth/register",
  verifyEmail: "/auth/verify-email",
  checkEmail: "/auth/check-email",    
  forgotPassword: "/auth/forgot-password",
  privacyPolicy: "/privacy-policy",
  termsOfService: "/terms-of-service",
} as const;

export const PROTECTED_ROUTES = {
  dashboard: "/dashboard",
  settings: "/settings",
} as const;

export const ROUTES = {
  ...PUBLIC_ROUTES,
  ...PROTECTED_ROUTES,
} as const;

export const PUBLIC_ROUTES_PATHS: string[] = Object.values(PUBLIC_ROUTES);
export const PROTECTED_ROUTES_PATHS: string[] = Object.values(PROTECTED_ROUTES);
