"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { HelpCircle, ArrowRight, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

export default function ClarificationPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [questions, setQuestions] = useState<any[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQuestions();
  }, [projectId]);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getClarifications(projectId);
      setQuestions(data);
      const initialAnswers: Record<string, string> = {};
      data.forEach((q: any) => {
        initialAnswers[q.id] = "";
      });
      setAnswers(initialAnswers);
    } catch (err: any) {
      setError(err.message || "Failed to load clarifying questions.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (qId: string, val: string) => {
    setAnswers((prev) => ({ ...prev, [qId]: val }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const payload = Object.entries(answers).map(([question_id, answer]) => ({
        question_id,
        answer: answer.trim() || "Unspecified / standard default assumptions",
      }));

      await api.submitAnswers(projectId, payload);
      router.push(`/projects/${projectId}/generate`);
    } catch (err: any) {
      setError(err.message || "Failed to record answers.");
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-6 space-y-6">
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
          <span>Step 2 of 3: Engineering Clarifications</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Clarifying Technical Parameters</h1>
        <p className="text-sm text-slate-600">
          To help select appropriate motors, batteries, and sensors, answer these clarifying questions about your prototype&apos;s operating constraints.
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
          <p className="text-sm font-medium text-slate-700">Formulating clarifying questions...</p>
          <p className="text-xs text-slate-400">Analyzing your concept requirements and operating domain</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="space-y-5">
            {questions.map((q, idx) => (
              <div key={q.id} className="space-y-2 border-b border-slate-100 pb-5 last:border-none last:pb-0">
                <div className="flex items-start gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <label className="text-sm font-semibold text-slate-800 leading-snug">{q.question}</label>
                </div>
                {q.context_reason && (
                  <p className="text-xs text-slate-500 pl-7 italic">{q.context_reason}</p>
                )}
                <div className="pl-7">
                  <input
                    type="text"
                    value={answers[q.id] || ""}
                    onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                    placeholder="Enter your answer or leave blank for sensible defaults..."
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500"
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="pt-4 flex items-center justify-between border-t border-slate-100">
            <button
              type="button"
              onClick={handleSubmit}
              className="text-xs font-medium text-slate-500 hover:text-slate-800"
            >
              Skip &amp; Use Defaults
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="py-2.5 px-6 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm shadow-md transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {submitting ? (
                <span>Launching Pipeline...</span>
              ) : (
                <>
                  <span>Generate Engineering Plan</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
