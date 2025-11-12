"use client";

import { useStore } from "@/store";

import Loader from "@/components/common/Loader";

export default function ProtectedLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const { isAuthenticated } = useStore();

  if (!isAuthenticated) {
    return <Loader />;
  }

  // Remove Header and overflow - let dashboard handle its own layout
  return <>{children}</>;
}