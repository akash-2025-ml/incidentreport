from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from datetime import datetime, timezone, date, timedelta
import mysql.connector
import os, uvicorn
from dotenv import load_dotenv
from weekly_data import data_creation

load_dotenv()

app = FastAPI(title="Incident Summary API")


def get_tenant_database_name(tenant_id: str):
    """
    Get the actual tenant database name from organization_info table.

    Args:
        tenant_id: Tenant identifier

    Returns:
        str: Actual tenant database name from organization_info.tenant_db or fallback to tenant_id

    Raises:
        Exception: If database connection or query fails
    """
    try:
        # Connect to master database
        master_connection = mysql.connector.connect(
            host=os.environ.get("DATABASE_HOST"),
            port=int(os.environ.get("DATABASE_PORT")),
            user=os.environ.get("DATABASE_USERNAME"),
            password=os.environ.get("DATABASE_PASSWORD"),
            database=os.environ.get("MASTER_DB_NAME"),
        )

        mycursor = master_connection.cursor()
        # Get tenant_db from organization_info table using tenant_id
        mycursor.execute(
            "SELECT tenant_db FROM organization_info WHERE tenant_id = %s", (tenant_id,)
        )
        result = mycursor.fetchone()

        mycursor.close()
        master_connection.close()

        if result and result[0]:
            tenant_db_name = result[0]
            return tenant_db_name
        else:
            # Fallback to tenant_id for backward compatibility
            return tenant_id

    except Exception as e:
        # Fallback to tenant_id on error
        return tenant_id


# --- DB helpers ---
def get_mysql_conn(tenantid: str):
    return mysql.connector.connect(
        host=os.environ.get("DATABASE_HOST"),
        port=int(os.environ.get("DATABASE_PORT")),
        user=os.environ.get("DATABASE_USERNAME"),
        password=os.environ.get("DATABASE_PASSWORD"),
        database=get_tenant_database_name(tenantid),
    )


# --- Time parsing ---
def parse_dt_utc_naive(dt_str: str) -> datetime:
    if not dt_str:
        raise ValueError("Empty datetime string")
    # exact format first
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    # ISO fallback with Z/offset
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return (
            dt
            if dt.tzinfo is None
            else dt.astimezone(timezone.utc).replace(tzinfo=None)
        )
    except Exception as e:
        raise ValueError(f"Invalid datetime: {dt_str}") from e


# --- Models ---
class ThreatCounts(BaseModel):
    malicious: int
    spam: int
    warning: int
    safe: int


class ThreatPercentages(BaseModel):
    malicious: str
    spam: str
    warning: str
    safe: str


class Summary(BaseModel):
    totalEmailCount: int
    totalEmployeeCount: int
    avgEmailProcessingTime: str
    overallThreatCount: ThreatCounts
    threatPercentage: ThreatPercentages


class TopThreatSourceItem(BaseModel):
    senderDomain: str
    count: int
    threatType: str


class SummaryAndTopResponse(BaseModel):
    summary: Summary
    topThreatSources: List[TopThreatSourceItem]


# --- Queries ---
def compute_summary(conn, start_naive: datetime, end_naive: datetime) -> Summary:
    with conn.cursor(dictionary=True) as cur:
        cur.execute(
            """
            SELECT
              COUNT(*) AS total,
              SUM(CASE WHEN threat_type = 'malicious' THEN 1 ELSE 0 END) AS malicious,
              SUM(CASE WHEN threat_type = 'spam'      THEN 1 ELSE 0 END) AS spam,
              SUM(CASE WHEN threat_type = 'warning'   THEN 1 ELSE 0 END) AS warning,
              SUM(CASE WHEN threat_type = 'safe'      THEN 1 ELSE 0 END) AS safe
            FROM incident
            WHERE incident_time >= %s AND incident_time < %s
            """,
            (start_naive, end_naive),
        )
        row = cur.fetchone() or {}
        total = int(row.get("total") or 0)
        counts = {
            "malicious": int(row.get("malicious") or 0),
            "spam": int(row.get("spam") or 0),
            "warning": int(row.get("warning") or 0),
            "safe": int(row.get("safe") or 0),
        }

        # Employees (adjust to your schema; soft-fail to 0)
        try:
            cur.execute("SELECT COUNT(*) AS c FROM users")
            total_employees = int((cur.fetchone() or {}).get("c") or 0)
        except mysql.connector.Error:
            total_employees = 0

        avg_str = "N/A"  # replace with processed_at AVG if you have it

    def pct(n: int, d: int) -> str:
        return f"{(n / d * 100):.0f}%" if d > 0 else "0%"

    return Summary(
        totalEmailCount=total,
        totalEmployeeCount=total_employees,
        avgEmailProcessingTime=avg_str,
        overallThreatCount=ThreatCounts(**counts),
        threatPercentage=ThreatPercentages(
            malicious=pct(counts["malicious"], total),
            spam=pct(counts["spam"], total),
            warning=pct(counts["warning"], total),
            safe=pct(counts["safe"], total),
        ),
    )


