import tkinter as tk
from tkinter import messagebox
from interface_adapters.controllers.user_controller import UserController
from frameworks.services.api_client import APIClient
from frameworks.gui.register_window import RegisterWindow
from frameworks.gui.message_window import MessageWindow
import requests

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
        tk.Button(self.root, text="Créer un compte", command=self.open_register).pack()

        self.root.mainloop()

    def open_register(self):
        self.root.destroy()
        RegisterWindow()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showwarning("Champs requis", "Veuillez remplir tous les champs")
            return

        try:
            response = self.controller.login(email, password)
            print("Réponse login dans LoginWindow :", response)  # Journalisation temporaire
            user = response['user']
            print("Utilisateur extrait :", user)  # Journalisation temporaire
            messagebox.showinfo("Succès", f"Connecté : {user['email']}")
            self.api_client.set_token(response['token'])
            self.root.destroy()
            MessageWindow(sender_id=user['_id'])
        except requests.exceptions.JSONDecodeError as e:
            messagebox.showerror("Erreur", f"Réponse du serveur invalide : format JSON incorrect - {e}")
        except requests.exceptions.ConnectionError as e:
            messagebox.showerror("Erreur", f"Impossible de se connecter au serveur : {e}")
        except requests.exceptions.HTTPError as e:
            messagebox.showerror("Erreur", f"Erreur HTTP : {e}")
        except KeyError as e:
            messagebox.showerror("Erreur", f"Réponse inattendue du serveur : clé manquante {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Connexion échouée : {type(e).__name__} - {e}")