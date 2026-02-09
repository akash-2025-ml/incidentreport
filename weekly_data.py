import json
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

# from report import pdf_creater
from pro_report import pdf_creater
from weekly_highlights import summary_genrator


def Executive_Summary(a1, formatted_output, pie_data, threat_data, df1, a3):
    df = pd.DataFrame(list(a1.items()), columns=["PROTECTION METRICS", "count"])
    pdf_creater(df, formatted_output, pie_data, threat_data, df1)


def data_creation(a, previous_week):
    "create a data for pot the pie chart and table"
    a1 = {}
    a1["Total Email"] = a["summary"]["totalEmailCount"]
    a1["Employees Protected"] = a["summary"]["totalEmployeeCount"]
    a1["Avg Processing Time"] = a["summary"]["avgEmailProcessingTime"]
    a1["Threats Blocked"] = a["summary"]["overallThreatCount"]["malicious"]
    pie_data = a1["Total Email"]
    threat_data = a["summary"]["overallThreatCount"]["malicious"]

    # week comparison data
    a3 = {}
    if previous_week["summary"]["overallThreatCount"]["malicious"] == 0:
        a3["Maclicius"] = [
            a["summary"]["overallThreatCount"]["malicious"],
            previous_week["summary"]["overallThreatCount"]["malicious"],
            (
                a["summary"]["overallThreatCount"]["malicious"]
                - previous_week["summary"]["overallThreatCount"]["malicious"]
            )
            * 100
            / 1,
        ]
    else:
        a3["Maclicius"] = [
            a["summary"]["overallThreatCount"]["malicious"],
            previous_week["summary"]["overallThreatCount"]["malicious"],
            (
                a["summary"]["overallThreatCount"]["malicious"]
                - previous_week["summary"]["overallThreatCount"]["malicious"]
            )
            * 100
            / previous_week["summary"]["overallThreatCount"]["malicious"],
        ]
    if previous_week["summary"]["overallThreatCount"]["spam"] == 0:
        a3["spam"] = [
            a["summary"]["overallThreatCount"]["spam"],
            previous_week["summary"]["overallThreatCount"]["spam"],
            (
                a["summary"]["overallThreatCount"]["spam"]
                - previous_week["summary"]["overallThreatCount"]["spam"]
            )
            * 100
            / 1,
        ]
    else:
        a3["spam"] = [
            a["summary"]["overallThreatCount"]["spam"],
            previous_week["summary"]["overallThreatCount"]["spam"],
            (
                a["summary"]["overallThreatCount"]["spam"]
                - previous_week["summary"]["overallThreatCount"]["spam"]
            )
            * 100
            / previous_week["summary"]["overallThreatCount"]["spam"],
        ]
    if previous_week["summary"]["overallThreatCount"]["warning"] == 0:
        a3["warning"] = [
            a["summary"]["overallThreatCount"]["warning"],
            previous_week["summary"]["overallThreatCount"]["warning"],
            (
                a["summary"]["overallThreatCount"]["warning"]
                - previous_week["summary"]["overallThreatCount"]["warning"]
            )
            * 100
            / 1,
        ]
    else:
        a3["warning"] = [
            a["summary"]["overallThreatCount"]["warning"],
            previous_week["summary"]["overallThreatCount"]["warning"],
            (
                a["summary"]["overallThreatCount"]["warning"]
                - previous_week["summary"]["overallThreatCount"]["warning"]
            )
            * 100
            / previous_week["summary"]["overallThreatCount"]["warning"],
        ]
    if previous_week["summary"]["overallThreatCount"]["safe"] == 0:
        a3["safe"] = [
            a["summary"]["overallThreatCount"]["safe"],
            previous_week["summary"]["overallThreatCount"]["safe"],
            (
                a["summary"]["overallThreatCount"]["safe"]
                - previous_week["summary"]["overallThreatCount"]["safe"]
            )
            * 100
            / 1,
        ]
    else:
        a3["safe"] = [
            a["summary"]["overallThreatCount"]["safe"],
            previous_week["summary"]["overallThreatCount"]["safe"],
            (
                a["summary"]["overallThreatCount"]["safe"]
                - previous_week["summary"]["overallThreatCount"]["safe"]
            )
            * 100
            / previous_week["summary"]["overallThreatCount"]["safe"],
        ]
    print("a3 === ", a3)
    ######################################################################################
    a2 = {}
    a2 = a["summary"]["overallThreatCount"]

    names = list(a2.keys())
    salaries = list(a2.values())

    plt.figure(figsize=(3.5, 3.5))
    plt.pie(salaries, labels=names, autopct="%1.1f%%", startangle=140)

    plt.title("Distribution of Emails")
    plt.savefig("piechart.png")
    ################################################################################
    a4 = {
        "link_click": 21,
        "credential_request": 20,
        "legal_threat": 20,
        "document_download": 20,
    }

    formatted_output = summary_genrator(a1, a2, a4, a3)

    # formatted_output = """
    # ✅ High System Efficacy: The email security gateway processed 1,000 emails with an average speed of 2.2 seconds while blocking 400 distinct threats.

    # ⚠️ Elevated Threat Volume: 40% of all inbound email traffic was malicious, indicating a high-intensity threat environment.

    # 🔍 Dominant Threat Vectors: Phishing and credential harvesting were the primary attack methods observed.

    # 📈 Targeted Employee Impact: The system shielded 50 employees from an average of 8 malicious emails each.

    # 💡 Recommendation: Deploy targeted awareness training focusing on link verification and credential safety.
    #  """

    #############################################################################################
    # week summary
    df1 = pd.DataFrame(
        a3, index=["Current Week", "Last Week", "Change"]
    ).T.reset_index()
    df1["Current Week"] = df1["Current Week"].astype(int)
    df1["Last Week"] = df1["Last Week"].astype(int)
    df1 = df1.rename(columns={"index": "Category"})

    # Add arrows based on sign
    def format_change(x):
        if x > 0:
            return f"{x:.2f}% ▲"
        elif x < 0:
            return f"{x:.2f}% ▼"
        else:
            return f"{x:.2f}%"

    df1["Change"] = df1["Change"].apply(format_change)

    ##########################################################################################
    # Corrected dictionary
    # a4 = {'link_click': 140, 'credential_request': 50, 'document_download': 30}

    # Extract data
    categories = list(a4.keys())
    counts = list(a4.values())

    # Bar positions and width
    x = range(len(categories))
    bar_width = 0.3  # thinner bars

    # Plot bars
    plt.figure(figsize=(7, 4))
    plt.bar(x, counts, width=bar_width, color="skyblue")

    # Add labels and title
    plt.xlabel("Action Type")
    plt.ylabel("Count")
    plt.title("Email Threat Action Counts")
    plt.xticks(x, categories)

    # Add count numbers on top
    for i, v in enumerate(counts):
        plt.text(i, v + 2, str(v), ha="center", fontweight="bold")

    plt.savefig("email_threat_actions.png", bbox_inches="tight", dpi=300)
    plt.tight_layout()
    plt.show()

    ####################################################################################33

    Executive_Summary(a1, formatted_output, pie_data, threat_data, df1, a3)
