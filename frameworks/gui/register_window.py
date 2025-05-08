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
