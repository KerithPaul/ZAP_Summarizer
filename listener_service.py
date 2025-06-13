import json
import time
import psycopg2
import psycopg2.extensions
import requests # <-- Added this import

from src.config import DB_CONFIG
# from src.pipeline_processed import process_report # <-- Removed this import, as n8n will handle processing

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/zap_reports" # <-- Ensure this is your EXACT n8n webhook URL


class ReportListener:
    def __init__(self):
        self.conn = self._connect_db()

    def _connect_db(self):
        """Establish DB connection with auto-reconnect"""
        while True:
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                conn.set_isolation_level(
                    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
                )
                print("Connected to PostgreSQL database.")
                return conn
            except psycopg2.OperationalError as e:
                print(f"DB connection failed: {e}. Retrying in 5s...")
                time.sleep(5)

    def start(self):
        print("🚀 Starting report listener...")
        cursor = self.conn.cursor()
        cursor.execute("LISTEN new_report;")
        print("Listening for 'new_report' notifications...")

        while True:
            try:
                self.conn.poll()
                while self.conn.notifies:
                    notify = self.conn.notifies.pop(0)
                    print(f"Received notification: Channel='{notify.channel}', Payload='{notify.payload}'")
                    self.handle_notification(json.loads(notify.payload))

            except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
                print(f"Connection lost: {e}. Reconnecting...")
                self.conn = self._connect_db()
                cursor = self.conn.cursor()
                cursor.execute("LISTEN new_report;")
                print("Re-established connection and listening for 'new_report' notifications.")

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from notification payload: {e}. Payload: {notify.payload}")

            except Exception as e:
                print(f"An unexpected error occurred in polling loop: {e}")

            time.sleep(0.1)

    def handle_notification(self, payload):
        report_id = payload['id']
        print(f"📥 New report detected: ID {report_id}")

        # Fetch JSON content from DB
        json_content = None
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT results FROM zap_results WHERE id = %s",
                    (report_id,)
                )
                result = cur.fetchone()
                if result:
                    json_content = result[0]
                    # Ensure json_content is a dictionary if it's retrieved as a JSON string
                    # psycopg2 might return JSON as string, or dict if adapter is used.
                    if isinstance(json_content, str):
                        json_content = json.loads(json_content)
                    print(f"Fetched report ID {report_id} from DB.")
                else:
                    print(f"No results found for report ID {report_id} in DB.")
                    return # Exit if no content found

        except psycopg2.Error as e:
            print(f"❌ DB error fetching report ID {report_id}: {e}")
            return
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding JSON content from DB for report ID {report_id}: {e}")
            return
        except Exception as e:
            print(f"An unexpected error occurred while fetching report ID {report_id}: {e}")
            return


        # Send to n8n webhook
        try:
            payload_to_send = { #Define the payload to send
                "report_id": report_id,
                "zap_report_data": json_content # <-- Sending full JSON content
            }
            print(f"Sending report ID {report_id} to n8n webhook: {N8N_WEBHOOK_URL}")
            print(f"DEBUG: JSON payload being sent to n8n: {json.dumps(payload_to_send, indent=2)}") # Debug print
            response = requests.post(
                N8N_WEBHOOK_URL,
                json={
                    "report_id": report_id,
                    "zap_report_data": json_content # <-- Corrected key name, sending full JSON here
                },
                timeout=60
            )
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

            if response.status_code == 200:
                print(f"✅ Report ID {report_id} successfully sent to n8n webhook.")
                try:
                    n8n_response_data = response.json()
                    print(f"N8N response: {json.dumps(n8n_response_data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"N8N returned non-JSON response: {response.text[:200]}...") # Print first 200 chars
            else:
                print(f"⚠️ N8N webhook returned status code {response.status_code}: {response.text}")


        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending report ID {report_id} to n8n webhook: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while sending to n8n: {e}")


        # Mark as processed
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "UPDATE zap_results SET processed = TRUE WHERE id = %s",
                    (report_id,)
                )
                print(f"Report ID {report_id} marked as processed in DB.")
        except psycopg2.Error as e:
            print(f"❌ DB error marking report ID {report_id} as processed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while marking report ID {report_id} processed: {e}")


if __name__ == "__main__":
    ReportListener().start()