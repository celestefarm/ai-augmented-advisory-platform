"use client";

import { useState } from "react";

import { Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import Logo from "@/components/common/Logo";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { Button } from "@/components/ui/button";

import { NAV_LINKS } from "@/constants";
import { ROUTES } from "@/routes";

import { WAITLIST_URL } from "@/constants";

export function Navbar() {
  const pathname = usePathname();

  // Mobile menu state
  const [isOpen, setIsOpen] = useState(false);

  /**
   * Determines if a navigation link is active based on current pathname
   * Handles exact matches and nested routes (e.g., /about/team matches /about)
   */
  const isActiveLink = (href: string): boolean => {
    return pathname === href || (href !== "/" && pathname.startsWith(href));
  };

  /**
   * Renders navigation links with consistent styling and active state
   * @param layout - Layout style: 'horizontal' for desktop, 'vertical' for mobile
   * @param closeMenu - Whether clicking a link should close the mobile menu
   */
  const renderNavLinks = (
    layout: "horizontal" | "vertical",
    closeMenu = false,
  ) => {
    const layoutClasses =
      layout === "horizontal"
        ? "hidden items-center gap-2.5 md:flex"
        : "flex flex-col gap-2.5";

    return (
      <nav className={layoutClasses}>
        {NAV_LINKS.map(link => {
          const isActive = isActiveLink(link.href);
          return (
            <Link
              key={link.label}
              href={link.href}
              className={`relative rounded-lg px-3 py-2 transition-all duration-300 ${
                isActive
                  ? "bg-input/50 font-semibold"
                  : "font-medium hover:bg-input/50"
              }`}
              onClick={closeMenu ? () => setIsOpen(false) : undefined}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    );
  };

  /**
   * Renders beta button with responsive layout
   * @param layout - Layout style: 'horizontal' for desktop, 'vertical' for mobile
   * @param closeMenu - Whether clicking a button should close the mobile menu
   */
  const renderBetaButton = (
    layout: "horizontal" | "vertical",
    closeMenu = false,
  ) => {
    const layoutClasses =
      layout === "horizontal"
        ? "hidden items-center gap-5 md:flex"
        : "flex flex-col gap-2.5 border-t border-border pt-5";

    const buttonClasses = layout === "vertical" ? "w-full" : "";

    return (
      <div className={layoutClasses}>
        <Button asChild size="lg" className={buttonClasses}>
          <Link
            href={WAITLIST_URL}
            target="_blank"
            rel="noopener noreferrer"
            onClick={closeMenu ? () => setIsOpen(false) : undefined}
          >
            Join BETA
          </Link>
        </Button>
      </div>
    );
  };

  return (
    <nav className="fixed top-0 right-0 left-0 z-50 h-[var(--header-height)] border-b border-black/10 bg-white/70 shadow-lg backdrop-blur-lg dark:border-white/10 dark:bg-white/5">
      <div className="container-width flex h-full items-center justify-between py-5">
        {/* Logo and Brand Section */}
        <Logo href={ROUTES.home} />

        {/* Desktop Navigation and Auth */}
        <div className="flex items-center gap-2.5 md:gap-5">
          {renderNavLinks("horizontal")}
          {renderBetaButton("horizontal")}

          {/* Theme toggle */}
          <ThemeToggle />

          {/* Mobile Menu Toggle */}
          <Button
            variant="ghost"
            onClick={() => setIsOpen(!isOpen)}
            className="transition-colors hover:bg-accent/50 md:hidden"
            aria-label="Toggle mobile menu"
          >
            {isOpen ? (
              <X className="!h-5 !w-5" />
            ) : (
              <Menu className="!h-5 !w-5" />
            )}
          </Button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div className="absolute top-full right-0 left-0 border-b border-black/10 bg-white/90 shadow-lg backdrop-blur-lg md:hidden dark:border-white/10 dark:bg-black/90">
          <div className="container-width space-y-2.5 p-5">
            {renderNavLinks("vertical", true)}
            {renderBetaButton("vertical", true)}
          </div>
        </div>
      )}
    </nav>
  );
}