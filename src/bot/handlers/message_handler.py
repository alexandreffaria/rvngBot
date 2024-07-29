from pywa import WhatsApp
from pywa.types import Message, CallbackButton
from bot.services.database import Database
from bot.handlers.email_handler import EmailHandler
from bot.handlers.order_handler import OrderHandler
from bot.handlers.state_handler import StateHandler
from config.settings import ME
import logging
import time

class MessageHandler:
    def __init__(self, whatsapp_client: WhatsApp):
        self.whatsapp_client = whatsapp_client
        self.database = Database()
        self.email_handler = EmailHandler(self.whatsapp_client, self.database)
        self.order_handler = OrderHandler(self.whatsapp_client, self.database)
        self.state_handler = StateHandler(self.whatsapp_client, self.database)

    def handle_message(self, message: Message):
        user_number = message.from_user.wa_id
        user_input = message.text.strip()
        timestamp = message.timestamp

        logging.info(f"Received message from {user_number}: {user_input}")

        # Get the user_id from the database
        user_id = self.database.insert_user(user_number)

        # Store the incoming message in the database
        self.database.insert_message(user_id, "user", user_number, "bot", ME, user_input, timestamp)

        # Check if the user wants to talk to a human
        if "atendente" in user_input.lower() or "humano" in user_input.lower() or "falar" in user_input.lower():
            self.state_handler.handle_human_request(user_number)
            self.database.set_state(user_id, 'state', None)
            return

        # Get the current state of the user
        current_state = self.database.get_state(user_id, 'state')
        logging.info(f"Current state for {user_number}: {current_state}")

        if current_state is None:
            self.state_handler.initial_interaction(user_number)
        elif current_state == 'awaiting_name':
            self.state_handler.handle_name(user_number, user_input)
        elif current_state == 'awaiting_email':
            self.email_handler.handle_email(user_number, user_input)
        elif current_state in ['awaiting_pd_rosa_quantity', 'awaiting_pd_azul_quantity', 'awaiting_pd_laranja_quantity', 'awaiting_pd_verde_quantity']:
            self.order_handler.handle_pd_quantity(user_number, current_state, user_input)
        elif current_state == 'awaiting_book_quantity':
            self.order_handler.handle_book_quantity(user_number, user_input)

    def handle_callback_button(self, callback_button: CallbackButton):
        user_number = callback_button.from_user.wa_id
        user_input = callback_button.data
        user_id = self.database.insert_user(user_number)

        logging.info(f"Received callback from {user_number}: {user_input}")

        # Store the incoming callback data as a message
        self.database.insert_message(user_id, "user", user_number, "bot", ME, user_input, time.time())

        # Get the current state of the user
        current_state = self.database.get_state(user_id, 'state')
        logging.info(f"Current state for {user_number}: {current_state}")

        if current_state == 'awaiting_role':
            self.state_handler.handle_role(user_number, user_input)
        elif current_state == 'awaiting_help_type':
            self.state_handler.handle_help_type(user_number, user_input)
        elif current_state == 'awaiting_pd_interest':
            self.order_handler.handle_pd_interest(user_number, user_input)
        elif current_state.startswith('awaiting_pd_'):
            self.order_handler.handle_pd_response(user_number, current_state, user_input)
        elif current_state == 'awaiting_book':
            self.order_handler.handle_book_response(user_number, user_input)