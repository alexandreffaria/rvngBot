from pywa import WhatsApp
from pywa.types import Message, CallbackData
from fastapi import FastAPI
import uvicorn
from config.settings import PHONE_ID, TOKEN, CALLBACK_URL, VERIFY_TOKEN, APP_ID, APP_SECRET, ME
from bot.message_handler import MessageHandler

fastapi_app = FastAPI()

wa = WhatsApp(
    phone_id=PHONE_ID,
    token=TOKEN,
    server=fastapi_app,
    callback_url=CALLBACK_URL,
    verify_token=VERIFY_TOKEN,
    app_id=APP_ID,
    app_secret=APP_SECRET,
)

message_handler = MessageHandler(wa)

@wa.on_message()
async def handle_message(client: WhatsApp, message: Message):
    message_handler.handle_message(message)

@wa.on_callback_button()
async def handle_callback(client: WhatsApp, callback: CallbackData):
    message_handler.handle_callback(callback)

if __name__ == '__main__':
    uvicorn.run(fastapi_app, port=8080)