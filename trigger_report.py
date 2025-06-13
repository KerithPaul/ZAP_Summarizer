import psycopg2
import json
import datetime
from src.config import DB_CONFIG # Assumes your DB_CONFIG is defined here

def trigger_new_report(report_id, html_fragment_content):
    """
    Simulates inserting a new ZAP report (JSON structure) into the database
    and sending a NOTIFY signal.

    Args:
        report_id (int): The ID for the report.
        html_fragment_content (str): A string representing the HTML part
                                     that would typically be embedded in the ZAP JSON report.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True # Ensures changes are immediately committed
        cursor = conn.cursor()

        # Construct the full ZAP-like JSON structure.
        # In a real scenario, this would be the actual JSON output from ZAP.
        # Here, we're just creating a minimal dummy structure.
        results_data = {
            "id": report_id,
            "site": "https://example.com",
            "alerts": [
                {
                    "alertName": "Simulated Alert 1",
                    "risk": "High",
                    "confidence": "Medium",
                    "description": "This is a simulated high-risk alert.",
                    "solution": "Apply patches for simulated vulnerability."
                },
                {
                    "alertName": "Simulated Alert 2",
                    "risk": "Low",
                    "confidence": "High",
                    "description": "This is a simulated low-risk alert.",
                    "solution": "Review configuration."
                }
            ],
            "html_report_snippet": html_fragment_content, # Key to hold the HTML fragment
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Convert the Python dictionary to a JSON string for storage in the DB
        results_json_string = json.dumps(results_data)

        # 1. Insert/Update the report in zap_results table
        insert_sql = """
        INSERT INTO zap_results (id, scan_id, target_url, results, timestamp, processed, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            results = EXCLUDED.results,
            processed = EXCLUDED.processed,
            updated_at = EXCLUDED.updated_at;
        """
        scan_id = 1
        cursor.execute(
            insert_sql,
            (report_id, scan_id, "https://example.com", results_json_string, datetime.datetime.now(), False, datetime.datetime.now(), datetime.datetime.now())
        )
        print(f"✅ Report ID {report_id} data (simulated ZAP JSON) ensured in DB.")

        # 2. Send the NOTIFY signal
        notify_payload = json.dumps({"id": report_id})
        cursor.execute(f"NOTIFY new_report, '{notify_payload}';")
        print(f"🔔 NOTIFY new_report with payload '{notify_payload}' sent to DB.")

        cursor.close()
        conn.close()
        print("DB connection closed.")

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Configuration for your test ---
    test_report_id = 100 # Change this ID for each new test run if needed
   
    # This is a dummy HTML fragment that would typically be inside the ZAP JSON
    test_html_fragment = """
    <html>
        <body>
            <h1>Simulated ZAP Report - Section for ID {test_report_id}</h1>
            <p>This paragraph contains a <b>simulated HTML vulnerability</b>.</p>
            <ul>
                <li>Alert: Insecure Header</li>
                <li>Solution: Add Strict-Transport-Security header.</li>
            </ul>
        </body>
    </html>
    """.format(test_report_id=test_report_id)

    print(f"Attempting to trigger report ID: {test_report_id}")
    trigger_new_report(test_report_id, test_html_fragment)