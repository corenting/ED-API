import os

from dotenv import load_dotenv

APP_VERSION = "3.0"

load_dotenv()

DEBUG_MODE = os.environ["DEBUG"] == "True"
WORKING_DIR = "/opt/ed-api/"
EDDN_RELAY = "tcp://eddn.edcd.io:9500"
EDDN_TIMEOUT = 600000
INARA_API_KEY = os.environ["INARA_API_KEY"]
DB_URI = os.environ["DATABASE_URI"]
FCM_API_KEY = os.environ["FCM_API_KEY"]
LOG_LEVEL = os.environ["LOG_LEVEL"] if "LOG_LEVEL" in os.environ else "INFO"
