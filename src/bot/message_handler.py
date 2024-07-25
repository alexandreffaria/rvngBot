from pywa import WhatsApp
from pywa.types import Message, Button, CallbackButton, ButtonUrl, Contact
from .storage import Storage
from .database import Database
import logging
import time
import requests
from email_validator import validate_email, EmailNotValidError
from datetime import datetime

class MessageHandler:
    def __init__(self, whatsapp_client: WhatsApp):
        self.whatsapp_client = whatsapp_client
        self.storage = Storage()
        self.database = Database()

    def validate_email_address(self, email):
        try:
            v = validate_email(email)
            email = v["email"]
            return True, email
        except EmailNotValidError as e:
            return False, str(e)

    def handle_message(self, message: Message):
        user_number = message.from_user.wa_id
        user_input = message.text.strip()
        timestamp = message.timestamp

        logging.info(f"Received message from {user_number}: {user_input}")

        # Store the incoming message in the database
        self.database.insert_message(user_number, "user", user_input, timestamp)

        # Check if the user wants to talk to a human
        if "atendente" in user_input or "humano" in user_input or "falar" in user_input:
            self.handle_human_request(user_number)
            self.storage.set(user_number, 'state', None)
            return

        # Get the current state of the user
        current_state = self.storage.get(user_number, 'state')
        logging.info(f"Current state for {user_number}: {current_state}")

        if current_state is None:
            # Initial interaction
            self.send_message(user_number, "Olá, eu sou a assistente virtual da Fada do Dente. 🧚 Obrigada por entrar em contato. Para iniciar seu atendimento, qual o seu nome completo?")
            self.storage.set(user_number, 'state', 'awaiting_name')

        elif current_state == 'awaiting_name':
            # User has provided their name
            self.storage.set(user_number, 'name', user_input)
            self.send_message(user_number, f"Muito obrigada, {user_input.split(' ')[0].capitalize()}. E qual o seu email?")
            self.storage.set(user_number, 'state', 'awaiting_email')

        elif current_state == 'awaiting_email':
            # User has provided their email, validate it
            is_valid, result = self.validate_email_address(user_input)
            if is_valid:
                self.storage.set(user_number, 'email', result)
                self.send_message(user_number, "Qual sua área de atuação?", buttons=[
                    Button("Dentista", callback_data="Dentista"),
                    Button("Lojista", callback_data="Lojista"),
                    Button("Outros", callback_data="Outros"),
                ])
                self.storage.set(user_number, 'state', 'awaiting_role')
            else:
                self.send_message(user_number, f"Hm, isso não parece um email válido. 🤔 Vamos tentar de novo?")
                self.storage.set(user_number, 'state', 'awaiting_email')

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

    def send_message(self, user_number, text, buttons=None, button_url=None, footer=None):
        if buttons:
            self.whatsapp_client.send_message(to=user_number, text=text, buttons=buttons)
        elif button_url:
            self.whatsapp_client.send_message(to=user_number, text=text, buttons=[button_url], footer=footer)
        else:
            self.whatsapp_client.send_message(to=user_number, text=text)

        # Store the outgoing message in the database
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.database.insert_message(user_number, "bot", text, timestamp)

    def handle_callback_button(self, callback_button: CallbackButton):
        user_number = callback_button.from_user.wa_id
        user_input = callback_button.data

        logging.info(f"Received callback from {user_number}: {user_input}")

        # Store the incoming callback data as a message
        self.database.insert_message(user_number, "user", user_input, time.time())

        # Get the current state of the user
        current_state = self.storage.get(user_number, 'state')
        logging.info(f"Current state for {user_number}: {current_state}")

        if current_state == 'awaiting_role':
            # User has provided their role
            self.storage.set(user_number, 'role', user_input)
            self.tag_user(user_number)
            self.send_message(user_number, "Obrigada pelas informações 😊. Como podemos te ajudar hoje?", buttons=[
                Button("Fazer um pedido", callback_data="Fazer um pedido"),
                Button("Tirar dúvidas", callback_data="Tirar dúvidas"),
            ])
            self.storage.set(user_number, 'state', 'awaiting_help_type')

        elif current_state == 'awaiting_help_type':
            if user_input == "Fazer um pedido":
                self.send_message(user_number, "Temos condições especiais para você, olha só!")
                
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
                self.send_message(user_number, "Vamos montar seu pedido!")

                time.sleep(3)

                self.whatsapp_client.send_sticker(
                    to=user_number,
                    sticker="stickers/todos-os-produtos.webp",
                    mime_type="image/webp"
                )

                self.send_message(user_number, "Você gostaria de comprar o Porta Dentinho de Leite?",buttons=[
                        Button("Sim", callback_data="Sim"),
                        Button("Não", callback_data="Não"),
                    ])
               
                self.storage.set(user_number, 'state', 'awaiting_pd_interest')
            elif user_input == "Tirar dúvidas":
                self.send_message(user_number, "No momento esse número não tem atendimento, por favor entre em contato com a gente no contato abaixo! 📞")
                self.whatsapp_client.send_contact(
                    to=user_number,
                    contact=Contact(
                        name=Contact.Name(formatted_name='Dentinho da Fada', first_name='Dentinho da Fada'),
                        phones=[Contact.Phone(phone='553184161141', type='MAIN')],
                        emails=[Contact.Email(email='vendas@dentinhodafada.com.br', type='WORK')],
                        urls=[Contact.Url(url='https://dentinhodafada.com.br', type='WORK')],
                    )
                )
                self.storage.set(user_number, 'state', None)

        elif current_state == 'awaiting_pd_interest':
            if user_input == "Sim":
                self.ask_next_color(user_number, 'Rosa')
            else:
                self.ask_for_book(user_number)

        elif current_state == 'awaiting_pd_rosa':
            if user_input == "Sim":
                self.send_message(user_number, "Quantos porta dente de leite *rosa* você gostaria?")
                self.storage.set(user_number, 'state', 'awaiting_pd_rosa_quantity')
            else:
                self.ask_next_color(user_number, 'Azul')

        elif current_state == 'awaiting_pd_azul':
            if user_input == "Sim":
                self.send_message(user_number, "Quantos porta dente de leite *azul* você gostaria?")
                self.storage.set(user_number, 'state', 'awaiting_pd_azul_quantity')
            else:
                self.ask_next_color(user_number, 'Laranja')

        elif current_state == 'awaiting_pd_laranja':
            if user_input == "Sim":
                self.send_message(user_number, "Quantos porta dente de leite *laranja* você gostaria?")
                self.storage.set(user_number, 'state', 'awaiting_pd_laranja_quantity')
            else:
                self.ask_next_color(user_number, 'Verde')

        elif current_state == 'awaiting_pd_verde':
            if user_input == "Sim":
                self.send_message(user_number, "Quantos porta dente de leite *verde* você gostaria?")
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
                self.send_message(user_number, "Quantos livros *Dentinho da Fada* você gostaria? 📖?")
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
        self.send_message(
            user_number, 
            f"Você gostaria de comprar o porta dentinho *{color}*? {emoji_color}",
            buttons=[
                Button("Sim", callback_data="Sim"),
                Button("Não", callback_data="Não"),
        ])
        self.storage.set(user_number, f'state', f'awaiting_pd_{color.lower()}')

    def ask_for_book(self, user_number):
        self.send_message(
            user_number, 
            "Você gostaria de comprar o Livro - Dentinho da Fada?",
            buttons=[
                Button("Sim", callback_data="Sim"),
                Button("Não", callback_data="Não"),
            ])

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
            self.send_message(user_number, "Você não selecionou nenhum item para finalizar o pedido. Por favor, selecione pelo menos um item.")
            self.storage.set(user_number, 'state', 'awaiting_pd_interest')

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
        shortened_checkout_url = self.shorten_url(checkout_url)
        self.send_message(user_number, f"{name.split()[0].capitalize()}, agradecemos muito sua confiança e esperamos que você adore nossos produtos! ❤️🧚")

        # Send the checkout link to the user
        self.send_message(
            user_number, 
            f"🛒 Segue o link do seu pedido:", 
            buttons=ButtonUrl(
                title="Link de pagamento",
                url=shortened_checkout_url,
            ),
            footer="A magia de cuidar dos dentinhos!"
        )

        self.storage.set(user_number, 'pd_azul', '0')
        self.storage.set(user_number, 'pd_rosa', '0')
        self.storage.set(user_number, 'pd_verde', '0')
        self.storage.set(user_number, 'pd_laranja', '0')
        self.storage.set(user_number, 'book_quantity', '0')
        self.storage.set(user_number, 'state', None)

    def shorten_url(self, long_url):
        url = "https://url-shortener-service.p.rapidapi.com/shorten"
        payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"url\"\r\n\r\n{long_url}\r\n-----011000010111000001101001--\r\n\r\n"
        headers = {
            "x-rapidapi-key": "94442fdf41msh063434b9eadbca4p10158fjsn2df90fa67770",
            "x-rapidapi-host": "url-shortener-service.p.rapidapi.com",
            "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
        }

        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("result_url")
        else:
            logging.error(f"Failed to shorten URL: {response.text}")
            return long_url

    def tag_user(self, user_number):
        name = self.storage.get(user_number, 'name')
        email = self.storage.get(user_number, 'email')
        role = self.storage.get(user_number, 'role')
        # Here you can implement tagging logic, e.g., save to database or CRM
        logging.info(f"Tagging user {user_number}: Name={name}, Email={email}, Role={role}")

    def handle_human_request(self, user_number):
        self.send_message(user_number, "No momento esse número não tem atendimento, por favor entre em contato com a gente no contato abaixo! 📞")
        self.whatsapp_client.send_contact(
            to=user_number,
            contact=Contact(
                name=Contact.Name(formatted_name='Dentinho da Fada', first_name='Dentinho da Fada'),
                phones=[Contact.Phone(phone='553184161141', type='MAIN')],
                emails=[Contact.Email(email='vendas@dentinhodafada.com.br', type='WORK')],
                urls=[Contact.Url(url='https://dentinhodafada.com.br', type='WORK')],
            )
        )