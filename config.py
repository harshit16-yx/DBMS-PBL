import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "bus-reservation-system-secret-key-2026")
    
    # MySQL Database Config
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME = os.getenv("DB_NAME", "bus_system")
    
    # Connection Pool Settings
    DB_POOL_NAME = "bus_pool"
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
    
    # App Settings
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
