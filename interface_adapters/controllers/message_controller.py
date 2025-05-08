class MessageController:
    def __init__(self, api_client):
        self.api_client = api_client

    def send_message(self, sender_id, receiver_id, content):
        return self.api_client.send_message(sender_id, receiver_id, content)

    def get_messages(self, user1_id, user2_id):
        return self.api_client.get_messages(user1_id, user2_id)

    def get_users(self):
        return self.api_client.get_users()

    def set_message_callback(self, callback):
        self.api_client.set_message_callback(callback)