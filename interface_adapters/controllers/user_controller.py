from use_cases.login_user import LoginUserUseCase
from use_cases.register_user import RegisterUserUseCase

class UserController:
    def __init__(self, api_client):
        self.login_use_case = LoginUserUseCase(api_client)
        self.register_use_case = RegisterUserUseCase(api_client)

    def login(self, email, password):
        return self.login_use_case.execute(email, password)

    def register(self, name, email, password):
        return self.register_use_case.execute(name, email, password)
    