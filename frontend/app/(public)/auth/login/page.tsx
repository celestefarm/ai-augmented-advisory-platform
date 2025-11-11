"use client";

import { useState } from "react";

import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Eye, EyeOff, Lock, Mail } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import axios, { AxiosError } from "axios";

import { useStore } from "@/store";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";

import { LoginRequest } from "@/services/authService";

import { ROUTES } from "@/routes";

// Zod schema for login validation
const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function Login() {
  const router = useRouter();

  const { login } = useStore();

  const [showPassword, setShowPassword] = useState(false);
  const [showResendVerification, setShowResendVerification] = useState(false);
  const [resendingEmail, setResendingEmail] = useState(false);

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
    mode: "onChange",
  });

  // Handle resend verification email
  const handleResendVerification = async () => {
    const email = form.getValues('email');
    if (!email) {
      toast.error('Please enter your email address');
      return;
    }
    
    setResendingEmail(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/resend-verification/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast.success('Email sent!', {
          description: 'Please check your inbox for the verification link.',
        });
        setShowResendVerification(false);
      } else {
        toast.error('Failed to send email', {
          description: data.message || 'Please try again later.',
        });
      }
    } catch (error) {
      toast.error('Failed to resend email', {
        description: 'An error occurred. Please try again.',
      });
    } finally {
      setResendingEmail(false);
    }
  };

  // Handle login submission
  async function handleLogin(values: LoginFormData) {
    try {
      const loginData: LoginRequest = {
        email: values.email,
        password: values.password,
      };
      
      const response = await login(loginData);
      
      if (response.access_token) {
        router.push(ROUTES.dashboard);
      }
    } catch (error: unknown) {
      const axiosError = error as AxiosError<{ 
        message: string; 
        email_verified?: boolean; 
      }>;
      
      // Check if it's unverified email error
      if (axiosError?.response?.status === 403 && 
          axiosError?.response?.data?.email_verified === false) {
        setShowResendVerification(true);
      }
    }
  }

  return (
    <Card className="mx-auto w-full max-w-md p-5">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="space-y-5"
      >
        {/* Heading */}
        <div className="space-y-2.5 text-center">
          <h3>Welcome back</h3>
          <p className="text-small text-muted-foreground">
            Log in to your account to continue.
          </p>
        </div>

        {/* ShadCN Form */}
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleLogin)} className="space-y-5">
            {/* Email Field */}
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <div className="relative">
                    <Mail className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="Enter your email address"
                        className="pl-9"
                        {...field}
                      />
                    </FormControl>
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Password Field */}
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center justify-between">
                    <FormLabel>Password</FormLabel>
                    <Link
                      href={ROUTES.forgotPassword}
                      className="text-small underline-offset-4 hover:underline"
                    >
                      Forgot password?
                    </Link>
                  </div>
                  <div className="relative">
                    <Lock className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <FormControl>
                      <Input
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        className="pr-9 pl-9"
                        {...field}
                      />
                    </FormControl>
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute top-1/2 right-3 -translate-y-1/2 text-muted-foreground hover:cursor-pointer"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Resend Verification Notice */}
            {showResendVerification && (
              <div className="rounded-md bg-yellow-50 p-4 dark:bg-yellow-900/20">
                <div className="flex">
                  <div className="ml-3 flex-1">
                    <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                      Email not verified
                    </h3>
                    <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                      <p>Please verify your email before logging in.</p>
                    </div>
                    <div className="mt-4">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={handleResendVerification}
                        disabled={resendingEmail}
                      >
                        {resendingEmail ? (
                          <>
                            <Spinner className="mr-2" />
                            Sending...
                          </>
                        ) : (
                          'Resend Verification Email'
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={!form.formState.isValid || form.formState.isSubmitting}
              className="w-full"
            >
              {form.formState.isSubmitting ? (
                <>
                  <Spinner />
                  Logging In...
                </>
              ) : (
                "Log In"
              )}
            </Button>
          </form>
        </Form>

        {/* Footer Link */}
        <div className="text-small flex items-center justify-center gap-1">
          <p className="text-muted-foreground">Don&apos;t have an account?</p>
          <Link
            href={ROUTES.register}
            className="font-medium underline-offset-4 hover:underline"
          >
            Register
          </Link>
        </div>
      </motion.div>
    </Card>
  );
}