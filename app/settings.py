import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")