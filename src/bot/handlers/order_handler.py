import logging
import requests
from pywa.types import Button, ButtonUrl

class OrderHandler:
    def __init__(self, storage, whatsapp_client, database):
        self.storage = storage
        self.whatsapp_client = whatsapp_client
        self.database = database

    def handle_pd_quantity(self, user_number, current_state, user_input):
        color = current_state.split('_')[-2]
        self.storage.set(user_number, f'pd_{color}', user_input)
        next_color = self.get_next_color(color)
        if next_color:
            self.ask_next_color(user_number, next_color)
        else:
            self.ask_for_book(user_number)

    def handle_book_quantity(self, user_number, user_input):
        self.storage.set(user_number, 'book_quantity', user_input)
        self.finalize_order(user_number)

    def handle_pd_interest(self, user_number, user_input):
        if user_input == "Sim":
            self.ask_next_color(user_number, 'Rosa')
        else:
            self.ask_for_book(user_number)

    def handle_pd_response(self, user_number, current_state, user_input):
        color = current_state.split('_')[-1]
        if user_input == "Sim":
            self.whatsapp_client.send_message(user_number, f"Quantos porta dente de leite *{color}* você gostaria?")
            self.storage.set(user_number, 'state', f'awaiting_pd_{color.lower()}_quantity')
        else:
            next_color = self.get_next_color(color)
            if next_color:
                self.ask_next_color(user_number, next_color)
            else:
                self.ask_for_book(user_number)

    def handle_book_response(self, user_number, user_input):
        if user_input == "Sim":
            self.whatsapp_client.send_sticker(
                to=user_number,
                sticker="assets/stickers/livro-dentinho-da-fada.webp",
                mime_type="image/webp"
            )
            self.whatsapp_client.send_message(user_number, "Quantos livros *Dentinho da Fada* você gostaria? 📖?")
            self.storage.set(user_number, 'state', 'awaiting_book_quantity')
        else:
            self.finalize_order(user_number)

    def ask_next_color(self, user_number, color):
        sticker_path = self.get_sticker_path(color)
        emoji_color = self.get_emoji_color(color)

        self.whatsapp_client.send_sticker(
            to=user_number,
            sticker=sticker_path,
            mime_type="image/webp"
        )
        self.whatsapp_client.send_message(
            user_number, 
            f"Você gostaria de comprar o porta dentinho *{color}*? {emoji_color}",
            buttons=[
                Button("Sim", callback_data="Sim"),
                Button("Não", callback_data="Não"),
        ])
        self.storage.set(user_number, f'state', f'awaiting_pd_{color.lower()}')

    def ask_for_book(self, user_number):
        self.whatsapp_client.send_message(
            user_number, 
            "Você gostaria de comprar o Livro - Dentinho da Fada?",
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
            self.whatsapp_client.send_message(user_number, "Você não selecionou nenhum item para finalizar o pedido. Por favor, selecione pelo menos um item.")
            self.storage.set(user_number, 'state', 'awaiting_pd_interest')
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
        checkout_url = f"{base_url}{products}?checkout[email]={email}&checkout[shipping_address][first_name]={name.split()[0]}&checkout[shipping_address][last_name]={'%20'.join(name.split()[1:])}&checkout[shipping_address][phone]={user_number}"
        shortened_checkout_url = self.shorten_url(checkout_url)
        print(f"checkoutURL: {checkout_url}")
        print(f"shortURL: {shortened_checkout_url}")
        self.whatsapp_client.send_message(user_number, f"{name.split()[0].capitalize()}, agradecemos muito sua confiança e esperamos que você adore nossos produtos! ❤️🧚")

        # Send the checkout link to the user
        self.whatsapp_client.send_message(
            user_number, 
            f"🛒 Segue o link do seu pedido:", 
            buttons=ButtonUrl(
                title="Link de pagamento",
                url=shortened_checkout_url,
            ),
            footer="A magia de cuidar dos dentinhos!"
        )

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
