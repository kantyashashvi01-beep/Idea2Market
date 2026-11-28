import io
from datetime import datetime, timezone
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

DISCLAIMER_TEXT = (
    "AI-generated preliminary draft. Not an engineering certification, not a quotation, "
    "and not a safety or regulatory approval. Have a qualified engineer review before "
    "building or selling anything."
)


class NumberedCanvas:
    """Canvas that adds disclaimer and page numbering to every page."""
    def __init__(self, canvas, doc):
        self.canvas = canvas
        self.doc = doc

    def draw_header_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(colors.HexColor("#dc2626"))
        canvas.drawCentredString(letter[0] / 2.0, letter[1] - 25, DISCLAIMER_TEXT)

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(54, 25, f"Idea2market Preliminary Report - Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        page_num = canvas.getPageNumber()
        canvas.drawRightString(letter[0] - 54, 25, f"Page {page_num}")
        canvas.restoreState()


class PDFBuilder:
    @staticmethod
    def generate_project_pdf(project_data: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=45,
            bottomMargin=45,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
        )

        h2_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold",
            spaceBefore=14,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )

        disclaimer_box_style = ParagraphStyle(
            "DisclaimerBox",
            parent=styles["Normal"],
            fontSize=8,
            leading=12,
            textColor=colors.HexColor("#991b1b"),
            fontName="Helvetica-Bold",
        )

        elements = []

        # Title and Domain
        title = project_data.get("title", "Hardware Planning Report")
        elements.append(Paragraph(f"Idea2market: {title}", title_style))
        elements.append(Spacer(1, 6))

        domain = project_data.get("domain", "Hardware Prototyping").replace("_", " ").title()
        meta_text = f"<b>Domain:</b> {domain} &nbsp;|&nbsp; <b>Status:</b> AI Draft (Preliminary)"
        elements.append(Paragraph(meta_text, body_style))
        elements.append(Spacer(1, 10))

        # Prominent Disclaimer Callout Box
        disclaimer_table = Table(
            [[Paragraph(f"<b>CRITICAL NOTICE:</b> {DISCLAIMER_TEXT}", disclaimer_box_style)]],
            colWidths=[letter[0] - 108],
        )
        disclaimer_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fee2e2")),
                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#dc2626")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ])
        )
        elements.append(disclaimer_table)
        elements.append(Spacer(1, 12))

        # Safety Banner if safety flag
        if project_data.get("safety_flag"):
            warn_msg = project_data.get("safety_warning") or "Safety-critical domain detected. Commercial readiness is blocked."
            safety_table = Table(
                [[Paragraph(f"<b>SAFETY-CRITICAL DOMAIN ALERT:</b> {warn_msg}", disclaimer_box_style)]],
                colWidths=[letter[0] - 108],
            )
            safety_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffedd5")),
                    ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#ea580c")),
                    ("PADDING", (0, 0), (-1, -1), 8),
                ])
            )
            elements.append(safety_table)
            elements.append(Spacer(1, 10))

        # Problem & Target Users
        elements.append(Paragraph("1. Concept Summary & Target Users", h2_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
        elements.append(Paragraph(f"<b>Idea Description:</b> {project_data.get('idea_text', '')}", body_style))
        elements.append(Spacer(1, 8))

        # Requirements
        requirements = project_data.get("requirements", [])
        if requirements:
            elements.append(Paragraph("2. Structured Requirements", h2_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
            req_data = [["Kind", "Priority", "Requirement Statement", "Source"]]
            for r in requirements:
                req_data.append([
                    r.get("kind", "").capitalize(),
                    r.get("priority", "").upper(),
                    Paragraph(r.get("text", ""), body_style),
                    r.get("source_type", "model_estimate"),
                ])

            req_table = Table(req_data, colWidths=[65, 55, letter[0] - 108 - 180, 60])
            req_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ])
            )
            elements.append(req_table)
            elements.append(Spacer(1, 12))

        # Subsystems & Architecture
        subsystems = project_data.get("subsystems", [])
        if subsystems:
            elements.append(Paragraph("3. Preliminary Architecture Subsystems", h2_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
            sub_data = [["Subsystem", "Purpose"]]
            for s in subsystems:
                sub_data.append([
                    s.get("name", ""),
                    Paragraph(s.get("purpose", ""), body_style),
                ])
            sub_table = Table(sub_data, colWidths=[150, letter[0] - 108 - 150])
            sub_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ])
            )
            elements.append(sub_table)
            elements.append(Spacer(1, 12))

        # BOM & Budget
        bom_data_obj = project_data.get("bom", {})
        bom_items = bom_data_obj.get("items", [])
        if bom_items:
            elements.append(Paragraph("4. Bill of Materials (Closed-World Catalogue)", h2_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
            elements.append(Paragraph("<i>Note: All prices are unverified placeholder estimates for order-of-magnitude budgeting.</i>", body_style))
            elements.append(Spacer(1, 4))

            table_rows = [["Cat ID", "Component Name", "Qty", "Price Range (INR)", "Role in Design"]]
            for item in bom_items:
                low = item.get("unit_low_inr", item.get("low_inr", 0))
                high = item.get("unit_high_inr", item.get("high_inr", 0))
                table_rows.append([
                    str(item.get("component_id", "-")),
                    Paragraph(item.get("name", ""), body_style),
                    str(item.get("quantity", 1)),
                    f"₹{int(low):,} - ₹{int(high):,}",
                    Paragraph(item.get("role_in_design", ""), body_style),
                ])

            bom_table = Table(table_rows, colWidths=[40, 180, 30, 100, letter[0] - 108 - 350])
            bom_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ])
            )
            elements.append(bom_table)
            elements.append(Spacer(1, 8))

            # Budget Totals Table
            grand_total = bom_data_obj.get("grand_total_inr", [0, 0])
            base_total = bom_data_obj.get("base_total_inr", [0, 0])
            budget_summary = [
                ["Component Base Subtotal", f"₹{int(base_total[0]):,} - ₹{int(base_total[1]):,}"],
            ]
            for al in bom_data_obj.get("allowances", []):
                budget_summary.append([
                    f"{al.get('label')} ({al.get('percent')}%)",
                    f"₹{int(al.get('amount_low_inr', 0)):,} - ₹{int(al.get('amount_high_inr', 0)):,}",
                ])
            budget_summary.append(["Estimated Grand Total Range", f"₹{int(grand_total[0]):,} - ₹{int(grand_total[1]):,}"])

            budget_table = Table(budget_summary, colWidths=[260, letter[0] - 108 - 260])
            budget_table.setStyle(
                TableStyle([
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("LINEBELOW", (0, -1), (-1, -1), 1.5, colors.HexColor("#0f172a")),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ])
            )
            elements.append(budget_table)
            elements.append(Spacer(1, 12))

        # Engineering Risks
        risks = project_data.get("risks", [])
        if risks:
            elements.append(Paragraph("5. Engineering Risks & Failure Modes", h2_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
            risk_rows = [["Risk / Failure Mode", "Severity", "Technical Rationale", "Expert Review"]]
            for r in risks:
                risk_rows.append([
                    Paragraph(r.get("title", ""), body_style),
                    r.get("severity", "").upper(),
                    Paragraph(r.get("reason", ""), body_style),
                    "REQUIRED" if r.get("needs_expert") else "Recommended",
                ])

            risk_table = Table(risk_rows, colWidths=[130, 55, letter[0] - 108 - 250, 65])
            risk_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ])
            )
            elements.append(risk_table)
            elements.append(Spacer(1, 12))

        # DFM & Readiness Findings
        rule_findings = project_data.get("rule_findings", [])
        if rule_findings:
            elements.append(Paragraph("6. Rule-Based DFM & Readiness Checks", h2_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
            finding_rows = [["Rule ID", "Status", "Evaluation Note"]]
            for rf in rule_findings:
                finding_rows.append([
                    rf.get("rule_id", ""),
                    rf.get("status", "").upper(),
                    Paragraph(rf.get("note", ""), body_style),
                ])
            finding_table = Table(finding_rows, colWidths=[70, 70, letter[0] - 108 - 140])
            finding_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ])
            )
            elements.append(finding_table)
            elements.append(Spacer(1, 12))

        # Facilities
        elements.append(Paragraph("7. Public Prototyping & Testing Facilities (India)", h2_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
        facility_info = (
            "<b>I-STEM Portal:</b> National web platform listing publicly funded research equipment across India (https://www.startupindia.gov.in/content/sih/en/i-stem.html)<br/>"
            "<b>T-Works (Hyderabad):</b> India's largest prototyping center with open access to rapid fabrication, PCB assembly, and mechanical tooling (https://tworks.telangana.gov.in/)"
        )
        elements.append(Paragraph(facility_info, body_style))

        # Build document with page decoration
        def on_page(canvas, d):
            NumberedCanvas(canvas, d).draw_header_footer(canvas, d)

        doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
