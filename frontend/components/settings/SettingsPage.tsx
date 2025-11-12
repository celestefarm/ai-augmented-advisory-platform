"use client";

import { useEffect, useState } from "react";

import { motion } from "framer-motion";
import { User, Shield, CreditCard, Bell, ArrowLeft, Menu, X } from "lucide-react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";

import { useStore } from "@/store";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";

import { ROUTES } from "@/routes";

type SettingsTab = "general" | "account" | "privacy" | "billing";

interface FormChoice {
  value: string;
  label: string;
}

interface FormChoices {
  industries: FormChoice[];
  regions: FormChoice[];
}

export default function SettingsPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useStore();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [formChoices, setFormChoices] = useState<FormChoices>({
    industries: [],
    regions: [],
  });
  
  // Get tab from URL, default to general
  const getTabFromPath = (): SettingsTab => {
    if (pathname.includes("/account")) return "account";
    if (pathname.includes("/privacy")) return "privacy";
    if (pathname.includes("/billing")) return "billing";
    return "general";
  };

  const [activeTab, setActiveTab] = useState<SettingsTab>(getTabFromPath());

  // Fetch form choices on mount
  useEffect(() => {
    const fetchFormChoices = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/form-choices/`
        );
        
        if (response.ok) {
          const data = await response.json();
          setFormChoices(data);
        }
      } catch (error) {
        console.error('Failed to fetch form choices:', error);
      }
    };

    fetchFormChoices();
  }, []);

  // Update tab when URL changes
  useEffect(() => {
    setActiveTab(getTabFromPath());
  }, [pathname]);

  const tabs = [
    { id: "general", label: "General", icon: Bell, path: "/settings" },
    { id: "account", label: "Account", icon: User, path: "/settings/account" },
    { id: "privacy", label: "Privacy", icon: Shield, path: "/settings/privacy" },
    { id: "billing", label: "Billing", icon: CreditCard, path: "/settings/billing" },
  ];

  const handleTabChange = (tabId: SettingsTab) => {
    setActiveTab(tabId);
    setIsMobileMenuOpen(false); // Close mobile menu on navigation
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="fixed top-3 left-3 z-50 md:hidden"
      >
        {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 shrink-0 transform border-r border-border bg-card transition-transform md:static md:translate-x-0 ${
          isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-14 items-center justify-between border-b border-border px-6">
          <h2 className="text-lg font-semibold">Settings</h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push(ROUTES.dashboard)}
            title="Back to dashboard"
            className="hidden md:flex"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </div>

        <nav className="space-y-1 p-3">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <Link
                key={tab.id}
                href={tab.path}
                onClick={() => handleTabChange(tab.id as SettingsTab)}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-primary/10 text-primary font-medium"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
                prefetch={true}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span>{tab.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Back Button for Mobile */}
        <div className="absolute bottom-4 left-0 right-0 px-3 md:hidden">
          <Button
            variant="outline"
            className="w-full"
            onClick={() => router.push(ROUTES.dashboard)}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Mobile Header */}
        <div className="sticky top-0 z-10 flex h-14 items-center border-b border-border bg-card px-4 md:hidden">
          <h2 className="ml-12 text-lg font-semibold">
            {tabs.find(t => t.id === activeTab)?.label}
          </h2>
        </div>

        <div className="mx-auto max-w-3xl p-4 md:p-8">
          <div>
            {activeTab === "general" && <GeneralSettings user={user} formChoices={formChoices} />}
            {activeTab === "account" && <AccountSettings user={user} />}
            {activeTab === "privacy" && <PrivacySettings />}
            {activeTab === "billing" && <BillingSettings />}
          </div>
        </div>
      </main>
    </div>
  );
}

// General Settings Component
function GeneralSettings({ user, formChoices }: { user: any; formChoices: FormChoices }) {
  const { updateProfile } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    industry: user?.industry || "",
    region: user?.region || "",
    role: user?.role || "",
  });

  const hasChanges = () => {
    return (
      formData.industry !== (user?.industry || "") ||
      formData.region !== (user?.region || "") ||
      formData.role !== (user?.role || "")
    );
  };

  const handleSave = async () => {
    if (!hasChanges()) {
      toast.info("No changes to save");
      return;
    }

    setIsLoading(true);
    try {
      await updateProfile(formData);
      toast.success("Settings saved successfully");
    } catch (error) {
      console.log(error);
      toast.error("Failed to save settings");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">General</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage your general preferences and settings
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium">Professional Information</h3>
          <p className="text-sm text-muted-foreground">
            Help us personalize your experience
          </p>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Industry</Label>
            <Select
              value={formData.industry}
              onValueChange={(value) => setFormData({ ...formData, industry: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select your industry" />
              </SelectTrigger>
              <SelectContent>
                {formChoices.industries.map((industry) => (
                  <SelectItem key={industry.value} value={industry.value}>
                    {industry.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Region</Label>
            <Select
              value={formData.region}
              onValueChange={(value) => setFormData({ ...formData, region: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select your region" />
              </SelectTrigger>
              <SelectContent>
                {formChoices.regions.map((region) => (
                  <SelectItem key={region.value} value={region.value}>
                    {region.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="role">Role/Title</Label>
            <Input
              id="role"
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              placeholder="e.g., VP Strategy, CEO, Director"
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={isLoading || !hasChanges()}>
          {isLoading ? "Saving..." : "Save changes"}
        </Button>
      </div>
    </div>
  );
}

// Account Settings Component
function AccountSettings({ user }: { user: any }) {
  const { updateProfile } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
  });

  const hasChanges = () => {
    return (
      formData.first_name !== (user?.first_name || "") ||
      formData.last_name !== (user?.last_name || "")
    );
  };

  const handleSave = async () => {
    if (!hasChanges()) {
      toast.info("No changes to save");
      return;
    }

    setIsLoading(true);
    try {
      await updateProfile(formData);
      toast.success("Account updated successfully");
    } catch (error) {
      toast.error("Failed to update account");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Account</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage your account information
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium">Profile</h3>
          <p className="text-sm text-muted-foreground">
            Update your personal information
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="firstName">First name</Label>
            <Input
              id="firstName"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              placeholder="Enter your first name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="lastName">Last name</Label>
            <Input
              id="lastName"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              placeholder="Enter your last name"
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={user?.email || ""}
            placeholder="Enter your email"
            disabled
          />
          <p className="text-xs text-muted-foreground">
            Email cannot be changed
          </p>
        </div>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={isLoading || !hasChanges()}>
          {isLoading ? "Saving..." : "Save changes"}
        </Button>
      </div>
    </div>
  );
}

// Privacy Settings Component
function PrivacySettings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Privacy</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Control your privacy and data settings
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium">Data Collection</h3>
          <p className="text-sm text-muted-foreground">
            Help us provide personalized responses
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between rounded-lg border border-border bg-muted/30 p-4">
            <div className="space-y-0.5">
              <Label>Personalized responses</Label>
              <p className="text-sm text-muted-foreground">
                Allow AI to learn from your conversations to provide better, 
                personalized responses
              </p>
            </div>
            <Switch defaultChecked disabled />
          </div>
        </div>
      </div>

      <Separator />

      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium text-destructive">Danger Zone</h3>
          <p className="text-sm text-muted-foreground">
            Irreversible actions that affect your account
          </p>
        </div>

        <Button variant="destructive">Delete account</Button>
      </div>
    </div>
  );
}

// Billing Settings Component
function BillingSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Billing</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage your subscription and billing information
        </p>
      </div>

      <Separator />

      <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed border-border">
        <div className="text-center">
          <CreditCard className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-4 text-lg font-semibold">Coming Soon</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Billing and subscription management features are currently under
            development.
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            Stay tuned for updates!
          </p>
        </div>
      </div>
    </div>
  );
}