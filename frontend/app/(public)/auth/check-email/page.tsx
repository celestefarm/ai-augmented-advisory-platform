"use client";

import { useState } from "react";

import { motion } from "framer-motion";
import { Mail, Loader2 } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import { ROUTES } from "@/routes";

export default function CheckEmail() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "your email";

  const [isResending, setIsResending] = useState(false);

  const handleResendEmail = async () => {
    setIsResending(true);

    try {
      const response = await fetch("/api/auth/resend-verification/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("Email sent!", {
          description: data.message || "Verification email has been resent.",
        });
      } else {
        toast.error("Failed to resend", {
          description: data.message || "Please try again later.",
        });
      }
    } catch (error) {
      toast.error("Error", {
        description: "Failed to resend verification email.",
      });
    } finally {
      setIsResending(false);
    }
  };

  return (
    <Card className="mx-auto w-full max-w-md p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="space-y-6 text-center"
      >
        {/* Icon */}
        <div className="flex justify-center">
          <div className="rounded-full bg-primary/10 p-4">
            <Mail className="h-12 w-12 text-primary" />
          </div>
        </div>

        {/* Title */}
        <div className="space-y-2">
          <h3>Check Your Email</h3>
          <p className="text-small text-muted-foreground">
            We&apos;ve sent a verification link to
          </p>
          <p className="font-medium text-foreground">{email}</p>
        </div>

        {/* Instructions */}
        <div className="space-y-3 text-left">
          <p className="text-sm text-muted-foreground">
            Click the verification link in the email to activate your account.
          </p>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Check your spam folder if you don&apos;t see it</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>The link expires in 3 days</span>
            </li>
          </ul>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <Button
            onClick={handleResendEmail}
            disabled={isResending}
            variant="outline"
            className="w-full"
          >
            {isResending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Resending...
              </>
            ) : (
              "Resend Verification Email"
            )}
          </Button>

          <Button asChild variant="ghost" className="w-full">
            <Link href={ROUTES.login}>Back to Login</Link>
          </Button>
        </div>
      </motion.div>
    </Card>
  );
}