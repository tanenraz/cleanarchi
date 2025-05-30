# messenger_frontend/interface_adapters/controllers/message_controller.py (Updated)
from use_cases.send_message import SendMessageUseCase
from use_cases.get_messages import GetMessagesUseCase
from use_cases.get_users import GetUsersUseCase
from use_cases.get_user_by_id import GetUserByIdUseCase
from use_cases.decrypt_message import DecryptMessageUseCase

class MessageController:
    def __init__(self, api_client):
        self.send_use_case = SendMessageUseCase(api_client)
        self.get_use_case = GetMessagesUseCase(api_client)
        self.get_users_use_case = GetUsersUseCase(api_client)
        self.get_user_by_id_use_case = GetUserByIdUseCase(api_client)
        self.decrypt_use_case = DecryptMessageUseCase()
        self.message_callback = None

    def send_message(self, sender_id, receiver_id, content):
        return self.send_use_case.execute(sender_id, receiver_id, content)

    def get_messages(self, user1_id, user2_id):
        return self.get_use_case.execute(user1_id, user2_id)

    def get_users(self):
        return self.get_users_use_case.execute()

    def get_user_by_id(self, user_id):
        return self.get_user_by_id_use_case.execute(user_id)

    def decrypt_message(self, encrypted_content, aes_key):
        return self.decrypt_use_case.execute(encrypted_content, aes_key)

    def set_message_callback(self, callback):
        self.message_callback = callback