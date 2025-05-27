
import os


# db
DB_URI = os.getenv("db_uri", default="127.0.0.1")


# app
APP_HOST = os.getenv("app_host", default="0.0.0.0")
APP_PORT = int(os.getenv("app_port", default=8000))


# logs
LOGS_LEVEL = "DEBUG"


# resources
RESOURCES_DIR = "resources"
LOGS_DIR = os.path.join(RESOURCES_DIR, "logs")
