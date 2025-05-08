import requests
import json
import socketio
import time

class APIClient:
    BASE_URL = "http://localhost:3000/api/users"
    WS_URL = "http://localhost:3000"

    def __init__(self):
        self.token = None
        self.sio = socketio.Client()
        self.message_callback = None
        self.setup_socket_events()

    def setup_socket_events(self):
        @self.sio.event
        def connect():
            print("🟢 Connexion socket.io établie")

        @self.sio.event
        def disconnect():
            print("🔴 Connexion socket.io fermée")

        @self.sio.event
        def receive_message(data):
            if self.message_callback:
                self.message_callback(data)

        @self.sio.event
        def error(data):
            print(f"Erreur socket.io : {data}")

    def set_token(self, token):
        self.token = token
        if token and not self.sio.connected:
            self.sio.connect(self.WS_URL, auth={"token": self.token})

    def set_message_callback(self, callback):
        self.message_callback = callback

    def send_message(self, sender_id, receiver_id, content):
        if not self.sio.connected:
            print("Socket.io non connecté, tentative de reconnexion...")
            try:
                self.sio.connect(self.WS_URL, auth={"token": self.token})
                time.sleep(1)  # Attendre que la connexion s'établisse
            except socketio.exceptions.ConnectionError as e:
                print(f"Échec de la reconnexion : {e}")
                raise ValueError(f"Socket.io non connecté : {e}")
        self.sio.emit("send_message", {
            "senderId": sender_id,
            "receiverId": receiver_id,
            "content": content
        })

    def clean_response(self, text):
        """Nettoie la réponse JSON en extrayant le premier objet ou tableau JSON valide."""
        if not text:
            return text
        try:
            # Trouver le premier objet ou tableau JSON valide
            decoder = json.JSONDecoder()
            obj, end = decoder.raw_decode(text)
            return json.dumps(obj)  # Convertir en chaîne JSON valide
        except json.JSONDecodeError as e:
            print(f"Erreur lors du nettoyage JSON : {e}, Texte brut : {text}")
            # Tentative de couper après la dernière accolade/parenthèse fermante
            brace_count = 0
            bracket_count = 0
            last_valid = 0
            for i, char in enumerate(text):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and bracket_count == 0:
                        last_valid = i + 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if brace_count == 0 and bracket_count == 0:
                        last_valid = i + 1
            if last_valid > 0:
                cleaned = text[:last_valid]
                try:
                    json.loads(cleaned)  # Vérifier si valide
                    return cleaned
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"Impossible de nettoyer la réponse JSON : {text}")

    def login(self, email, password):
        try:
            res = requests.post(f"{self.BASE_URL}/login", json={"email": email, "password": password})
            res.raise_for_status()
            print("Réponse brute du serveur (login) :", res.text)
            if not res.text:
                raise ValueError("Réponse vide du serveur")
            cleaned_text = self.clean_response(res.text)
            print("Réponse nettoyée (login) :", cleaned_text)
            return json.loads(cleaned_text)
        except requests.exceptions.JSONDecodeError as e:
            print(f"Erreur de parsing JSON : {e}, Contenu brut : {res.text}")
            raise ValueError(f"Réponse du serveur non-JSON : {res.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            raise
        except ValueError as e:
            print(f"Erreur de validation : {e}")
            raise

    def register(self, name, email, password):
        try:
            res = requests.post(f"{self.BASE_URL}/register", json={"name": name, "email": email, "password": password})
            res.raise_for_status()
            print("Réponse brute du serveur (register) :", res.text)
            if not res.text:
                raise ValueError("Réponse vide du serveur")
            cleaned_text = self.clean_response(res.text)
            print("Réponse nettoyée (register) :", cleaned_text)
            return json.loads(cleaned_text)
        except requests.exceptions.JSONDecodeError as e:
            print(f"Erreur de parsing JSON : {e}, Contenu brut : {res.text}")
            raise ValueError(f"Réponse du serveur non-JSON : {res.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            raise
        except ValueError as e:
            print(f"Erreur de validation : {e}")
            raise

    def get_users(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            res = requests.get(f"{self.BASE_URL}/getAll", headers=headers)
            res.raise_for_status()
            print("Réponse brute du serveur (get_users) :", res.text)
            if not res.text:
                raise ValueError("Réponse vide du serveur")
            cleaned_text = self.clean_response(res.text)
            print("Réponse nettoyée (get_users) :", cleaned_text)
            return json.loads(cleaned_text)
        except requests.exceptions.JSONDecodeError as e:
            print(f"Erreur de parsing JSON : {e}, Contenu brut : {res.text}")
            raise ValueError(f"Réponse du serveur non-JSON : {res.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            raise
        except ValueError as e:
            print(f"Erreur de validation : {e}")
            raise

    def get_messages(self, user1_id, user2_id):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        res = requests.get(f"http://localhost:3000/api/message/{user1_id}/{user2_id}", headers=headers)
        return res.json()