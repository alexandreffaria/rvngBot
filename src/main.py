from pywa import WhatsApp
from pywa.types import Message, CallbackButton
from fastapi import FastAPI
import uvicorn
from config.settings import PHONE_ID, TOKEN, CALLBACK_URL, VERIFY_TOKEN, APP_ID, APP_SECRET
from bot.handlers.message_handler import MessageHandler
import logging

# Configure the logging level
logging.basicConfig(level=logging.INFO)

# Initialize the FastAPI application
fastapi_app = FastAPI()

# Initialize the WhatsApp client
wa = WhatsApp(
    phone_id=PHONE_ID,
    token=TOKEN,
    server=fastapi_app,
    callback_url=CALLBACK_URL,
    verify_token=VERIFY_TOKEN,
    app_id=APP_ID,
    app_secret=APP_SECRET,
)

# Initialize the message handler
message_handler = MessageHandler(wa)

# Define the on_message event
@wa.on_message()
def handle_message(client: WhatsApp, message: Message):
    message_handler.handle_message(message)

# Define the on_callback_button event
@wa.on_callback_button()
def handle_callback_button(client: WhatsApp, callback_button: CallbackButton):
    message_handler.handle_callback_button(callback_button)

# Run the FastAPI application
if __name__ == '__main__':
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8080)
