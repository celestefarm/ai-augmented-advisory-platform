"use client";

import { Suspense, useEffect, useState } from "react";

import { motion } from "framer-motion";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import { ROUTES } from "@/routes";

type VerificationState = "verifying" | "success" | "error";

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [state, setState] = useState<VerificationState>("verifying");
  const [message, setMessage] = useState("Verifying your email...");

  useEffect(() => {
    if (!token) {
      setState("error");
      setMessage("No verification token provided.");
      return;
    }

    const verifyEmail = async (verificationToken: string) => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/verify-email/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ token: verificationToken }),
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          localStorage.setItem("user", JSON.stringify(data.user));

          setState("success");
          setMessage("Email verified successfully! Redirecting to dashboard...");

          setTimeout(() => {
            router.push(ROUTES.dashboard);
          }, 2000);
        } else {
          setState("error");
          setMessage(data.message || "Email verification failed.");
        }
      } catch {
        setState("error");
        setMessage("An error occurred during verification. Please try again.");
      }
    };

    verifyEmail(token);
  }, [token, router]);

  return (
    <Card className="mx-auto w-full max-w-md p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="space-y-6 text-center"
      >
        <div className="flex justify-center">
          {state === "verifying" && (
            <Loader2 className="h-16 w-16 animate-spin text-primary" />
          )}
          {state === "success" && (
            <CheckCircle2 className="h-16 w-16 text-green-500" />
          )}
          {state === "error" && (
            <XCircle className="h-16 w-16 text-destructive" />
          )}
        </div>

        <div className="space-y-2">
          <h3>
            {state === "verifying" && "Verifying Your Email"}
            {state === "success" && "Email Verified!"}
            {state === "error" && "Verification Failed"}
          </h3>
          <p className="text-small text-muted-foreground">{message}</p>
        </div>

        {state === "error" && (
          <div className="space-y-3">
            <Button asChild className="w-full">
              <Link href={ROUTES.login}>Go to Login</Link>
            </Button>
          </div>
        )}

        {state === "success" && (
          <Button asChild className="w-full">
            <Link href={ROUTES.dashboard}>Go to Dashboard</Link>
          </Button>
        )}
      </motion.div>
    </Card>
  );
}

export default function VerifyEmail() {
  return (
    <Suspense fallback={
      <Card className="mx-auto w-full max-w-md p-8">
        <div className="flex justify-center">
          <Loader2 className="h-16 w-16 animate-spin text-primary" />
        </div>
      </Card>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}