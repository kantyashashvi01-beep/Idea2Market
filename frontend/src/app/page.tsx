"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { api, getStoredUser } from "@/lib/api";
import { PlusCircle, ArrowRight, Layers, FileText, CheckCircle2, ShieldAlert, Wrench } from "lucide-react";

export default function HomePage() {
  const [user, setUser] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = getStoredUser();
    setUser(stored);
    if (stored) {
      loadProjects();
    } else {
      setLoading(false);
    }
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await api.listProjects();
      setProjects(data);
    } catch (err) {
      console.error("Failed to load projects", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-10">
      {/* Hero Section */}
      <div className="text-center space-y-4 py-8 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
          <span>AI-Assisted Idea-to-Prototype Planning for Hardware Non-Engineers</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
          Turn your hardware idea into a <span className="text-emerald-600">reviewable engineering plan</span>
        </h1>
        <p className="text-slate-600 text-base sm:text-lg max-w-2xl mx-auto">
          Before spending thousands on CAD modeling or custom prototypes: generate structured requirements, Bill of Materials with India-relevant prices, staged roadmaps, and DFM readiness checklists in minutes.
        </p>

        <div className="pt-4 flex flex-wrap justify-center gap-4">
          <Link
            href="/projects/new"
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-emerald-600 text-white font-semibold hover:bg-emerald-500 shadow-md transition-all text-sm"
          >
            <PlusCircle className="w-5 h-5" />
            <span>Start Planning Hardware</span>
          </Link>
          <a
            href="#capabilities"
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-white border border-slate-300 text-slate-700 font-semibold hover:bg-slate-50 transition-all text-sm"
          >
            <span>Learn How It Works</span>
            <ArrowRight className="w-4 h-4 text-slate-400" />
          </a>
        </div>
      </div>

      {/* User Projects List (if signed in) */}
      {user && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Your Hardware Projects</h2>
              <p className="text-xs text-slate-500">Manage and iterate on your prototype specifications</p>
            </div>
            <Link
              href="/projects/new"
              className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Create New</span>
            </Link>
          </div>

          {loading ? (
            <div className="py-8 text-center text-slate-400 text-sm">Loading projects...</div>
          ) : projects.length === 0 ? (
            <div className="text-center py-10 space-y-3">
              <p className="text-slate-500 text-sm">No hardware projects created yet.</p>
              <Link
                href="/projects/new"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 text-white text-xs font-semibold"
              >
                Create your first project
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.map((p) => (
                <Link
                  key={p.id}
                  href={`/projects/${p.id}`}
                  className="p-4 rounded-lg border border-slate-200 hover:border-emerald-500 hover:shadow-md transition-all bg-slate-50/50 flex flex-col justify-between group"
                >
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-semibold text-slate-900 text-sm group-hover:text-emerald-700 transition-colors line-clamp-1">
                        {p.title}
                      </h3>
                      <span
                        className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                          p.safety_flag
                            ? "bg-red-100 text-red-700 border border-red-300"
                            : p.status === "ready"
                            ? "bg-emerald-100 text-emerald-700"
                            : "bg-slate-200 text-slate-700"
                        }`}
                      >
                        {p.safety_flag ? "Safety Flag" : p.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500">Domain: {p.domain.replace("_", " ")}</p>
                  </div>
                  <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs text-slate-400">
                    <span>Created {new Date(p.created_at).toLocaleDateString()}</span>
                    <span className="text-emerald-600 font-medium group-hover:translate-x-0.5 transition-transform flex items-center">
                      View Plan &rarr;
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Feature Highlights */}
      <div id="capabilities" className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 space-y-3 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
            <Layers className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-slate-900">Closed-World BOM</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Every component in your Bill of Materials is resolvable to verified hardware parts with realistic INR price ranges. Hallucinated part numbers are rejected by design.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 space-y-3 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-slate-900">Deterministic Arithmetic</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            All budgets, ranges, and allowances (fabrication, shipping, consumables, contingency) are calculated deterministically in code. Fully editable in your workspace.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 space-y-3 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-slate-900">Safety & DFM Guardrails</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Over 20 rule-based DFM checks assess vibration, ingress, and battery management. High-hazard domains (medical, mains power) trigger safety blocks and advisory notices.
          </p>
        </div>
      </div>
    </div>
  );
}
