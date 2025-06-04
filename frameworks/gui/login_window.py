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
        self.root.geometry("420x620+260+100")  # Format: width x height + x_offset + y_offset
        self.root.configure(bg="#f0f0f0")
        self.root.minsize(420,620)
        
        
        

        self.api_client = APIClient()
        self.controller = UserController(self.api_client)

        self.frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        self.frame.pack(expand=False, fill="both", padx=40, pady=40)

        self.frame.columnconfigure(0, weight=1)

        tk.Label(self.frame, text="Connexion", font=("Helvetica", 16, "bold"), bg="#f0f0f0").grid(row=0, column=0, pady=(0, 20))

        tk.Label(self.frame, text="Email", font=("Helvetica", 12), bg="#f0f0f0", anchor="w").grid(row=1, column=0, sticky="ew")
        self.email_entry = tk.Entry(self.frame, font=("Helvetica", 11))
        self.email_entry.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        tk.Label(self.frame, text="Mot de passe", font=("Helvetica", 12), bg="#f0f0f0", anchor="w").grid(row=3, column=0, sticky="ew")
        self.password_entry = tk.Entry(self.frame, show="*", font=("Helvetica", 11))
        self.password_entry.grid(row=4, column=0, sticky="ew", pady=(0, 20))

        self.login_button = tk.Button(
            self.frame, text="Se connecter", command=self.login,
            font=("Helvetica", 11), bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5
        )
        self.login_button.grid(row=5, column=0, sticky="ew")

        self.register_button = tk.Button(
            self.frame, text="Créer un compte", command=self.open_register,
            font=("Helvetica", 10), bg="#2196F3", fg="white", relief="flat", padx=10, pady=5
        )
        self.register_button.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        self.root.resizable(False,False)
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
            user = response['user']
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
