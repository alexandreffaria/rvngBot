from email_validator import validate_email, EmailNotValidError
from pywa.types import Button
from config.settings import ME
import time

class EmailHandler:
    def __init__(self, whatsapp_client, database):
        self.whatsapp_client = whatsapp_client
        self.database = database

    def handle_email(self, user_number, user_input):
        message = "Qual sua área de atuação?"
        is_valid, result = self.validate_email_address(user_input)
        user_id = self.database.insert_user(user_number)
        if is_valid:
            self.database.update_user(user_id, email=result)
            self.whatsapp_client.send_message(
                to=user_number,
                text=message,
                buttons=[
                    Button("Dentista", callback_data="Dentista"),
                    Button("Lojista", callback_data="Lojista"),
                    Button("Outros", callback_data="Outros"),
                ]
            )
            self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
            self.database.set_state(user_id, 'state', 'awaiting_role')
        else:
            message = "Hm, isso não parece um email válido. 🤔 Vamos tentar de novo?"
            self.whatsapp_client.send_message(user_number, message)
            self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
            self.database.set_state(user_id, 'state', 'awaiting_email')

    def validate_email_address(self, email):
        try:
            v = validate_email(email)
            email = v["email"]
            return True, email
        except EmailNotValidError as e:
            return False, str(e)
