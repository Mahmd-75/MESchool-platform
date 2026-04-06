import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

    MYSQL_HOST = os.environ.get("MYSQL_HOST", "db")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "academic_db")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600