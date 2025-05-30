# messenger_frontend/frameworks/services/api_client.py (Updated)
import requests

class APIClient:
    BASE_URL = "http://localhost:3000/api/users"
    MESSAGES_URL = "http://localhost:3000/api/message"

    def __init__(self):
        self.token = None
        self.headers = {"Content-Type": "application/json"}

    def set_token(self, token):
        """Définit le token d'authentification"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"

    def _get_headers(self):
        """Retourne les headers avec le token si disponible"""
        return self.headers

    def login(self, email, password):
        res = requests.post(f"{self.BASE_URL}/login", 
                          json={"email": email, "password": password},
                          headers=self._get_headers())
        res.raise_for_status()
        response_data = res.json()
        
        # Si le login retourne un token, on le sauvegarde automatiquement
        if 'token' in response_data:
            self.set_token(response_data['token'])
            
        return response_data

    def register(self, name, email, password):
        res = requests.post(f"{self.BASE_URL}/register", 
                          json={"name": name, "email": email, "password": password},
                          headers=self._get_headers())
        res.raise_for_status()
        response_data = res.json()
        
        # Si le register retourne un token, on le sauvegarde automatiquement
        if 'token' in response_data:
            self.set_token(response_data['token'])
            
        return response_data

    def send_message(self, sender_id, receiver_id, content):
        res = requests.post(f"{self.MESSAGES_URL}/send", 
                          json={
                              "senderId": sender_id,
                              "receiverId": receiver_id,
                              "content": content
                          },
                          headers=self._get_headers())
        res.raise_for_status()
        return res.json()

    def get_messages(self, user1_id, user2_id):
        res = requests.get(f"{self.MESSAGES_URL}/{user1_id}/{user2_id}",
                          headers=self._get_headers())
        res.raise_for_status()
        return res.json()

    def get_users(self):
        res = requests.get(f"{self.BASE_URL}/getAll",
                          headers=self._get_headers())
        res.raise_for_status()
        return res.json()

    def get_user_by_id(self, user_id):
        res = requests.get(f"{self.BASE_URL}/getById/{user_id}",
                          headers=self._get_headers())
        res.raise_for_status()
        return res.json()