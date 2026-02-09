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
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from tabulate import tabulate
import pandas as pd
from reportlab.platypus import KeepTogether


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
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from tabulate import tabulate
import pandas as pd
import os


def register_safe_font():
    try:
        # 🟢 Use DejaVuSans font from Windows system (supports emoji & unicode)
        font_path = r"C:\Users\INDIA\Desktop\open_cv\computer_Vision\incidentreport\DejaVuSans.ttf"
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
    pdf_path = r"C:\Users\INDIA\Desktop\open_cv\computer_Vision\incidentreport\executive_summary_with_tabulate.pdf"
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
    story = []

    # ----------------------------------------------------------------------------
    # add title and report start and end date with Executive Summary
    # ----------------------------------------------------------------------------
    story.append(Paragraph("<b>Weekly Email Protection Summary</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Report generated on: 16 Oct 2025", styles["Normal"]))
    story.append(Paragraph("Report generated To: 09 Oct 2025", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Executive Summary", styles["Heading2"]))

    # Add Executive Summary table
    metrics_block = tabulate(df, headers="keys", tablefmt="pretty")  # excute summary
    story.append(Preformatted(metrics_block, styles["Monospace"]))
    story.append(Spacer(1, 20))

    # ----------------------------------------------------------------------------
    # Week Highlights
    # ----------------------------------------------------------------------------

    # weekly  Week Highlights using LLM
    story.append(Paragraph("<b>Week Highlights</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))

    # Split on double newlines and create paragraphs
    # for line in formatted_output.strip().split("\n\n"):
    #     if line.strip():
    #         p = Paragraph(line.strip(), styles["EmojiStyle"])
    #         story.append(p)
    #         story.append(Spacer(1, 10))

    for line in formatted_output.strip().split("\n"):
        line = line.strip()
        if line:
            p = Paragraph(line, styles["EmojiStyle"])
            story.append(p)
            story.append(Spacer(1, 6))

    # ----------------------------------------------------------------------------
    # WEEK-OVER-WEEK COMPARISON TABLE
    # ----------------------------------------------------------------------------
    story.append(Paragraph("📈 Week-over-Week Comparison", styles["Heading2"]))
    story.append(Spacer(1, 6))
    table_data = [df1.columns.to_list()] + df1.values.tolist()
    table = Table(table_data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    story.append(table)

    # ----------------------------------------------------------------------------
    # EMAIL TRAFFIC ANALYSIS SECTION
    # ----------------------------------------------------------------------------
    email_analysis_block = []

    # Heading + text
    email_analysis_block.append(
        Paragraph("📊 Email Traffic Analysis", styles["Heading2"])
    )
    email_analysis_block.append(Spacer(1, 6))
    email_analysis_block.append(
        Paragraph(
            f"Volume & Classification ({pie_data} emails processed)", styles["Normal"]
        )
    )
    email_analysis_block.append(Spacer(1, 10))
    if os.path.exists("piechart.png"):
        email_analysis_block.append(Image("piechart.png", width=300, height=300))
    else:
        email_analysis_block.append(
            Paragraph("📊 (Pie chart image not found — skipped)", styles["Normal"])
        )

    # ✅ Force heading + text + chart to stay on the same page
    story.append(KeepTogether(email_analysis_block))
    story.append(Spacer(1, 25))
    # # ----------------------------------------------------------------------------
    # # WEEK-OVER-WEEK COMPARISON TABLE
    # # ----------------------------------------------------------------------------
    # story.append(Paragraph("📈 Week-over-Week Comparison", styles["Heading2"]))
    # story.append(Spacer(1, 6))
    # table_data = [df1.columns.to_list()] + df1.values.tolist()
    # table = Table(table_data, hAlign="LEFT")
    # table.setStyle(
    #     TableStyle(
    #         [
    #             ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
    #             ("GRID", (0, 0), (-1, -1), 1, colors.black),
    #             ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    #             ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    #         ]
    #     )
    # )
    # story.append(table)

    # ----------------------------------------------------------------------------
    # THREAT TYPE DISTRIBUTION
    # ----------------------------------------------------------------------------

    email_analysis_block = []

    # Heading + text
    email_analysis_block.append(
        Paragraph("📊 hreat Type Distribution", styles["Heading2"])
    )
    email_analysis_block.append(Spacer(1, 6))
    email_analysis_block.append(
        Paragraph(f"Total malicious email count: {threat_data}", styles["Normal"])
    )

    email_analysis_block.append(Spacer(1, 10))
    if os.path.exists("email_threat_actions.png"):
        email_analysis_block.append(
            Image("email_threat_actions.png", width=500, height=250)
        )
    else:
        email_analysis_block.append(
            Paragraph("📊 (BAR chart image not found — skipped)", styles["Normal"])
        )

    story.append(KeepTogether(email_analysis_block))
    story.append(Spacer(1, 25))

    doc.build(story)
    print(f"✅ Table saved as PDF: {pdf_path}")
