import json
import pandas as pd
from tabulate import tabulate
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for automated plotting
import matplotlib.pyplot as plt

# from report import pdf_creater
from pro_report import pdf_creater
from weekly_highlights import summary_genrator


def Executive_Summary(a1, formatted_output, pie_data, threat_data, df1, a3):
    df = pd.DataFrame(list(a1.items()), columns=["PROTECTION METRICS", "count"])
    pdf_creater(df, formatted_output, pie_data, threat_data, df1)


def safe_get(value, default=0):
    """Return value if valid, otherwise return default. Handles None and NaN."""
    if value is None:
        return default
    if isinstance(value, float) and pd.isna(value):
        return default
    return value


def data_creation(a, previous_week):
    "create a data for pot the pie chart and table"
    a1 = {}
    a1["Total Email"] = safe_get(a["summary"]["totalEmailCount"], 0)
    a1["Employees Protected"] = safe_get(a["summary"]["totalEmployeeCount"], 0)
    a1["Avg Processing Time"] = safe_get(a["summary"]["avgEmailProcessingTime"], 0)
    a1["Threats Blocked"] = safe_get(a["summary"]["overallThreatCount"]["malicious"], 0)
    pie_data = a1["Total Email"]
    threat_data = a["summary"]["overallThreatCount"]["malicious"]

    # week comparison data - helper function for clean calculation
    def calc_week_comparison(current_val, prev_val):
        """Calculate [current, previous, % change] with safe division."""
        current = safe_get(current_val, 0)
        prev = safe_get(prev_val, 0)
        if prev == 0:
            change = (current - prev) * 100 / 1 if current != 0 else 0
        else:
            change = (current - prev) * 100 / prev
        return [current, prev, change]

    a3 = {}
    a3["Malicious"] = calc_week_comparison(
        a["summary"]["overallThreatCount"].get("malicious"),
        previous_week["summary"]["overallThreatCount"].get("malicious")
    )
    a3["spam"] = calc_week_comparison(
        a["summary"]["overallThreatCount"].get("spam"),
        previous_week["summary"]["overallThreatCount"].get("spam")
    )
    a3["warning"] = calc_week_comparison(
        a["summary"]["overallThreatCount"].get("warning"),
        previous_week["summary"]["overallThreatCount"].get("warning")
    )
    a3["safe"] = calc_week_comparison(
        a["summary"]["overallThreatCount"].get("safe"),
        previous_week["summary"]["overallThreatCount"].get("safe")
    )
    print("a3 === ", a3)
    ######################################################################################
    a2 = {}
    a2 = a["summary"]["overallThreatCount"]

    print("=" * 50)
    print("DEBUG: Raw overallThreatCount data:")
    print(f"  a2 = {a2}")
    print(f"  a2 type = {type(a2)}")

    names = list(a2.keys())
    salaries = list(a2.values())

    print(f"  names = {names}")
    print(f"  salaries (raw) = {salaries}")
    print(f"  salaries types = {[type(v) for v in salaries]}")

    # Handle NaN, None, or all-zero values for pie chart
    salaries = [0 if (v is None or (isinstance(v, float) and pd.isna(v))) else v for v in salaries]

    print(f"  salaries (cleaned) = {salaries}")
    print(f"  sum(salaries) = {sum(salaries)}")
    print("=" * 50)

    plt.figure(figsize=(3.5, 3.5))

    # Only create pie chart if there's valid data (sum > 0)
    if sum(salaries) > 0:
        plt.pie(salaries, labels=names, autopct="%1.1f%%", startangle=140)
        plt.title("Distribution of Emails")
    else:
        # Show actual counts when all values are 0
        plt.axis('off')
        plt.title("Distribution of Emails", fontsize=12, fontweight='bold', pad=20)

        # Build text showing each category with its count
        count_text = "Email Counts:\n\n"
        for name, value in zip(names, salaries):
            count_text += f"{name.capitalize()}: {value}\n"
        count_text += f"\nTotal: {sum(salaries)}"

        plt.text(0.5, 0.5, count_text, ha='center', va='center', fontsize=11,
                 transform=plt.gca().transAxes,
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f0f0', edgecolor='#cccccc', alpha=0.9))

    plt.savefig("piechart.png")
    plt.close()  # Close the figure to free memory and prevent display
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
    # Fill NaN values with 0 before converting to int
    df1["Current Week"] = df1["Current Week"].fillna(0).astype(int)
    df1["Last Week"] = df1["Last Week"].fillna(0).astype(int)
    df1["Change"] = df1["Change"].fillna(0)
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

    plt.tight_layout()  # Apply layout adjustments BEFORE saving
    plt.savefig("email_threat_actions.png", bbox_inches="tight", dpi=300)
    plt.close()  # Close the figure to free memory and prevent display

    ####################################################################################33

    Executive_Summary(a1, formatted_output, pie_data, threat_data, df1, a3)
