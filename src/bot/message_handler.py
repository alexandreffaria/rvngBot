from pywa import WhatsApp
from pywa.types import Message, Button, CallbackButton
from .storage import Storage
import logging
import time

class MessageHandler:
    def __init__(self, whatsapp_client: WhatsApp):
        self.whatsapp_client = whatsapp_client
        self.storage = Storage()

    def handle_message(self, message: Message):
        user_number = message.from_user.wa_id
        user_input = message.text.strip()

        logging.info(f"Received message from {user_number}: {user_input}")

         # Check if the user wants to talk to a human
        if "atendente" in user_input or "humano" in user_input:
            self.handle_human_request(user_number)
            self.storage.set(user_number, 'state', None)
            return

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

        elif current_state == 'awaiting_pd_rosa_quantity':
            # User has provided the quantity of rosa porta dente de leite
            self.storage.set(user_number, 'pd_rosa', user_input)
            self.ask_next_color(user_number, 'Azul')

        elif current_state == 'awaiting_pd_azul_quantity':
            # User has provided the quantity of azul porta dente de leite
            self.storage.set(user_number, 'pd_azul', user_input)
            self.ask_next_color(user_number, 'Laranja')

        elif current_state == 'awaiting_pd_laranja_quantity':
            # User has provided the quantity of laranja porta dente de leite
            self.storage.set(user_number, 'pd_laranja', user_input)
            self.ask_next_color(user_number, 'Verde')

        elif current_state == 'awaiting_pd_verde_quantity':
            # User has provided the quantity of verde porta dente de leite
            self.storage.set(user_number, 'pd_verde', user_input)
            self.ask_for_book(user_number)

        elif current_state == 'awaiting_book_quantity':
            # User has provided the quantity of books
            self.storage.set(user_number, 'book_quantity', user_input)
            self.finalize_order(user_number)

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
                text="Obrigada pelas informações 😊. Como podemos te ajudar hoje?",
                buttons=[
                    Button("Fazer um pedido", callback_data="Fazer um pedido"),
                    Button("Tirar dúvidas", callback_data="Tirar dúvidas"),
                ]
            )
            self.storage.set(user_number, 'state', 'awaiting_help_type')

        elif current_state == 'awaiting_help_type':
            if user_input == "Fazer um pedido":
                self.whatsapp_client.send_message(
                to=user_number,
                text="Temos condições especiais para você, olha só!"
                )
                self.whatsapp_client.send_image(
                    to=user_number,
                    caption="Porta Dentinho de Leite",
                    image="images/tabela_porta_dentinho.jpeg"
                )
                self.whatsapp_client.send_image(
                    to=user_number,
                    caption="Livro - Dentinho da Fada",
                    image="images/tabela_livro.jpeg"
                )
                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Vamos montar seu pedido!"
                )

                time.sleep(3)

                self.whatsapp_client.send_sticker(
                    to=user_number,
                    sticker="stickers/todos-os-produtos.webp",
                    mime_type="image/webp"
                )

                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Você gostaria de comprar o Porta Dentinho de Leite?",
                    buttons=[
                        Button("Sim", callback_data="Sim"),
                        Button("Não", callback_data="Não"),
                    ]
                )
                self.storage.set(user_number, 'state', 'awaiting_pd_interest')
            elif user_input == "Tirar dúvidas":
                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Vamos entrar em contato com você em breve para tirar suas dúvidas."
                )
                self.storage.set(user_number, 'state', None)

        elif current_state == 'awaiting_pd_interest':
            if user_input == "Sim":
                self.ask_next_color(user_number, 'Rosa')
            else:
                self.ask_for_book(user_number)

        elif current_state == 'awaiting_pd_rosa':
            if user_input == "Sim":

                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Quantos porta dente de leite rosa você gostaria?"
                )
                self.storage.set(user_number, 'state', 'awaiting_pd_rosa_quantity')
            else:
                self.ask_next_color(user_number, 'Azul')

        elif current_state == 'awaiting_pd_azul':
            if user_input == "Sim":
                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Quantos porta dente de leite azul você gostaria?"
                )
                self.storage.set(user_number, 'state', 'awaiting_pd_azul_quantity')
            else:
                self.ask_next_color(user_number, 'Laranja')

        elif current_state == 'awaiting_pd_laranja':
            if user_input == "Sim":
                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Quantos porta dente de leite laranja você gostaria?"
                )
                self.storage.set(user_number, 'state', 'awaiting_pd_laranja_quantity')
            else:
                self.ask_next_color(user_number, 'Verde')

        elif current_state == 'awaiting_pd_verde':
            if user_input == "Sim":
                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Quantos porta dente de leite verde você gostaria?"
                )
                self.storage.set(user_number, 'state', 'awaiting_pd_verde_quantity')
            else:
                self.ask_for_book(user_number)

        elif current_state == 'awaiting_book':
            if user_input == "Sim":
                self.whatsapp_client.send_sticker(
                    to=user_number,
                    sticker="stickers/livro-dentinho-da-fada.webp",
                    mime_type="image/webp"
                )
                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Quantos livros *Dentinho da Fada* você gostaria? 📖"
                )
                self.storage.set(user_number, 'state', 'awaiting_book_quantity')
            else:
                self.finalize_order(user_number)

    def ask_next_color(self, user_number, color):

        sticker_path = ""
        emoji_color = ""
        if color == "Rosa":
            sticker_path = "stickers/porta-dente-rosa.webp"
            emoji_color = "🩷"
        elif color == "Azul":
            sticker_path = "stickers/porta-dente-azul.webp"
            emoji_color = "🔵"
        elif color == "Laranja":
            sticker_path = "stickers/porta-dente-laranja.webp"
            emoji_color = "🟠"
        elif color == "Verde":
            sticker_path = "stickers/porta-dente-verde.webp"
            emoji_color = "🟢"

        self.whatsapp_client.send_sticker(
            to=user_number,
            sticker=sticker_path,
            mime_type="image/webp"
        )
        self.whatsapp_client.send_message(
            to=user_number,
            text=f"Você gostaria de comprar o porta dentinho *{color}*? {emoji_color}",
            buttons=[
                Button("Sim", callback_data="Sim"),
                Button("Não", callback_data="Não"),
            ]
        )
        self.storage.set(user_number, f'state', f'awaiting_pd_{color.lower()}')

    def ask_for_book(self, user_number):
        self.whatsapp_client.send_message(
            to=user_number,
            text="Você gostaria de comprar o Livro - Dentinho da Fada?",
            buttons=[
                Button("Sim", callback_data="Sim"),
                Button("Não", callback_data="Não"),
            ]
        )
        self.storage.set(user_number, 'state', 'awaiting_book')

    def finalize_order(self, user_number):
        # Gather all the necessary information
        pd_azul = self.storage.get(user_number, 'pd_azul', '0')
        pd_rosa = self.storage.get(user_number, 'pd_rosa', '0')
        pd_verde = self.storage.get(user_number, 'pd_verde', '0')
        pd_laranja = self.storage.get(user_number, 'pd_laranja', '0')
        book_quantity = self.storage.get(user_number, 'book_quantity', '0')
        email = self.storage.get(user_number, 'email')
        name = self.storage.get(user_number, 'name')

        # Check if any items were selected
        if pd_azul == '0' and pd_rosa == '0' and pd_verde == '0' and pd_laranja == '0' and book_quantity == '0':
            self.whatsapp_client.send_message(
                to=user_number,
                text="Você não selecionou nenhum item para finalizar o pedido. Por favor, selecione pelo menos um item."
            )
            return

        # Create the link dynamically
        base_url = "https://loja.dentinhodafada.com.br/cart/"
        product_list = []

        if pd_azul != '0':
            product_list.append(f"48281127977237:{pd_azul}")
        if pd_rosa != '0':
            product_list.append(f"48281127944469:{pd_rosa}")
        if pd_verde != '0':
            product_list.append(f"48281128010005:{pd_verde}")
        if pd_laranja != '0':
            product_list.append(f"48281128042773:{pd_laranja}")
        if book_quantity != '0':
            product_list.append(f"45653364015381:{book_quantity}")

        products = ",".join(product_list)
        checkout_url = f"{base_url}{products}?checkout[email]={email}&checkout[shipping_address][first_name]={name.split()[0]}&checkout[shipping_address][last_name]={name.split()[-1]}&checkout[shipping_address][phone]={user_number}"

        # Send the checkout link to the user
        self.whatsapp_client.send_message(
            to=user_number,
            text=f"Segue o link do seu pedido {name.split()[0].capitalize()}: ({checkout_url})"
        )

        self.storage.set(user_number, 'pd_azul', '0')
        self.storage.set(user_number, 'pd_rosa', '0')
        self.storage.set(user_number, 'pd_verde', '0')
        self.storage.set(user_number, 'pd_laranja', '0')
        self.storage.set(user_number, 'book_quantity', '0')
        self.storage.set(user_number, 'state', None)

    def tag_user(self, user_number):
        name = self.storage.get(user_number, 'name')
        email = self.storage.get(user_number, 'email')
        role = self.storage.get(user_number, 'role')
        # Here you can implement tagging logic, e.g., save to database or CRM
        logging.info(f"Tagging user {user_number}: Name={name}, Email={email}, Role={role}")

    def handle_human_request(self, user_number):
        self.whatsapp_client.send_message(
            to=user_number,
            text="Para falar com um atendente, por favor entre em contato pelo número: +55 31 1234-5678"
        )