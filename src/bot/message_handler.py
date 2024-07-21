from pywa import WhatsApp
from pywa.types import Message, Button, CallbackButton
from .storage import Storage
import logging

class MessageHandler:
    def __init__(self, whatsapp_client: WhatsApp):
        self.whatsapp_client = whatsapp_client
        self.storage = Storage()

    def handle_message(self, message: Message):
        user_number = message.from_user.wa_id
        user_input = message.text.strip()

        logging.info(f"Received message from {user_number}: {user_input}")

        # Get the current state of the user
        current_state = self.storage.get(user_number, 'state')
        logging.info(f"Current state for {user_number}: {current_state}")

        if current_state is None:
            # Initial interaction
            self.whatsapp_client.send_message(
                to=user_number,
                text="Olá, eu sou a assistente virtual da Fada do Dente. 🧚 Obrigada por entrar em contato. Para iniciar seu atendimento, qual o seu nome completo?",
            )
            self.storage.set(user_number, 'state', 'awaiting_name')

        elif current_state == 'awaiting_name':
            # User has provided their name
            self.storage.set(user_number, 'name', user_input)
            self.whatsapp_client.send_message(
                to=user_number,
                text=f"Muito obrigada, {user_input.split(' ')[0].capitalize()}. E qual o seu email?",
            )
            self.storage.set(user_number, 'state', 'awaiting_email')

        elif current_state == 'awaiting_email':
            # User has provided their email
            self.storage.set(user_number, 'email', user_input)
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

    def handle_callback_button(self, callback_button: CallbackButton):
        user_number = callback_button.from_user.wa_id
        user_input = callback_button.data

        logging.info(f"Received callback from {user_number}: {user_input}")

        # Get the current state of the user
        current_state = self.storage.get(user_number, 'state')
        logging.info(f"Current state for {user_number}: {current_state}")

        if current_state == 'awaiting_role':
            # User has provided their role
            self.storage.set(user_number, 'role', user_input)
            self.tag_user(user_number)
            self.whatsapp_client.send_message(
                to=user_number,
                text="Obrigada pelas informações 😊. E agora, o que você gostaria?",
                buttons=[
                    Button("Fazer um pedido", callback_data="Fazer um pedido"),
                    Button("Tirar dúvidas", callback_data="Tirar dúvidas"),
                ]
            )
            self.storage.set(user_number, 'state', 'awaiting_next_action')

        elif current_state == 'awaiting_next_action' and user_input == "Fazer um pedido":
            # User wants to place an order
            self.whatsapp_client.send_message(
                to=user_number,
                text="Temos condições especiais para você, olha só!"
            )
            self.whatsapp_client.send_image(
                to=user_number,
                caption="Porta Dentinho de Leite",
                image="tabela_porta_dentinho.jpeg"
            )
            self.whatsapp_client.send_image(
                to=user_number,
                caption="Livro - Dentinho da Fada",
                image="tabela_livro.jpeg"
            )
            self.whatsapp_client.send_message(
                to=user_number,
                text="Vamos montar seu pedido!"
            )
            self.whatsapp_client.send_message(
                to=user_number,
                text="Agora que você sabe das nossas condições, selecione o produto que você deseja:",
                buttons=[
                    Button("Porta Dente de Leite", callback_data="Porta Dente de Leite"),
                    Button("Livro", callback_data="Livro - Dentinho da Fada"),
                    Button("Finalizar pedido", callback_data="Finalizar pedido"),
                ]
            )
            self.storage.set(user_number, 'state', 'order_start')

    def tag_user(self, user_number):
        name = self.storage.get(user_number, 'name')
        email = self.storage.get(user_number, 'email')
        role = self.storage.get(user_number, 'role')
        # Here you can implement tagging logic, e.g., save to database or CRM
        logging.info(f"Tagging user {user_number}: Name={name}, Email={email}, Role={role}")
