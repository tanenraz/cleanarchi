# messenger_frontend/use_cases/get_users.py
class GetUsersUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self):
        return self.api_client.get_users()