import os
from dotenv import load_dotenv

load_dotenv()

# General config
DEBUG_MODE = bool(os.environ['DEBUG'])
APP_VERSION = '2.4.1'
WORKING_DIR = '/opt/ed-api/'

# EDDN
EDDN_RELAY = 'tcp://eddn.edcd.io:9500'
EDDN_TIMEOUT = 600000

# Inara
INARA_API_KEY = os.environ['INARA_API_KEY']

# Database
DB_URI = 'sqlite:///edapi.db'
if not DEBUG_MODE:
    DB_URI = os.environ['PROD_DB']

# FCM
FCM_API_KEY = os.environ['FCM_API_KEY']
