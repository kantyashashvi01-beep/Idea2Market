"use client";

import React from "react";
import { AlertTriangle } from "lucide-react";

export const DISCLAIMER_TEXT =
  "AI-generated preliminary draft. Not an engineering certification, not a quotation, and not a safety or regulatory approval. Have a qualified engineer review before building or selling anything.";

export default function DisclaimerBanner() {
  return (
    <div className="bg-amber-500/10 border-b border-amber-500/30 text-amber-900 px-4 py-2 text-xs md:text-sm font-medium flex items-center justify-center gap-2 text-center">
      <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
      <span>{DISCLAIMER_TEXT}</span>
    </div>
  );
}
