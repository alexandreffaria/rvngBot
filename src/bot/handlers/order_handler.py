import logging
import requests
from pywa.types import Button, ButtonUrl
from config.settings import ME, SHORT_IO_API_KEY
import time

class OrderHandler:
    def __init__(self, whatsapp_client, database):
        self.whatsapp_client = whatsapp_client
        self.database = database

    def validate_integer(self, user_input):
        try:
            value = int(user_input)
            return True, value
        except ValueError:
            return False, None

    def handle_pd_quantity(self, user_number, current_state, user_input):
        user_id = self.database.insert_user(user_number)
        is_valid, quantity = self.validate_integer(user_input)
        if is_valid:
            color = current_state.split('_')[-2]
            self.database.insert_or_update_product_amount(user_id, f'pd_{color}', quantity)
            next_color = self.get_next_color(color)
            if next_color:
                self.ask_next_color(user_number, next_color)
            else:
                self.ask_for_book(user_number)
        else:
            message = "Por favor, insira um número válido para a quantidade."
            self.whatsapp_client.send_message(user_number, message)
            self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
            self.database.set_state(user_id, 'state', current_state)

    def handle_book_quantity(self, user_number, user_input):
        user_id = self.database.insert_user(user_number)
        is_valid, quantity = self.validate_integer(user_input)
        if is_valid:
            self.database.insert_or_update_product_amount(user_id, 'book', quantity)
            self.finalize_order(user_number)
        else:
            message = "Por favor, insira um número válido para a quantidade de livros."
            self.whatsapp_client.send_message(user_number, message)
            self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
            self.database.set_state(user_id, 'state', 'awaiting_book_quantity')

    def handle_pd_interest(self, user_number, user_input):
        if user_input == "Sim":
            self.ask_next_color(user_number, 'Rosa')
        else:
            self.ask_for_book(user_number)

    def handle_pd_response(self, user_number, current_state, user_input):
        user_id = self.database.insert_user(user_number)
        color = current_state.split('_')[-1]
        if user_input == "Sim":
            message = f"Quantos porta dente de leite *{color}* você gostaria?"
            self.whatsapp_client.send_message(user_number, message)
            self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
            self.database.set_state(user_id, 'state', f'awaiting_pd_{color.lower()}_quantity')
        else:
            next_color = self.get_next_color(color)
            if next_color:
                self.ask_next_color(user_number, next_color)
            else:
                self.ask_for_book(user_number)

    def handle_book_response(self, user_number, user_input):
        user_id = self.database.insert_user(user_number)
        if user_input == "Sim":
            self.whatsapp_client.send_sticker(
                to=user_number,
                sticker="assets/stickers/livro-dentinho-da-fada.webp",
                mime_type="image/webp"
            )
            message = "Quantos livros *Dentinho da Fada* você gostaria? 📖"
            self.whatsapp_client.send_message(user_number, message)
            self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
            self.database.set_state(user_id, 'state', 'awaiting_book_quantity')
        else:
            self.finalize_order(user_number)

    def ask_next_color(self, user_number, color):
        user_id = self.database.insert_user(user_number)
        sticker_path = self.get_sticker_path(color)
        emoji_color = self.get_emoji_color(color)

        self.whatsapp_client.send_sticker(
            to=user_number,
            sticker=sticker_path,
            mime_type="image/webp"
        )
        message = f"Você gostaria de comprar o porta dentinho *{color}*? {emoji_color}"
        self.whatsapp_client.send_message(
            user_number, 
            message,
            buttons=[
                Button("Sim", callback_data="Sim"),
                Button("Não", callback_data="Não"),
        ])
        self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
        self.database.set_state(user_id, 'state', f'awaiting_pd_{color.lower()}')

    def ask_for_book(self, user_number):
        user_id = self.database.insert_user(user_number)
        message = "Você gostaria de comprar o Livro - Dentinho da Fada?"
        self.whatsapp_client.send_message(
            user_number, 
            message,
            buttons=[
                Button("Sim", callback_data="Sim"),
                Button("Não", callback_data="Não"),
            ]
        )
        self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
        self.database.set_state(user_id, 'state', 'awaiting_book')

    def finalize_order(self, user_number):
        user_id = self.database.insert_user(user_number)
        user_details = self.database.get_user_by_phone(user_number)

        # Retrieve product amounts from the database
        product_amounts = self.database.get_product_amounts(user_id)
        product_dict = {item[0]: item[1] for item in product_amounts}

        pd_azul = product_dict.get('pd_azul', 0)
        pd_rosa = product_dict.get('pd_rosa', 0)
        pd_verde = product_dict.get('pd_verde', 0)
        pd_laranja = product_dict.get('pd_laranja', 0)
        book_quantity = product_dict.get('book', 0)

        email = user_details['email']
        name =  user_details['name']

        # Check if any items were selected
        if pd_azul == 0 and pd_rosa == 0 and pd_verde == 0 and pd_laranja == 0 and book_quantity == 0:
            message = "Você não selecionou nenhum item para finalizar o pedido. Por favor, selecione pelo menos um item."
            self.whatsapp_client.send_message(user_number, message)
            self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
            self.database.set_state(user_id, 'state', 'awaiting_pd_interest')
            self.whatsapp_client.send_sticker(
                to=user_number,
                sticker="assets/stickers/todos-os-produtos.webp",
                mime_type="image/webp"
            )
            message = "Você gostaria de comprar o Porta Dentinho de Leite?"
            self.whatsapp_client.send_message(user_number, message, buttons=[
                    Button("Sim", callback_data="Sim"),
                    Button("Não", callback_data="Não"),
                ])
            self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())
            self.database.set_state(user_id, 'state', 'awaiting_pd_interest')
            return

        # Create the link dynamically
        base_url = "https://loja.dentinhodafada.com.br/cart/"
        product_list = []

        if pd_azul != 0:
            product_list.append(f"48281127977237:{pd_azul}")
        if pd_rosa != 0:
            product_list.append(f"48281127944469:{pd_rosa}")
        if pd_verde != 0:
            product_list.append(f"48281128010005:{pd_verde}")
        if pd_laranja != 0:
            product_list.append(f"48281128042773:{pd_laranja}")
        if book_quantity != 0:
            product_list.append(f"45653364015381:{book_quantity}")

        products = ",".join(product_list)
        checkout_url = f"{base_url}{products}?checkout[email]={email}&checkout[shipping_address][first_name]={name.split(' ')[0]}&checkout[shipping_address][last_name]={'%20'.join(name.split()[1:])}&checkout[shipping_address][phone]={user_number}"
        shortened_checkout_url = self.shorten_url(checkout_url)
        
        message = f"{name.split()[0].capitalize()}, agradecemos muito sua confiança e esperamos que você adore nossos produtos! ❤️🧚"
        self.whatsapp_client.send_message(user_number, message)
        self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())

        # Send the checkout link to the user
        message = f"🛒 Segue o link do seu pedido:"
        self.whatsapp_client.send_message(
            user_number, 
            message, 
            buttons=ButtonUrl(
                title="Link de pagamento",
                url=shortened_checkout_url,
            ),
            footer="A magia de cuidar dos dentinhos!"
        )
        message = f"🛒 Segue o link do seu pedido: {shortened_checkout_url}"
        self.database.insert_message(user_id, "bot", ME, "user", user_number, message, time.time())

        # Reset the states
        self.reset_user_state(user_number)

    def get_next_color(self, current_color):
        colors = ["rosa", "azul", "laranja", "verde"]
        current_index = colors.index(current_color.lower())
        if current_index + 1 < len(colors):
            return colors[current_index + 1]
        return None

    def get_sticker_path(self, color):
        return f"assets/stickers/porta-dente-{color.lower()}.webp"

    def get_emoji_color(self, color):
        emojis = {
            "Rosa": "🩷",
            "Azul": "🔵",
            "Laranja": "🟠",
            "Verde": "🟢"
        }
        color_capitalized = color.capitalize()
        if color_capitalized not in emojis:
            logging.error(f"Color '{color}' not found in emojis dictionary")
            return ""
        return emojis[color_capitalized]

    def reset_user_state(self, user_number):
        user_id = self.database.insert_user(user_number)
        self.database.insert_or_update_product_amount(user_id, 'pd_azul', 0)
        self.database.insert_or_update_product_amount(user_id, 'pd_rosa', 0)
        self.database.insert_or_update_product_amount(user_id, 'pd_verde', 0)
        self.database.insert_or_update_product_amount(user_id, 'pd_laranja', 0)
        self.database.insert_or_update_product_amount(user_id, 'book', 0)
        self.database.set_state(user_id, 'state', None)

    def shorten_url(self, long_url):
        url = "https://api.short.io/links"
        payload = {
            "domain": "short.redandblue.vip",
            "originalURL": long_url
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": SHORT_IO_API_KEY
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("secureShortURL")
        else:
            logging.error(f"Failed to shorten URL: {response.text}")
            return long_url
