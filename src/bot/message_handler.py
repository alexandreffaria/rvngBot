from pywa import WhatsApp
from pywa.types import Message

class MessageHandler:
    def __init__(self, whatsapp_client: WhatsApp):
        self.whatsapp_client = whatsapp_client

    def handle_message(self, message: Message):
        user_number = message.from_user.wa_id

        if message.text == "oi":
            self.whatsapp_client.send_message(
                to=user_number,
                text="Olá, eu sou a assistente virtual da Fada do Dente. 🧚 Obrigada por entrar em contato. Para iniciar seu atendimento, qual o seu nome?",
            )
