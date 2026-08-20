import sys
import os
from dotenv import load_dotenv

# Ensure apps/api directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from internal.core.db import run_migrations

if __name__ == "__main__":
    print("Executing database migrations...")
    try:
        run_migrations()
        print("Migrations executed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
