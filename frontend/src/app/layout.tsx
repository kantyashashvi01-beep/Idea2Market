import type { Metadata } from "next";
import "./globals.css";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Idea2market | AI Product Engineer for Non-Engineers",
  description: "Transform hardware ideas into reviewable engineering requirements, BOM, budgets, and staged roadmaps before spending money on CAD.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex flex-col min-h-screen bg-slate-50 text-slate-900 antialiased">
        <DisclaimerBanner />
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 space-y-2">
            <p>Idea2market &bull; Open Innovation Track, 13th Protocol: An AI Hackathon 2026</p>
            <p className="text-slate-400">
              Disclaimer: All generated requirements, BOMs, and budgets are preliminary AI drafts. Not an engineering certification.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
