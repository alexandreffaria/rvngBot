from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from pywa import WhatsApp
from pywa.types import Message, CallbackButton
from bot.handlers.message_handler import MessageHandler
import logging

# Configure the logging level
logging.basicConfig(level=logging.INFO)

# Initialize the FastAPI application
fastapi_app = FastAPI()

# Initialize the WhatsApp client
wa = WhatsApp(
    phone_id=os.getenv("PHONE_NUMBER_ID"),
    token=os.getenv("ACCESS_TOKEN"),
    server=fastapi_app,
    callback_url=os.getenv("CALLBACK_URL"),
    verify_token=os.getenv("VERIFY_TOKEN"),
    app_id=int(os.getenv("APP_ID", "123456")),
    app_secret=os.getenv("APP_SECRET"),
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

@fastapi_app.get("/")
def read_root():
    return {"message": "Hello World"}

@fastapi_app.post("/webhook")
async def webhook(request: Request):
    return await wa.handle_request(request)

def google_cloud_function(request):
    return JSONResponse(uvicorn.run(fastapi_app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080))))

# Run the FastAPI application
if __name__ == '__main__':
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8080)
