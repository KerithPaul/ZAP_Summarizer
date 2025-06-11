import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

ollama_url = os.getenv("API_URL")
ollama_model = os.getenv("MODEL_NAME")

template_dir = os.path.join(os.path.dirname(__file__), "templates")
output_dir = os.path.join(os.path.dirname(__file__), "/var/reports")