import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")  # PostgreSQL in production
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "480"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
MAX_OPEN_BOOKINGS = int(os.getenv("MAX_OPEN_BOOKINGS", "3"))        # fair use
MAX_HOURS_PER_WEEK = float(os.getenv("MAX_HOURS_PER_WEEK", "12"))   # fair use
CHECKIN_EARLY_MINUTES = int(os.getenv("CHECKIN_EARLY_MINUTES", "60"))
LATE_GRACE_MINUTES = int(os.getenv("LATE_GRACE_MINUTES", "15"))
