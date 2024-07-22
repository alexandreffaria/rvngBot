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

        elif current_state == 'awaiting_book_quantity':
            # User has provided the quantity of books
            self.storage.set(user_number, 'book_quantity', user_input)
            self.whatsapp_client.send_message(
                to=user_number,
                text="Agora que você sabe das nossas condições, selecione o produto que você deseja:",
                buttons=[
                    Button("Porta Dente de Leite", callback_data="Porta Dente de Leite"),
                    Button("Livro", callback_data="Livro - Dentinho da Fada"),
                    Button("Finalizar pedido", callback_data="Finalizar pedido"),
                ]
            )

        elif current_state == 'awaiting_pd_rosa':
            # User has provided the quantity of rosa porta dente de leite
            self.storage.set(user_number, 'pd_rosa', user_input)
            self.whatsapp_client.send_message(
                to=user_number,
                text="Quantos porta dente de leite azul você gostaria?"
            )
            self.storage.set(user_number, 'state', 'awaiting_pd_azul')

        elif current_state == 'awaiting_pd_azul':
            # User has provided the quantity of azul porta dente de leite
            self.storage.set(user_number, 'pd_azul', user_input)
            self.whatsapp_client.send_message(
                to=user_number,
                text="Quantos porta dente de leite laranja você gostaria?"
            )
            self.storage.set(user_number, 'state', 'awaiting_pd_laranja')

        elif current_state == 'awaiting_pd_laranja':
            # User has provided the quantity of laranja porta dente de leite
            self.storage.set(user_number, 'pd_laranja', user_input)
            self.whatsapp_client.send_message(
                to=user_number,
                text="Quantos porta dente de leite verde você gostaria?"
            )
            self.storage.set(user_number, 'state', 'awaiting_pd_verde')

        elif current_state == 'awaiting_pd_verde':
            # User has provided the quantity of verde porta dente de leite
            self.storage.set(user_number, 'pd_verde', user_input)
            self.whatsapp_client.send_message(
                to=user_number,
                text="Agora que você sabe das nossas condições, selecione o produto que você deseja:",
                buttons=[
                    Button("Porta Dente de Leite", callback_data="Porta Dente de Leite"),
                    Button("Livro", callback_data="Livro"),
                    Button("Finalizar pedido", callback_data="Finalizar pedido"),
                ]
            )
            self.storage.set(user_number, 'state', 'order_start')

        
        

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

        elif current_state == 'order_start':
            if user_input == "Livro":
                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Quantos livros 'Dentinho da Fada' você gostaria?"
                )
                self.storage.set(user_number, 'state', 'awaiting_book_quantity')
            elif user_input == "Porta Dente de Leite":
                self.whatsapp_client.send_message(
                    to=user_number,
                    text="Quantos porta dente de leite rosa você gostaria?"
                )
                self.storage.set(user_number, 'state', 'awaiting_pd_rosa')

        elif user_input == "Finalizar pedido":
            self.finalize_order(user_number)
    
    def finalize_order(self, user_number):
        # Gather all the necessary information
        pd_azul = self.storage.get(user_number, 'pd_azul', '0')
        pd_rosa = self.storage.get(user_number, 'pd_rosa', '0')
        pd_verde = self.storage.get(user_number, 'pd_verde', '0')
        pd_laranja = self.storage.get(user_number, 'pd_laranja', '0')
        book_quantity = self.storage.get(user_number, 'book_quantity', '0')
        email = self.storage.get(user_number, 'email')
        name = self.storage.get(user_number, 'name')
        phone = self.storage.get(user_number, 'phone', '')  # Assuming you have the phone number stored

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
        checkout_url = f"{base_url}{products}?checkout[email]={email}&checkout[shipping_address][first_name]={name.split()[0]}&checkout[shipping_address][last_name]={' '.join(name.split()[1:])}&checkout[shipping_address][phone]={phone}"

        # Send the checkout link to the user
        self.whatsapp_client.send_message(
            to=user_number,
            text=f"Aqui está o link para finalizar o seu pedido: {checkout_url}"
        )

    def tag_user(self, user_number):
        name = self.storage.get(user_number, 'name')
        email = self.storage.get(user_number, 'email')
        role = self.storage.get(user_number, 'role')
        # Here you can implement tagging logic, e.g., save to database or CRM
        logging.info(f"Tagging user {user_number}: Name={name}, Email={email}, Role={role}")
