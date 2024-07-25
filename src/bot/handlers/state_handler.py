from pywa.types import Button, Contact
import logging
import time

class StateHandler:
    def __init__(self, storage, whatsapp_client, database):
        self.storage = storage
        self.whatsapp_client = whatsapp_client
        self.database = database

    def initial_interaction(self, user_number):
        self.whatsapp_client.send_message(user_number, "Olá, eu sou a assistente virtual da Fada do Dente. 🧚 Obrigada por entrar em contato. Para iniciar seu atendimento, qual o seu nome completo?")
        self.storage.set(user_number, 'state', 'awaiting_name')

    def handle_name(self, user_number, user_input):
        self.storage.set(user_number, 'name', user_input)
        self.whatsapp_client.send_message(user_number, f"Muito obrigada, {user_input.split(' ')[0].capitalize()}. E qual o seu email?")
        self.storage.set(user_number, 'state', 'awaiting_email')

    def handle_role(self, user_number, user_input):
        self.storage.set(user_number, 'role', user_input)
        self.tag_user(user_number)
        self.whatsapp_client.send_message(user_number, "Obrigada pelas informações. 😊 Como podemos te ajudar hoje?", buttons=[
            Button("Fazer um pedido", callback_data="Fazer um pedido"),
            Button("Tirar dúvidas", callback_data="Tirar dúvidas"),
        ])
        self.storage.set(user_number, 'state', 'awaiting_help_type')

    def handle_help_type(self, user_number, user_input):
        if user_input == "Fazer um pedido":
            self.whatsapp_client.send_message(user_number, "Temos condições especiais para você, olha só!")
            
            self.whatsapp_client.send_image(
                to=user_number,
                caption="Porta Dentinho de Leite",
                image="assets/images/tabela_porta_dentinho.jpeg"
            )
            self.whatsapp_client.send_image(
                to=user_number,
                caption="Livro - Dentinho da Fada",
                image="assets/images/tabela_livro.jpeg"
            )
            self.whatsapp_client.send_message(user_number, "Vamos montar seu pedido!")

            time.sleep(3)

            self.whatsapp_client.send_sticker(
                to=user_number,
                sticker="assets/stickers/todos-os-produtos.webp",
                mime_type="image/webp"
            )

            self.whatsapp_client.send_message(user_number, "Você gostaria de comprar o Porta Dentinho de Leite?", buttons=[
                    Button("Sim", callback_data="Sim"),
                    Button("Não", callback_data="Não"),
                ])
            
            self.storage.set(user_number, 'state', 'awaiting_pd_interest')
        elif user_input == "Tirar dúvidas":
            self.whatsapp_client.send_message(user_number, "No momento esse número não tem atendimento, por favor entre em contato com a gente no contato abaixo! 📞")
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

    def handle_human_request(self, user_number):
        self.whatsapp_client.send_message(user_number, "No momento esse número não tem atendimento, por favor entre em contato com a gente no contato abaixo! 📞")
        self.whatsapp_client.send_contact(
            to=user_number,
            contact=Contact(
                name=Contact.Name(formatted_name='Dentinho da Fada', first_name='Dentinho da Fada'),
                phones=[Contact.Phone(phone='553184161141', type='MAIN')],
                emails=[Contact.Email(email='vendas@dentinhodafada.com.br', type='WORK')],
                urls=[Contact.Url(url='https://dentinhodafada.com.br', type='WORK')],
            )
        )

    def tag_user(self, user_number):
        name = self.storage.get(user_number, 'name')
        email = self.storage.get(user_number, 'email')
        role = self.storage.get(user_number, 'role')
        # Here you can implement tagging logic, e.g., save to database or CRM
        logging.info(f"Tagging user {user_number}: Name={name}, Email={email}, Role={role}")
