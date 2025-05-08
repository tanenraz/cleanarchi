class LoginUserUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self, email, password):
        return self.api_client.login(email, password)