import json
import time
import psycopg2
import psycopg2.extensions
from src.config import DB_CONFIG
from src.pipeline_processed import process_report

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
                return conn
            except psycopg2.OperationalError:
                print("DB connection failed. Retrying in 5s...")
                time.sleep(5)
               
    def start(self):
        print("🚀 Starting report listener...")
        cursor = self.conn.cursor()
        cursor.execute("LISTEN new_report;")
       
        while True:
            try:
                self.conn.poll()
                while self.conn.notifies:
                    notify = self.conn.notifies.pop(0)
                    self.handle_notification(json.loads(notify.payload))
                   
            except (psycopg2.InterfaceError, psycopg2.OperationalError):
                print("Connection lost. Reconnecting...")
                self.conn = self._connect_db()
                cursor = self.conn.cursor()
                cursor.execute("LISTEN new_report;")
               
            time.sleep(0.1)
           
    def handle_notification(self, payload):
        report_id = payload['id']
        print(f"📥 New report detected: ID {report_id}")
       
        # Fetch HTML from DB
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT results FROM zap_results WHERE id = %s",
                (report_id,)
            )
            json_content = cur.fetchone()[0]
            if isinstance(json_content,dict):
                json_content = json.dumps(json_content)
       
        # Process report (PDF generation)
        process_report(report_id, json_content)
       
        # Mark as processed
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE zap_results SET processed = TRUE WHERE id = %s",
                (report_id,)
            )

if __name__ == "__main__":
    ReportListener().start()
