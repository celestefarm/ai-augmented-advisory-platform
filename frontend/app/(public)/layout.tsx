import type { Metadata } from "next";
import { Inter, Cinzel } from "next/font/google";

import { ThemeProvider } from "@/components/common/ThemeProvider";
import { ThemeScript } from "@/components/common/ThemeScript";
import { Toaster } from "@/components/ui/sonner";

import "../globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
  preload: true,
});

const cinzel = Cinzel({
  variable: "--font-cinzel",
  subsets: ["latin"],
  display: "swap",
  preload: true,
});

export const metadata: Metadata = {
  title: "AI-Augmented | Command Intelligence",
  description: "Strategic decision-making with AI advisory. Your judgment amplified, not replaced.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html 
      lang="en" 
      suppressHydrationWarning
      className={`${inter.variable} ${cinzel.variable}`}
    >
      <head>
        <ThemeScript />
      </head>
      <body
        suppressHydrationWarning
      >
        <ThemeProvider>
          {children}
          <Toaster position="top-center" closeButton richColors />
        </ThemeProvider>
      </body>
    </html>
  );
}