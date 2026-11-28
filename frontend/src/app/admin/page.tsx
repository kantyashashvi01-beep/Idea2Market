"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getStoredUser } from "@/lib/api";
import { Shield, Wrench, Plus, CheckCircle, AlertCircle, RefreshCw } from "lucide-react";

export default function AdminPage() {
  const router = useRouter();
  const [components, setComponents] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [tab, setTab] = useState<"components" | "rules">("components");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const user = getStoredUser();
    if (!user || user.role !== "admin") {
      router.push("/");
      return;
    }
    loadData();
  }, [router]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [comps, rls] = await Promise.all([api.getAdminComponents(), api.getAdminRules()]);
      setComponents(comps);
      setRules(rls);
    } catch (err: any) {
      setError(err.message || "Failed to load admin data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-amber-600" />
            <h1 className="text-xl font-bold text-slate-900">Catalogue &amp; Rule Administration</h1>
          </div>
          <p className="text-xs text-slate-500">
            Maintain closed-world hardware components and deterministic DFM/readiness rules.
          </p>
        </div>
        <button
          onClick={loadData}
          className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      <div className="flex gap-2 border-b border-slate-200 pb-2 text-xs font-semibold">
        <button
          onClick={() => setTab("components")}
          className={`px-4 py-2 rounded-lg transition-colors ${
            tab === "components" ? "bg-emerald-600 text-white" : "bg-white text-slate-600 hover:bg-slate-100"
          }`}
        >
          Components Catalogue ({components.length})
        </button>
        <button
          onClick={() => setTab("rules")}
          className={`px-4 py-2 rounded-lg transition-colors ${
            tab === "rules" ? "bg-emerald-600 text-white" : "bg-white text-slate-600 hover:bg-slate-100"
          }`}
        >
          Manufacturing Rules ({rules.length})
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="py-12 text-center text-xs text-slate-400">Loading admin dataset...</div>
      ) : tab === "components" ? (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-700 font-bold">
                  <th className="py-2.5 px-3">ID</th>
                  <th className="py-2.5 px-3">Name</th>
                  <th className="py-2.5 px-3">Price Range (INR)</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Typical Application</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {components.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-3 font-mono text-slate-500">{c.id}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{c.name}</td>
                    <td className="py-2.5 px-3 font-mono text-slate-600">₹{c.low_inr} - ₹{c.high_inr}</td>
                    <td className="py-2.5 px-3">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                        {c.price_verified ? "Verified" : "Placeholder"}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-500 max-w-sm">{c.typical_use}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-700 font-bold">
                  <th className="py-2.5 px-3">Rule ID</th>
                  <th className="py-2.5 px-3">Area</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Version</th>
                  <th className="py-2.5 px-3">Requirement Text</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rules.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-800">{r.id}</td>
                    <td className="py-2.5 px-3 uppercase text-[10px] font-semibold text-slate-500">{r.area}</td>
                    <td className="py-2.5 px-3 uppercase text-[10px] font-bold text-amber-700">{r.severity}</td>
                    <td className="py-2.5 px-3 font-mono text-slate-500">v{r.version}</td>
                    <td className="py-2.5 px-3 text-slate-700 max-w-md">{r.text}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
