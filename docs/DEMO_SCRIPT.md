# Idea2market: 4-Minute Hackathon Demo Script

**Context**: 13th Protocol: An AI Hackathon 2026 (Open Innovation Track)
**Demo Concept**: *"An affordable autonomous agricultural robot for small Indian farmers"*

---

## Minute 0:00 - 0:45: The Problem & The Pre-CAD Gap
- **Opening**: "Hardware prototyping in India has a documented discovery and planning bottleneck. Non-engineers have great concepts but don't know what components they need, what realistic budget ranges to expect, or how to prepare a brief for prototyping facilities like T-Works or I-STEM."
- **Positioning**: "Idea2market is not an autonomous certifier or a manufacturing marketplace. It is an **AI Product Engineer for non-engineers** that generates a structured, preliminary engineering draft before you spend money on CAD or prototypes."

---

## Minute 0:45 - 1:45: Concept Input & Technical Clarification
- Open the Idea2market UI.
- Click **Start Planning Hardware** &rarr; click **Load Example Agri-Rover Prompt**.
- Show the plain-language prompt describing row navigation, weed detection, and micro-spraying.
- Click **Proceed to Technical Clarification**.
- Explain: "The system asks up to 5 high-impact questions on terrain, battery runtime, and payload weight because hardware cannot be specified in a vacuum."
- Enter answers and click **Generate Engineering Plan**.

---

## Minute 1:45 - 3:00: The Generated Plan & Closed-World BOM
- Show the generation progress bar.
- Land on the Report Workspace:
  1. **Mandatory Disclaimer**: Point out the persistent warning banner at the top of every page and report: *"AI-generated preliminary draft. Not an engineering certification."*
  2. **Requirements & Subsystems**: Show the clean separation into functional requirements, constraints, and physical subsystems.
  3. **Closed-World BOM**: "Notice that every single item references an actual catalogue ID from our database—motors, drivers, compute, GPS, battery. No hallucinated part numbers."
  4. **Unverified Placeholder Badges**: Highlight that all seed prices are explicitly badged as unverified placeholder estimates.
  5. **Deterministic Arithmetic Demo**: Change a motor quantity from 2 to 4 or edit the contingency allowance from 15% to 20%. Watch the grand total budget recalculate instantly in Python code.

---

## Minute 3:00 - 3:45: DFM Readiness, Safety Gating & Facility Links
- Click the **Engineering Risks** tab: Show the failure modes (e.g. soil grit in planetary gearboxes, heat in sealed IP65 boxes) with mandatory rationale and *"Needs Qualified Engineer Review"* badges.
- Click **DFM & Readiness Checklist**: Point out the pass/warn findings evaluated by our 20+ rule YAML engine.
- Click **Facilities** tab: Show direct links to national public facilities: I-STEM shared equipment portal and T-Works Hyderabad.
- Click **Download PDF Report**: Show the downloaded professional ReportLab PDF complete with running disclaimer headers and footers.

---

## Minute 3:45 - 4:00: Evaluation Slide & Conclusion
- Show the `eval/results.md` benchmark slide: 100% closed-world BOM resolvability, 100% safety domain detection, and deterministic cost math.
- **Closing**: "Idea2market turns plain language hardware ideas into transparent, reviewable engineering plans and budgets before you build."
