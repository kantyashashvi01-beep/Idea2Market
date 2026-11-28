"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import {
  FileText,
  Layers,
  ShoppingBag,
  MapPin,
  AlertTriangle,
  CheckCircle,
  Clock,
  Download,
  Building,
  Edit2,
  RefreshCw,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";

export default function ProjectReportWorkspace() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [detail, setDetail] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<
    "requirements" | "architecture" | "bom" | "roadmap" | "risks" | "readiness" | "facilities"
  >("requirements");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProjectDetail(projectId);
      setDetail(data);
    } catch (err: any) {
      setError(err.message || "Failed to load project details.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateBOMQty = async (itemId: string, newQty: number) => {
    if (newQty < 1 || newQty > 100) return;
    try {
      setSaving(true);
      const updatedBom = await api.updateBOMItem(projectId, itemId, { quantity: newQty });
      setDetail((prev: any) => ({ ...prev, bom: updatedBom }));
    } catch (err: any) {
      alert("Failed to update quantity: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateAllowance = async (index: number, newPercent: number) => {
    if (newPercent < 0 || newPercent > 100) return;
    try {
      setSaving(true);
      const currentAllowances = [...detail.bom.allowances];
      currentAllowances[index].percent = newPercent;
      const updatedBom = await api.updateAllowances(projectId, currentAllowances);
      setDetail((prev: any) => ({ ...prev, bom: updatedBom }));
    } catch (err: any) {
      alert("Failed to update allowance: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-3">
        <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-700">Loading Engineering Report...</p>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="max-w-md mx-auto py-12 p-6 bg-red-50 border border-red-200 rounded-xl text-center space-y-3">
        <AlertTriangle className="w-8 h-8 text-red-600 mx-auto" />
        <h2 className="font-bold text-red-900 text-sm">Failed to Load Report</h2>
        <p className="text-xs text-red-700">{error}</p>
        <button
          onClick={loadProject}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-xs font-semibold"
        >
          Retry
        </button>
      </div>
    );
  }

  const { project, requirements, subsystems, interfaces, bom, risks, roadmap, rule_findings, safety_warning } = detail;

  return (
    <div className="space-y-6">
      {/* Safety Alert if safety flag */}
      {project.safety_flag && (
        <div className="p-4 rounded-xl bg-orange-50 border-2 border-orange-400 text-orange-950 flex items-start gap-3 shadow-sm">
          <ShieldAlert className="w-6 h-6 text-orange-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h3 className="font-bold text-sm tracking-tight text-orange-900">
              SAFETY-CRITICAL DOMAIN ALERT: Readiness Status Gated
            </h3>
            <p className="text-xs text-orange-800 leading-relaxed">
              {safety_warning ||
                "This hardware concept interfaces with regulated medical, high-voltage, or automotive safety systems. Commercial readiness is blocked until formal review by a qualified licensed engineer."}
            </p>
          </div>
        </div>
      )}

      {/* Header Info */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900">{project.title}</h1>
            <span
              className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full ${
                project.safety_flag
                  ? "bg-orange-100 text-orange-800 border border-orange-300"
                  : "bg-emerald-100 text-emerald-800"
              }`}
            >
              {project.status.replace("_", " ")}
            </span>
          </div>
          <p className="text-xs text-slate-500">
            Domain: <span className="font-semibold text-slate-700">{project.domain.replace("_", " ")}</span> &bull;
            Created {new Date(project.created_at).toLocaleDateString()}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={api.getDownloadPdfUrl(projectId)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-sm transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF Report</span>
          </a>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-200 flex flex-wrap gap-1 text-xs font-semibold">
        {[
          { key: "requirements", label: "Requirements", icon: FileText },
          { key: "architecture", label: "Architecture", icon: Layers },
          { key: "bom", label: "BOM & Budget", icon: ShoppingBag },
          { key: "roadmap", label: "Roadmap", icon: Clock },
          { key: "risks", label: "Engineering Risks", icon: AlertTriangle },
          { key: "readiness", label: "DFM & Readiness", icon: CheckCircle },
          { key: "facilities", label: "Prototyping Facilities", icon: Building },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-1.5 px-4 py-2.5 border-b-2 transition-all ${
                isActive
                  ? "border-emerald-600 text-emerald-700 bg-emerald-50/50"
                  : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: Requirements */}
      {activeTab === "requirements" && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="border-b border-slate-100 pb-3 flex justify-between items-center">
            <div>
              <h2 className="text-base font-bold text-slate-900">Functional &amp; Constraint Requirements</h2>
              <p className="text-xs text-slate-500">Preliminary specification derived from your concept statement</p>
            </div>
          </div>

          <div className="divide-y divide-slate-100">
            {requirements.map((r: any) => (
              <div key={r.id} className="py-3 flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[9px] uppercase font-extrabold px-1.5 py-0.5 rounded ${
                        r.kind === "functional"
                          ? "bg-blue-100 text-blue-700"
                          : r.kind === "constraint"
                          ? "bg-amber-100 text-amber-700"
                          : "bg-purple-100 text-purple-700"
                      }`}
                    >
                      {r.kind}
                    </span>
                    <span
                      className={`text-[9px] uppercase font-bold px-1.5 py-0.5 rounded ${
                        r.priority === "high"
                          ? "text-red-700"
                          : r.priority === "medium"
                          ? "text-amber-700"
                          : "text-slate-600"
                      }`}
                    >
                      {r.priority} priority
                    </span>
                    <span className="text-[9px] text-slate-400">source: {r.source_type}</span>
                  </div>
                  <p className="text-xs text-slate-800 leading-relaxed">{r.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Architecture */}
      {activeTab === "architecture" && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900">Subsystem Architecture Breakdown</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {subsystems.map((sub: any, idx: number) => (
                <div key={sub.id} className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <h3 className="font-bold text-xs text-slate-900">{sub.name}</h3>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">{sub.purpose}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900">Inter-Subsystem Hardware Interfaces</h2>
            <div className="divide-y divide-slate-100">
              {interfaces.map((iface: any) => (
                <div key={iface.id} className="py-2.5 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-800">{iface.from_subsystem}</span>
                    <span className="text-slate-400">&rarr;</span>
                    <span className="font-semibold text-slate-800">{iface.to_subsystem}</span>
                  </div>
                  <span className="text-slate-500 italic">{iface.description}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: BOM & Cost */}
      {activeTab === "bom" && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
              <div>
                <h2 className="text-base font-bold text-slate-900">Closed-World Bill of Materials</h2>
                <p className="text-xs text-slate-500">
                  Every row links to a verified catalogue component. All totals are computed deterministically in code.
                </p>
              </div>
              <span className="text-[10px] bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-semibold self-start sm:self-center">
                Unverified Placeholder Prices
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                    <th className="py-2.5 px-3">Cat ID</th>
                    <th className="py-2.5 px-3">Component</th>
                    <th className="py-2.5 px-3 text-center">Qty</th>
                    <th className="py-2.5 px-3">Unit Range (INR)</th>
                    <th className="py-2.5 px-3">Subtotal Range (INR)</th>
                    <th className="py-2.5 px-3">Role / Typical Use</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {bom.items.map((item: any) => (
                    <tr key={item.component_id} className="hover:bg-slate-50/50">
                      <td className="py-2.5 px-3 font-mono text-slate-500">{item.component_id}</td>
                      <td className="py-2.5 px-3">
                        <div className="font-semibold text-slate-900">{item.name}</div>
                        <span className="text-[9px] text-amber-700 bg-amber-50 px-1.5 py-0.2 rounded border border-amber-200">
                          unverified placeholder price
                        </span>
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="flex items-center justify-center gap-1.5">
                          <button
                            disabled={saving || item.quantity <= 1}
                            onClick={() => handleUpdateBOMQty(item.id, item.quantity - 1)}
                            className="w-5 h-5 rounded bg-slate-200 hover:bg-slate-300 text-slate-700 flex items-center justify-center font-bold text-xs disabled:opacity-30"
                          >
                            -
                          </button>
                          <span className="w-6 text-center font-bold text-slate-800">{item.quantity}</span>
                          <button
                            disabled={saving || item.quantity >= 100}
                            onClick={() => handleUpdateBOMQty(item.id, item.quantity + 1)}
                            className="w-5 h-5 rounded bg-slate-200 hover:bg-slate-300 text-slate-700 flex items-center justify-center font-bold text-xs disabled:opacity-30"
                          >
                            +
                          </button>
                        </div>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-600">
                        ₹{item.unit_low_inr.toLocaleString()} - ₹{item.unit_high_inr.toLocaleString()}
                      </td>
                      <td className="py-2.5 px-3 font-mono font-bold text-emerald-800">
                        ₹{item.total_low_inr.toLocaleString()} - ₹{item.total_high_inr.toLocaleString()}
                      </td>
                      <td className="py-2.5 px-3 text-slate-500 max-w-xs">{item.role_in_design}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Configurable Allowances and Grand Total */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900">Prototype Budget &amp; Allowances</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Configurable Allowances (% of Base)
                </h3>
                {bom.allowances.map((allow: any, idx: number) => (
                  <div key={allow.name} className="flex items-center justify-between text-xs p-2 rounded bg-slate-50 border border-slate-200">
                    <span className="font-medium text-slate-700">{allow.label}</span>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={allow.percent}
                        onChange={(e) => handleUpdateAllowance(idx, parseFloat(e.target.value) || 0)}
                        className="w-14 px-1.5 py-0.5 border border-slate-300 rounded text-right font-bold text-xs"
                      />
                      <span className="text-slate-500">%</span>
                      <span className="font-mono text-slate-600 text-[11px] w-28 text-right">
                        ₹{allow.amount_low_inr.toLocaleString()} - ₹{allow.amount_high_inr.toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-slate-900 text-white rounded-xl p-6 flex flex-col justify-between space-y-4">
                <div>
                  <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                    Total Estimated Prototype Budget Range
                  </span>
                  <div className="text-2xl sm:text-3xl font-extrabold text-white font-mono mt-1">
                    ₹{bom.grand_total_inr[0].toLocaleString()} - ₹{bom.grand_total_inr[1].toLocaleString()}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
                    Includes components (₹{bom.base_total_inr[0].toLocaleString()} - ₹{bom.base_total_inr[1].toLocaleString()}) plus custom fabrication, shipping, and rework allowances.
                  </p>
                </div>
                <div className="text-[10px] text-amber-300/80 bg-slate-800 p-2 rounded border border-slate-700">
                  {bom.notice}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Roadmap */}
      {activeTab === "roadmap" && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h2 className="text-base font-bold text-slate-900">Staged Prototyping Roadmap</h2>
          <div className="space-y-4">
            {roadmap.map((stage: any) => (
              <div key={stage.id} className="p-4 rounded-lg border border-slate-200 bg-slate-50/40 flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-emerald-600 text-white text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  {stage.position}
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-xs text-slate-900">{stage.title}</h3>
                    <span className="text-[10px] font-semibold text-slate-500 bg-slate-200 px-2 py-0.5 rounded">
                      {stage.duration_note}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">{stage.deliverable}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 5: Risks */}
      {activeTab === "risks" && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-slate-900">Engineering Failure Modes &amp; Risk Register</h2>
            <p className="text-xs text-slate-500">Every risk contains a technical rationale and mandatory expert-review badge</p>
          </div>
          <div className="space-y-3">
            {risks.map((r: any) => (
              <div key={r.id} className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[9px] uppercase font-bold px-2 py-0.5 rounded ${
                        r.severity === "high"
                          ? "bg-red-100 text-red-800 border border-red-200"
                          : r.severity === "medium"
                          ? "bg-amber-100 text-amber-800 border border-amber-200"
                          : "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {r.severity} severity
                    </span>
                    <h3 className="font-bold text-xs text-slate-900">{r.title}</h3>
                  </div>
                  {r.needs_expert && (
                    <span className="text-[10px] font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                      Needs Qualified Engineer Review
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-700 leading-relaxed pl-1">
                  <span className="font-semibold text-slate-800">Technical Rationale:</span> {r.reason}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 6: Readiness */}
      {activeTab === "readiness" && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-slate-900">Rule-Based DFM &amp; Readiness Checklist</h2>
            <p className="text-xs text-slate-500">Evaluated deterministically against 20+ hardware manufacturing rules</p>
          </div>
          <div className="divide-y divide-slate-100">
            {rule_findings.map((f: any) => (
              <div key={f.id} className="py-3 flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-600">{f.rule_id}</span>
                    <span
                      className={`text-[9px] uppercase font-extrabold px-2 py-0.5 rounded ${
                        f.status === "pass"
                          ? "bg-emerald-100 text-emerald-800"
                          : f.status === "warn"
                          ? "bg-amber-100 text-amber-800"
                          : f.status === "fail"
                          ? "bg-red-100 text-red-800"
                          : "bg-purple-100 text-purple-800"
                      }`}
                    >
                      {f.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700">{f.note}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 7: Facilities */}
      {activeTab === "facilities" && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-slate-900">Public Prototyping &amp; Testing Facilities in India</h2>
            <p className="text-xs text-slate-500">
              Verified public shared infrastructure for booking equipment, fabrication time, and mentor assistance.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2 flex flex-col justify-between">
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-sm text-slate-900">I-STEM Portal</h3>
                  <span className="text-[10px] bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-semibold">
                    National
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Indian Science Technology and Engineering facilities Map. National web portal for reserving equipment time on publicly funded research and testing instruments across India.
                </p>
              </div>
              <a
                href="https://www.startupindia.gov.in/content/sih/en/i-stem.html"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1 mt-3"
              >
                <span>Visit I-STEM Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            <div className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2 flex flex-col justify-between">
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-sm text-slate-900">T-Works Hyderabad</h3>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold">
                    Hyderabad
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  India&apos;s largest prototyping centre. 78,000 sq ft facility with PCB fabrication, laser cutting, CNC machining, 3D printing, and non-discriminatory no-equity access policy.
                </p>
              </div>
              <a
                href="https://tworks.telangana.gov.in/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1 mt-3"
              >
                <span>Visit T-Works Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
