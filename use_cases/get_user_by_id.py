class GetUserByIdUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self, user_id):
        return self.api_client.get_user_by_id(user_id)