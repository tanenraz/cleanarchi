### messenger_frontend/entities/message.py

class Message:
    def __init__(self, sender_id, receiver_id, content):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content


### messenger_frontend/entities/user.py

class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email


### messenger_frontend/use_cases/send_message.py

class SendMessageUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self, sender_id, receiver_id, content):
        return self.api_client.send_message(sender_id, receiver_id, content)


### messenger_frontend/use_cases/get_messages.py

class GetMessagesUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self, user1_id, user2_id):
        return self.api_client.get_messages(user1_id, user2_id)


### messenger_frontend/use_cases/login_user.py

class LoginUserUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self, email, password):
        return self.api_client.login(email, password)


### messenger_frontend/use_cases/register_user.py

class RegisterUserUseCase:
    def __init__(self, api_client):
        self.api_client = api_client

    def execute(self, name, email, password):
        return self.api_client.register(name, email, password)


### messenger_frontend/interface_adapters/controllers/message_controller.py

from use_cases.send_message import SendMessageUseCase
from use_cases.get_messages import GetMessagesUseCase

class MessageController:
    def __init__(self, api_client):
        self.send_use_case = SendMessageUseCase(api_client)
        self.get_use_case = GetMessagesUseCase(api_client)

    def send_message(self, sender_id, receiver_id, content):
        return self.send_use_case.execute(sender_id, receiver_id, content)

    def get_messages(self, user1_id, user2_id):
        return self.get_use_case.execute(user1_id, user2_id)


### messenger_frontend/interface_adapters/controllers/user_controller.py

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


### messenger_frontend/frameworks/services/api_client.py

import requests

class APIClient:
    BASE_URL = "http://localhost:3000/api/users"

    def login(self, email, password):
        res = requests.post(f"{self.BASE_URL}/login", json={"email": email, "password": password})
        res.raise_for_status()
        return res.json()

    def register(self, name, email, password):
        res = requests.post(f"{self.BASE_URL}/register", json={"name": name, "email": email, "password": password})
        res.raise_for_status()
        return res.json()

    def send_message(self, sender_id, receiver_id, content):
        res = requests.post("http://localhost:3000/messages/send", json={
            "senderId": sender_id,
            "receiverId": receiver_id,
            "content": content
        })
        return res.json()

    def get_messages(self, user1_id, user2_id):
        res = requests.get(f"http://localhost:3000/messages/{user1_id}/{user2_id}")
        return res.json()


### messenger_frontend/frameworks/gui/message_window.py

import tkinter as tk
from interface_adapters.controllers.message_controller import MessageController
from frameworks.services.api_client import APIClient

class MessageWindow:
    def __init__(self, sender_id, receiver_id):
        self.root = tk.Tk()
        self.root.title("Messagerie")

        self.api_client = APIClient()
        self.controller = MessageController(self.api_client)

        self.sender_id = sender_id
        self.receiver_id = receiver_id

        self.text_display = tk.Text(self.root, state='disabled', height=20, width=50)
        self.text_display.pack()

        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(side=tk.LEFT)

        self.send_btn = tk.Button(self.root, text="Envoyer", command=self.send)
        self.send_btn.pack(side=tk.LEFT)

        self.refresh_messages()
        self.root.mainloop()

    def send(self):
        content = self.entry.get()
        self.controller.send_message(self.sender_id, self.receiver_id, content)
        self.entry.delete(0, tk.END)
        self.refresh_messages()

    def refresh_messages(self):
        messages = self.controller.get_messages(self.sender_id, self.receiver_id)
        self.text_display.config(state='normal')
        self.text_display.delete(1.0, tk.END)
        for msg in messages:
            self.text_display.insert(tk.END, f"{msg['senderId']}: {msg['content']}\n")
        self.text_display.config(state='disabled')


### messenger_frontend/frameworks/gui/register_window.py

import tkinter as tk
from tkinter import messagebox
from interface_adapters.controllers.user_controller import UserController
from frameworks.services.api_client import APIClient

class RegisterWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Inscription")

        self.api_client = APIClient()
        self.controller = UserController(self.api_client)

        tk.Label(self.root, text="Nom").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        tk.Label(self.root, text="Email").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Label(self.root, text="Mot de passe").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="S'inscrire", command=self.register).pack()

        self.root.mainloop()

    def register(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not name or not email or not password:
            messagebox.showwarning("Champs requis", "Veuillez remplir tous les champs")
            return

        user = self.controller.register(name, email, password)
        messagebox.showinfo("Succès", f"Utilisateur inscrit avec succès : {user}")
        self.root.destroy()


### messenger_frontend/frameworks/gui/login_window.py

import tkinter as tk
from tkinter import messagebox
from interface_adapters.controllers.user_controller import UserController
from frameworks.services.api_client import APIClient

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connexion")

        self.api_client = APIClient()
        self.controller = UserController(self.api_client)

        tk.Label(self.root, text="Email").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Label(self.root, text="Mot de passe").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Se connecter", command=self.login).pack()

        self.root.mainloop()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showwarning("Champs requis", "Veuillez remplir tous les champs")
            return

        try:
            user = self.controller.login(email, password)
            messagebox.showinfo("Succès", f"Connecté : {user['name']}")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Connexion échouée : {e}")


### messenger_frontend/main.py

from frameworks.gui.register_window import RegisterWindow
from frameworks.gui.login_window import LoginWindow

# Pour tester l'inscription
# RegisterWindow()

# Pour tester la connexion
LoginWindow()
