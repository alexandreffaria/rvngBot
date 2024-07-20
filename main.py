from pywa import WhatsApp
from dotenv import load_dotenv
import os

load_dotenv()

PHONE_ID = os.getenv("PHONE_NUMBER_ID")
TOKEN = os.getenv("TEMPORARY_ACCESS_TOKEN")

wa = WhatsApp(
    phone_id=PHONE_ID,
    token=TOKEN
)

wa.send_message(
    to="31933006786",
    text="is nice to talk to you again"
)