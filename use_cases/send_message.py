class SendMessageUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self, sender_id, receiver_id, content):
        return self.api_client.send_message(sender_id, receiver_id, content)