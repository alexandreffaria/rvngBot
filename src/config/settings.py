import os
from dotenv import load_dotenv

load_dotenv()

PHONE_ID = os.getenv("PHONE_NUMBER_ID")
TOKEN = os.getenv("ACCESS_TOKEN")
CALLBACK_URL = os.getenv("CALLBACK_URL")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
APP_ID = int(os.getenv("APP_ID", "123456"))
APP_SECRET = os.getenv("APP_SECRET", "")
ME = os.getenv("DDF_NUMBER")
