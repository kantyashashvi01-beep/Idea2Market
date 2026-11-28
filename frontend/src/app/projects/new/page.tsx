"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { api, getStoredUser } from "@/lib/api";
import { Lightbulb, Sparkles, ArrowRight, AlertCircle } from "lucide-react";

const DEMO_EXAMPLE =
  "I want to develop an affordable autonomous agricultural robot for small Indian farmers. The rover should navigate between cotton or soybean crop rows, identify unwanted weeds, and perform targeted micro-spraying without damaging young crops or compacting wet field soil. It needs to run on battery power for at least 3 hours.";

export default function NewProjectPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [ideaText, setIdeaText] = useState("");
  const [domain, setDomain] = useState("agricultural_robotics");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const charLimit = 3000;

  const handleUseDemo = () => {
    setTitle("Autonomous Agri Weeding Rover");
    setIdeaText(DEMO_EXAMPLE);
    setDomain("agricultural_robotics");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!getStoredUser()) {
      router.push("/login");
      return;
    }

    if (ideaText.trim().length < 20) {
      setError("Please describe your idea with at least 20 characters.");
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const project = await api.createProject(title.trim() || "Untitled Hardware Idea", ideaText.trim(), domain);
      // Navigate to Clarification Q&A step
      router.push(`/projects/${project.id}/clarify`);
    } catch (err: any) {
      setError(err.message || "Failed to create project. Please verify backend connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Describe Your Hardware Concept</h1>
        <p className="text-sm text-slate-600">
          Explain what physical product you want to build in plain words. Idea2market will help clarify constraints, propose an architecture, and assemble a catalogued BOM.
        </p>
      </div>

      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-start gap-3">
        <Sparkles className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
        <div className="text-xs text-emerald-900 space-y-1">
          <p className="font-semibold">Hackathon Demo Quick-Start:</p>
          <p className="text-emerald-800">
            Click below to load the reference scenario: an autonomous agricultural rover with weed detection and spot spraying for smallholder farms.
          </p>
          <button
            type="button"
            onClick={handleUseDemo}
            className="mt-1 font-bold text-emerald-700 hover:text-emerald-900 underline underline-offset-2 flex items-center gap-1"
          >
            Load Example Agri-Rover Prompt &rarr;
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Project Title</label>
          <input
            type="text"
            required
            placeholder="e.g. Autonomous Farm Rover"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Hardware Domain</label>
          <select
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 bg-white"
          >
            <option value="agricultural_robotics">Agricultural Robotics & Field Machinery</option>
            <option value="iot_agritech">IoT & Smart Agritech Monitoring</option>
            <option value="general_hardware">General Consumer/Industrial Hardware</option>
          </select>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-semibold text-slate-700">Detailed Concept Description</label>
            <span className={`text-[10px] ${ideaText.length > charLimit ? "text-red-500" : "text-slate-400"}`}>
              {ideaText.length} / {charLimit} chars
            </span>
          </div>
          <textarea
            required
            rows={6}
            maxLength={charLimit}
            value={ideaText}
            onChange={(e) => setIdeaText(e.target.value)}
            placeholder="Describe who uses it, where it operates, what mechanical actions it performs, and any size/power/budget preferences..."
            className="w-full p-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 leading-relaxed"
          />
        </div>

        <button
          type="submit"
          disabled={loading || ideaText.length < 20}
          className="w-full py-3 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm shadow-md transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <span>Submitting Concept...</span>
          ) : (
            <>
              <span>Proceed to Technical Clarification</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
