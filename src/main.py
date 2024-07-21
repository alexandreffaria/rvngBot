from pywa import WhatsApp
from pywa.types import Button, ButtonUrl, Section, SectionList, SectionRow, FlowButton, FlowActionType, Contact, Message
from dotenv import load_dotenv
import os

import fastapi
import uvicorn

load_dotenv()

PHONE_ID = os.getenv("PHONE_NUMBER_ID")
TOKEN = os.getenv("TEMPORARY_ACCESS_TOKEN")
CALLBACK_URL = os.getenv("CALLBACK_URL")
ME = "5531933006786"

fastapi_app = fastapi.FastAPI()

wa = WhatsApp(
    phone_id=PHONE_ID,
    token=TOKEN,
    server=fastapi_app,
    callback_url=CALLBACK_URL,
    verify_token="XYZ123",
    app_id=123456,
    app_secret="",
)


@wa.on_message()
async def handle_message(client: WhatsApp, message: Message):
    user_number = message.from_user.wa_id

    if message.text == "oi":
        wa.send_message(
        to=user_number,
        text="Olá, eu sou a assistente virtual da Fada do Dente. 🧚 Obrigada por entrar em contato. Para iniciar seu atendimento, qual o seu nome?",
        )


if __name__ == '__main__':
    uvicorn.run(fastapi_app, port=8080)


# wa.send_message(
#     to=ME,
#     text="Because a vision softly creeping",
#     header="what is this",
# )

# wa.send_image(
#     to=ME,
#     image="https://picsum.photos/1000",
#     caption="have a good one c:",
# )


# wa.send_message(
#     to=ME,
#     text="What can I help you with?",
#     footer="Powered by PyWa",
#     buttons=[
#         Button("Help", callback_data="help me plz"),
#         Button("About", callback_data="about"),
#     ],
#     header="what is this",
# )
# wa.send_message(
#     to=ME,
#     text="Hello from papa! (https://github.com/alexandreffaria)",
#     preview_url=True,
#     header="what is this",
# )
# wa.send_message(
#     to=ME,
#     text="Hello from PyWa!",
#     footer="Powered by PyWa",
#     buttons=ButtonUrl(
#         title="PyWa GitHub",
#         url="https://github.com/david-lev/pywa",
#     ),
#     header="what is this",
# )

# wa.send_message(
#     to=ME,
#     text="What can I help you with?",
#     footer="Powered by PyWa",
#     buttons=SectionList(
#         button_title="Segue se coração ❤️",
#         sections=[
#             Section(
#                 title="Help",
#                 rows=[
#                     SectionRow(
#                         title="Help",
#                         callback_data="help",
#                         description="Get help with PyWa",
#                     ),
#                     SectionRow(
#                         title="About",
#                         callback_data="about",
#                         description="Learn more about PyWa",
#                     ),
#                 ],
#             ),
#            Section(
#                 title="Other",
#                 rows=[
#                     SectionRow(
#                         title="GitHub",
#                         callback_data="github",
#                         description="View the PyWa GitHub repository",
#                     ),
#                 ],
#             ),
#         ],
#     ),
# )

# wa.send_message(
#     to=ME,
#     text="We love to get feedback!",
#     footer="Powered by PyWa",
#     buttons=FlowButton(
#         title="Feedback",
#         flow_id="1234567890",
#         flow_token="AQAAAAACS5FpgQ_cAAAAAD0QI3s.",
#         flow_action_type=FlowActionType.NAVIGATE,
#         flow_action_screen="RECOMMENDED"
#     ),
# )

# wa.send_location(
#     to=ME,
#     latitude=37.4847483695049,
#     longitude=-122.1473373086664,
#     name='WhatsApp HQ',
#     address='Menlo Park, 1601 Willow Rd, United States',
# )

# wa.send_contact(
#     to=ME,
#     contact=Contact(
#         name=Contact.Name(formatted_name='David Lev', first_name='David'),
#         phones=[Contact.Phone(phone='1234567890', wa_id='1234567890', type='MOBILE')],
#         emails=[Contact.Email(email='test@test.com', type='WORK')],
#         urls=[Contact.Url(url='https://exmaple.com', type='HOME')],
#      )
# )

# wa.send_sticker(
#     to=ME,
#     sticker='web.webp',
#     mime_type="image/webp"
# )
