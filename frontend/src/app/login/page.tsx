"use client";

import React, { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api, setAuthToken } from "@/lib/api";
import { Cpu, AlertCircle, ArrowRight } from "lucide-react";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("tab") === "register" ? "register" : "login";

  const [tab, setTab] = useState<"login" | "register">(initialTab);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      let data;
      if (tab === "register") {
        data = await api.register(email, password);
      } else {
        data = await api.login(email, password);
      }

      setAuthToken(data.access_token, {
        id: data.user_id,
        email: data.email,
        role: data.role,
      });

      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to authenticate. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-6">
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 mb-2">
          <Cpu className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900">
          {tab === "login" ? "Sign in to Idea2market" : "Create an Account"}
        </h1>
        <p className="text-xs text-slate-500">
          {tab === "login"
            ? "Access your hardware plans, BOM cost estimates, and reports"
            : "Get started turning your hardware ideas into engineering drafts"}
        </p>
      </div>

      <div className="flex border-b border-slate-200 text-sm font-semibold">
        <button
          type="button"
          onClick={() => { setTab("login"); setError(null); }}
          className={`flex-1 py-2 text-center border-b-2 transition-colors ${
            tab === "login"
              ? "border-emerald-600 text-emerald-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          Sign In
        </button>
        <button
          type="button"
          onClick={() => { setTab("register"); setError(null); }}
          className={`flex-1 py-2 text-center border-b-2 transition-colors ${
            tab === "register"
              ? "border-emerald-600 text-emerald-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          Register
        </button>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@domain.com"
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm shadow-md transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <span>Processing...</span>
          ) : (
            <>
              <span>{tab === "login" ? "Sign In" : "Create Account"}</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="py-20 text-center text-xs text-slate-400">Loading form...</div>}>
      <LoginForm />
    </Suspense>
  );
}
