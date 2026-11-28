"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Loader2, CheckCircle2, AlertTriangle, ArrowRight, Server } from "lucide-react";

const STAGES = [
  { key: "init", label: "Initializing Planning Engine" },
  { key: "requirements", label: "Generating Requirements & Assumptions" },
  { key: "architecture", label: "Designing Subsystems & Interfaces" },
  { key: "retrieval_and_bom", label: "Querying Closed-World Catalogue & Assembling BOM" },
  { key: "cost_and_rules", label: "Executing Cost Arithmetic & Evaluating DFM Rules" },
  { key: "roadmap_and_risks", label: "Synthesizing Roadmap & Engineering Risks" },
  { key: "report", label: "Compiling Report & Building PDF Document" },
];

export default function GenerationProgressPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [coldStartNotice, setColdStartNotice] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    startPipeline();
  }, [projectId]);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((s) => {
        if (s > 20 && !job) {
          setColdStartNotice(true);
        }
        return s + 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [job]);

  const startPipeline = async () => {
    try {
      const res = await api.generatePipeline(projectId);
      setJobId(res.job_id);
    } catch (err: any) {
      setError(err.message || "Failed to trigger generation pipeline.");
    }
  };

  useEffect(() => {
    if (!jobId) return;

    const pollInterval = setInterval(async () => {
      try {
        const jobStatus = await api.getJobStatus(jobId);
        setJob(jobStatus);

        if (jobStatus.status === "done") {
          clearInterval(pollInterval);
          setTimeout(() => {
            router.push(`/projects/${projectId}`);
          }, 1500);
        } else if (jobStatus.status === "failed") {
          clearInterval(pollInterval);
          setError(jobStatus.error_message || "Generation pipeline failed.");
        }
      } catch (err: any) {
        console.warn("Polling error (might be warming up):", err);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [jobId, projectId, router]);

  const progress = job?.progress_percent || 5;

  return (
    <div className="max-w-xl mx-auto py-12 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold text-slate-900">Generating Engineering Plan</h1>
        <p className="text-xs text-slate-500">
          Synthesizing requirements, catalogue BOM, deterministic budget, and readiness checklist.
        </p>
      </div>

      {coldStartNotice && !job && (
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-start gap-3">
          <Server className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold">Backend Service Waking Up</p>
            <p className="text-blue-800">
              The Render free-tier instance spins down after idle periods and can take about 45-60 seconds to boot. Retrying automatically...
            </p>
          </div>
        </div>
      )}

      {error ? (
        <div className="p-6 rounded-xl bg-red-50 border border-red-200 space-y-4 text-center">
          <AlertTriangle className="w-8 h-8 text-red-600 mx-auto" />
          <div className="space-y-1">
            <h3 className="font-bold text-red-900 text-sm">Generation Error</h3>
            <p className="text-xs text-red-700">{error}</p>
          </div>
          <button
            onClick={() => { setError(null); startPipeline(); }}
            className="px-4 py-2 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-500"
          >
            Retry Pipeline
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span>Overall Progress</span>
              <span className="text-emerald-600">{progress}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
              <div
                className="bg-emerald-600 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="text-right text-[10px] text-slate-400">
              Elapsed: {elapsedSeconds}s
            </div>
          </div>

          {/* Stage List */}
          <div className="space-y-3 pt-2">
            {STAGES.map((s, idx) => {
              const currentStageIdx = STAGES.findIndex((stg) => stg.key === job?.stage);
              const isPast = currentStageIdx > idx || job?.status === "done";
              const isCurrent = job?.stage === s.key;

              return (
                <div key={s.key} className="flex items-center gap-3 text-xs">
                  {isPast ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-emerald-600 animate-spin shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                  )}
                  <span className={`${isCurrent ? "font-bold text-emerald-700" : isPast ? "text-slate-700 font-medium" : "text-slate-400"}`}>
                    {s.label}
                  </span>
                </div>
              );
            })}
          </div>

          {job?.status === "done" && (
            <div className="p-3 bg-emerald-50 rounded-lg text-emerald-800 text-xs text-center font-medium flex items-center justify-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Generation complete! Redirecting to report workspace...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
