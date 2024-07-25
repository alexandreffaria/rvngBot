from email_validator import validate_email, EmailNotValidError
from pywa.types import Button

class EmailHandler:
    def __init__(self, storage, whatsapp_client, database):
        self.storage = storage
        self.whatsapp_client = whatsapp_client
        self.database = database

    def handle_email(self, user_number, user_input):
        is_valid, result = self.validate_email_address(user_input)
        if is_valid:
            self.storage.set(user_number, 'email', result)
            self.whatsapp_client.send_message(
                to=user_number,
                text="Qual sua área de atuação?",
                buttons=[
                    Button("Dentista", callback_data="Dentista"),
                    Button("Lojista", callback_data="Lojista"),
                    Button("Outros", callback_data="Outros"),
                ]
            )
            self.storage.set(user_number, 'state', 'awaiting_role')
        else:
            self.whatsapp_client.send_message(user_number, "Hm, isso não parece um email válido. 🤔 Vamos tentar de novo?")
            self.storage.set(user_number, 'state', 'awaiting_email')

    def validate_email_address(self, email):
        try:
            v = validate_email(email)
            email = v["email"]
            return True, email
        except EmailNotValidError as e:
            return False, str(e)
