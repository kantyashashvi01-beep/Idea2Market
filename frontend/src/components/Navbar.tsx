"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { getStoredUser, clearAuth } from "@/lib/api";
import { Cpu, PlusCircle, LogOut, Shield, Compass } from "lucide-react";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    setUser(getStoredUser());
  }, [pathname]);

  const handleLogout = () => {
    clearAuth();
    setUser(null);
    router.push("/login");
  };

  return (
    <nav className="bg-slate-900 border-b border-slate-800 text-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <Link href="/" className="flex items-center space-x-2 text-brand-500 font-bold text-lg hover:text-brand-400">
              <Cpu className="w-6 h-6 text-emerald-400" />
              <span className="text-white tracking-tight">Idea2market</span>
            </Link>
            <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded">
              Pre-CAD Engineer
            </span>
          </div>

          <div className="flex items-center space-x-4 text-sm font-medium">
            {user ? (
              <>
                <Link
                  href="/projects/new"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors shadow-sm"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>New Project</span>
                </Link>

                <Link
                  href="/"
                  className="text-slate-300 hover:text-white px-2 py-1 rounded transition-colors hidden md:inline"
                >
                  Dashboard
                </Link>

                {user.role === "admin" && (
                  <Link
                    href="/admin"
                    className="flex items-center gap-1 text-amber-400 hover:text-amber-300 px-2 py-1 rounded transition-colors"
                  >
                    <Shield className="w-4 h-4" />
                    <span className="hidden md:inline">Admin</span>
                  </Link>
                )}

                <div className="flex items-center gap-2 border-l border-slate-800 pl-4">
                  <span className="text-xs text-slate-400 hidden lg:inline">{user.email}</span>
                  <button
                    onClick={handleLogout}
                    title="Sign Out"
                    className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  href="/login"
                  className="text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/login?tab=register"
                  className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors shadow-sm"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