def _fetch_top_threat_sources(
    conn, start_naive: datetime, end_naive: datetime, limit: int = 10
) -> List[Dict[str, Any]]:
    with conn.cursor(dictionary=True) as cur:
        cur.execute(
            """
            SELECT
              COALESCE(NULLIF(TRIM(sender_domain), ''), '(unknown)')   AS sender_domain,
              COALESCE(NULLIF(TRIM(threat_type), ''), '(unspecified)') AS threat_type,
              COUNT(*) AS cnt
            FROM incident
            WHERE incident_time >= %s AND incident_time < %s   -- end exclusive to match summary
            GROUP BY sender_domain, threat_type
            ORDER BY cnt DESC
            LIMIT %s
            """,
            (start_naive, end_naive, int(limit)),
        )
        rows = cur.fetchall() or []

    return [
        {
            "senderDomain": r["sender_domain"],
            "count": int(r["cnt"] or 0),
            "threatType": r["threat_type"],
        }
        for r in rows
    ]


# --- Endpoint ---
@app.get("/incidents/summary", response_model=SummaryAndTopResponse)
def incidents_summary(
    start_time: str = Query(..., description="Start 'YYYY-MM-DD HH:MM:SS' or ISO"),
    end_time: str = Query(..., description="End (exclusive) same format"),
    top_limit: int = Query(10, ge=1, le=500, description="Max top threat source rows"),
):
    try:
        start_naive = parse_dt_utc_naive(start_time)
        end_naive = parse_dt_utc_naive(end_time)
        if end_naive <= start_naive:
            raise HTTPException(
                status_code=400, detail="end_time must be greater than start_time"
            )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

    try:
        conn = get_mysql_conn(os.environ.get("TENANT_ID"))
        try:
            summary = compute_summary(conn, start_naive, end_naive)
            top_sources = _fetch_top_threat_sources(
                conn, start_naive, end_naive, top_limit
            )
        finally:
            conn.close()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {e.msg}")

    return {"summary": summary, "topThreatSources": top_sources}


# if __name__ == "__main__":
#     # change 'app_file_name' to your actual filename without .py (or just run: uvicorn this_file:app --reload)
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
import threading
import time
import requests


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False, log_level="error")


server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Wait for FastAPI server to start
print("⏳ Starting FastAPI server...")
time.sleep(3)

# ---------------------------
# Client sends request
# ---------------------------
url = "http://127.0.0.1:8001/incidents/summary"

end_time = input("Enter your Start date in the Format of Year-Month-Date")
edt = "{0} 00:00:00".format(end_time)
print(edt)

start_time = input("Enter your End date in the Format of Year-Month-Date")
sdt = "{0} 00:00:00".format(start_time)
print(sdt)

Days = int(input("Enter How many days data you want For comparison."))
week_sd = datetime.strptime(sdt, "%Y-%m-%d %H:%M:%S")
week_ld = week_sd - timedelta(days=Days)

params = {
    "start_time": sdt,
    "end_time": edt,
}

week_com = {
    "start_time": week_ld,
    "end_time": week_sd,
}

try:
    print("🔍 Sending request to FastAPI server...")
    response = requests.get(url, params=params, timeout=10)
    week_response = requests.get(url, params=week_com, timeout=10)

    if response.status_code == 200:
        print("✅ Response received successfully:")
        print(response.json())
        print("week = ", week_response.json())
        data_creation(response.json(), week_response.json())
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"⚠️ Request failed: {e}")
