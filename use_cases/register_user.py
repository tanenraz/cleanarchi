class RegisterUserUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self, name, email, password):
        return self.api_client.register(name, email, password)