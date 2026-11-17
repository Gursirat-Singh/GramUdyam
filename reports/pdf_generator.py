'''
PDF Export Generator using ReportLab.
Produces a structured, print-ready A4 PDF dossier containing business advisory,
financial assumptions vs projections, 3-scenario comparison, and formulas.
'''
from io import BytesIO
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_report_pdf_bytes(report_obj):
    '''Renders the given Report instance to a PDF byte stream using ReportLab.'''
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=report_obj.title,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DossierTitle",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1B4332"),
        spaceAfter=6,
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#2D6A4F"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodySmall",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        spaceAfter=4,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#555555"),
    )

    story = []
    story.append(Paragraph("AI-Driven Hyper-Local Business & Financial Dossier", title_style))
    story.append(Paragraph(f"<b>Report Title:</b> {report_obj.title}", body_style))
    story.append(Paragraph(f"<b>Report Type:</b> {report_obj.get_report_type_display()}", body_style))
    story.append(Paragraph(f"<b>Prepared For:</b> {report_obj.user.get_full_name()} ({report_obj.user.username})", body_style))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("1. Executive Summary", section_style))
    story.append(Paragraph(report_obj.executive_summary.replace("\n", "<br/>"), body_style))

    try:
        snap = json.loads(report_obj.snapshot_data or "{}")
    except Exception:
        snap = {}

    if report_obj.business_plan:
        bp = report_obj.business_plan
        story.append(Paragraph("2. Hyper-Local Business Profile & Advisory", section_style))
        bp_data = [
            ["Field", "Details"],
            ["Venture Title", bp.title],
            ["Location", f"{bp.village_or_town}, {bp.district}, {bp.state}"],
            ["Category", bp.get_business_category_display()],
            ["Investment Budget", f"INR {bp.investment_budget}"],
            ["Target Customers", bp.target_customers],
            ["Advisory Engine Source", bp.get_advisory_source_display()],
            ["Risk Indicator", bp.get_risk_level_display()],
        ]
        t_bp = Table(bp_data, colWidths=[50 * mm, 125 * mm])
        t_bp.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(t_bp)
        story.append(Spacer(1, 3 * mm))

    if report_obj.financial_plan:
        fp = report_obj.financial_plan
        story.append(Paragraph("3. Financial Structuring & Calculated Estimates", section_style))
        story.append(
            Paragraph(
                "<i>Note: User-entered assumptions are separated from calculated financial projections.</i>",
                disclaimer_style,
            )
        )
        fp_data = [
            ["Metric Category", "Item", "Amount / Value"],
            ["User Assumption", "Available Own Capital", f"INR {fp.available_capital}"],
            ["User Assumption", "Selling Price per Unit", f"INR {fp.estimated_selling_price_per_unit}"],
            ["User Assumption", "Expected Monthly Sales Volume", f"{fp.expected_monthly_sales_volume} units"],
            ["User Assumption", "Loan Amount & Interest Rate", f"INR {fp.loan_amount} @ {fp.annual_interest_rate}% p.a."],
            ["Calculated Estimate", "Total Startup Investment", f"INR {fp.total_startup_investment}"],
            ["Calculated Estimate", "Total Monthly Operating Cost", f"INR {fp.total_monthly_operating_cost}"],
            ["Calculated Estimate", "Estimated Monthly Revenue", f"INR {fp.estimated_monthly_revenue}"],
            ["Calculated Estimate", "Monthly Profit Before Tax/Interest (EBITDA)", f"INR {fp.estimated_monthly_ebitda}"],
            ["Calculated Estimate", "Monthly Loan EMI", f"INR {fp.monthly_loan_emi}"],
            ["Calculated Estimate", "Operating Profit Margin", f"{fp.profit_margin_percent}%"],
            ["Calculated Estimate", "Break-Even Volume", f"{fp.break_even_units or 'N/A'} units/month"],
            ["Calculated Estimate", "Payback Timeline", f"{fp.payback_period_months or 'N/A'} months"],
            ["Calculated Estimate", "Working Capital Requirement", f"INR {fp.working_capital_requirement}"],
        ]
        t_fp = Table(fp_data, colWidths=[45 * mm, 75 * mm, 55 * mm])
        t_fp.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D6A4F")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(t_fp)
        story.append(Spacer(1, 3 * mm))

    scenarios = snap.get("scenarios")
    if scenarios:
        story.append(Paragraph("4. Three-Scenario Sensitivity Comparison", section_style))
        s_rows = [
            ["Metric", "Conservative (-25% Vol)", "Expected (Baseline)", "Optimistic (+25% Vol)"],
            [
                "Monthly Revenue",
                f"INR {scenarios['conservative']['estimated_monthly_revenue']}",
                f"INR {scenarios['expected']['estimated_monthly_revenue']}",
                f"INR {scenarios['optimistic']['estimated_monthly_revenue']}",
            ],
            [
                "Monthly Operating Cost",
                f"INR {scenarios['conservative']['total_monthly_operating_cost']}",
                f"INR {scenarios['expected']['total_monthly_operating_cost']}",
                f"INR {scenarios['optimistic']['total_monthly_operating_cost']}",
            ],
            [
                "Monthly Operating Profit",
                f"INR {scenarios['conservative']['estimated_monthly_ebitda']}",
                f"INR {scenarios['expected']['estimated_monthly_ebitda']}",
                f"INR {scenarios['optimistic']['estimated_monthly_ebitda']}",
            ],
            [
                "Profit Margin (%)",
                f"{scenarios['conservative']['profit_margin_percent']}%",
                f"{scenarios['expected']['profit_margin_percent']}%",
                f"{scenarios['optimistic']['profit_margin_percent']}%",
            ],
        ]
        t_sc = Table(s_rows, colWidths=[45 * mm, 43 * mm, 43 * mm, 44 * mm])
        t_sc.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#40916C")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(t_sc)
        story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("5. Methodology & Legal Disclaimer", section_style))
    story.append(
        Paragraph(
            "All financial projections are calculated deterministically using Python Decimal arithmetic from user-supplied "
            "assumptions. Market guidance and government scheme summaries are provided for planning support only and do not "
            "constitute verified local market statistics or guaranteed loan/subsidy approval.",
            disclaimer_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()
