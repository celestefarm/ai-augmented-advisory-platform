import React from "react";

import { Navigation } from "../components/Navigation";

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Navigation />
      <main className="relative z-10">
        {children}
      </main>
    </>
  );
}