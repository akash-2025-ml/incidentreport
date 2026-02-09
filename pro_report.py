from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted,
    Image,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from tabulate import tabulate
import pandas as pd
import os


def register_safe_font():
    try:
        # Use DejaVuSans font (supports emoji & unicode)
        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font not found at {font_path}")
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
        return "DejaVuSans"
    except Exception as e:
        print("⚠️ Falling back to UnicodeCIDFont due to:", e)
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        return "STSong-Light"


FONT_NAME = register_safe_font()


def pdf_creater(df, formatted_output, pie_data, threat_data, df1):
    # ----------------------------------------------------------------------------
    # PDF SETUP
    # ----------------------------------------------------------------------------
    pdf_path = os.path.join(os.path.dirname(__file__), "executive_summary_with_tabulate.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()

    # Add custom styles
    styles.add(
        ParagraphStyle(name="Monospace", fontName="Courier", fontSize=9, leading=12)
    )
    styles.add(
        ParagraphStyle(name="EmojiStyle", fontName=FONT_NAME, fontSize=11, leading=15)
    )
    styles["Title"].fontSize = 20
    styles["Title"].leading = 24
    styles["Title"].alignment = 1  # Center align title
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 12
    styles["Heading2"].fontSize = 14
    styles["Heading2"].spaceAfter = 8
    styles["Heading2"].spaceBefore = 12

    story = []

    # ----------------------------------------------------------------------------
    # TITLE SECTION - Better spacing and alignment
    # ----------------------------------------------------------------------------
    story.append(Paragraph("<b>Weekly Email Protection Summary</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    # Date information centered
    date_style = ParagraphStyle(
        "DateStyle", parent=styles["Normal"], alignment=1  # Center alignment
    )
    story.append(Paragraph("Report Period: 09 Oct 2025 - 16 Oct 2025", date_style))
    story.append(Paragraph("Report Generated: 16 Oct 2025", date_style))
    story.append(Spacer(1, 30))

    # ----------------------------------------------------------------------------
    # EXECUTIVE SUMMARY - Keep together
    # ----------------------------------------------------------------------------
    exec_summary_content = []
    exec_summary_content.append(
        Paragraph("<b>Executive Summary</b>", styles["Heading2"])
    )
    exec_summary_content.append(Spacer(1, 10))

    # Executive Summary table with better formatting
    metrics_block = tabulate(df, headers="keys", tablefmt="pretty")
    exec_summary_content.append(Preformatted(metrics_block, styles["Monospace"]))

    story.append(KeepTogether(exec_summary_content))
    story.append(Spacer(1, 30))

    # ----------------------------------------------------------------------------
    # WEEK HIGHLIGHTS - Better paragraph spacing
    # ----------------------------------------------------------------------------
    highlights_content = []
    highlights_content.append(Paragraph("<b>Week Highlights</b>", styles["Heading2"]))
    highlights_content.append(Spacer(1, 10))

    # Process highlights with better spacing
    highlight_lines = []
    for line in formatted_output.strip().split("\n"):
        line = line.strip()
        if line:
            p = Paragraph(line, styles["EmojiStyle"])
            highlight_lines.append(p)
            highlight_lines.append(Spacer(1, 8))

    # Remove last spacer
    if highlight_lines and isinstance(highlight_lines[-1], Spacer):
        highlight_lines.pop()

    highlights_content.extend(highlight_lines)
    story.append(KeepTogether(highlights_content))
    story.append(Spacer(1, 30))

    # ----------------------------------------------------------------------------
    # EMAIL TRAFFIC ANALYSIS - Keep chart with title
    # ----------------------------------------------------------------------------
    traffic_analysis_content = []
    traffic_analysis_content.append(
        Paragraph("📊 Email Traffic Analysis", styles["Heading2"])
    )
    traffic_analysis_content.append(Spacer(1, 10))
    traffic_analysis_content.append(
        Paragraph(
            f"<b>Volume & Classification</b> ({pie_data:,} emails processed)",
            styles["Normal"],
        )
    )
    traffic_analysis_content.append(Spacer(1, 15))

    if os.path.exists("piechart.png"):
        # Center the image
        img = Image("piechart.png", width=350, height=350)
        img.hAlign = "CENTER"
        traffic_analysis_content.append(img)
    else:
        traffic_analysis_content.append(
            Paragraph("📊 (Pie chart image not found — skipped)", styles["Normal"])
        )

    story.append(KeepTogether(traffic_analysis_content))
    story.append(Spacer(1, 30))

    # ----------------------------------------------------------------------------
    # WEEK-OVER-WEEK COMPARISON - Better table formatting
    # ----------------------------------------------------------------------------
    comparison_content = []
    comparison_content.append(
        Paragraph("📈 Week-over-Week Comparison", styles["Heading2"])
    )
    comparison_content.append(Spacer(1, 10))

    # Create better formatted table
    table_data = [df1.columns.to_list()] + df1.values.tolist()

    # Calculate column widths based on content
    col_count = len(table_data[0])
    available_width = doc.width
    col_widths = [available_width * 0.3] + [
        (available_width * 0.7) / (col_count - 1)
    ] * (col_count - 1)

    table = Table(table_data, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                # Header styling
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                # Data cells
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    comparison_content.append(table)

    story.append(KeepTogether(comparison_content))
    story.append(Spacer(1, 30))

    # ----------------------------------------------------------------------------
    # THREAT TYPE DISTRIBUTION - Keep together with better spacing
    # ----------------------------------------------------------------------------
    threat_content = []
    threat_content.append(Paragraph("📊 Threat Type Distribution", styles["Heading2"]))
    threat_content.append(Spacer(1, 10))
    threat_content.append(
        Paragraph(
            f"<b>Total malicious emails detected:</b> {threat_data:,}", styles["Normal"]
        )
    )
    threat_content.append(Spacer(1, 15))

    if os.path.exists("email_threat_actions.png"):
        # Better sized bar chart
        img = Image("email_threat_actions.png", width=450, height=250)
        img.hAlign = "CENTER"
        threat_content.append(img)
    else:
        threat_content.append(
            Paragraph("📊 (Bar chart image not found — skipped)", styles["Normal"])
        )

    story.append(KeepTogether(threat_content))
    story.append(Spacer(1, 20))

    # Build the PDF
    doc.build(story)
    print(f"✅ Table saved as PDF: {pdf_path}")
