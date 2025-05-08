class GetMessagesUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self, user1_id, user2_id):
        return self.api_client.get_messages(user1_id, user2_id)
