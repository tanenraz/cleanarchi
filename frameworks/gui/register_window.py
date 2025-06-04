import tkinter as tk
from tkinter import messagebox
from interface_adapters.controllers.user_controller import UserController
from frameworks.services.api_client import APIClient


class RegisterWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Inscription")
        self.root.geometry("420x620+100+100")  # Format: width x height + x_offset + y_offset

        self.root.configure(bg="#f0f0f0")
        self.root.minsize(420, 620)
        self.root.resizable(False, False)
        

        self.api_client = APIClient()
        self.controller = UserController(self.api_client)

        self.frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        self.frame.pack(expand=True, fill="both", padx=40, pady=40)

        self.frame.columnconfigure(0, weight=1)

        tk.Label(self.frame, text="Créer un compte", font=("Helvetica", 16, "bold"), bg="#f0f0f0").grid(row=0, column=0, pady=(0, 20))

        tk.Label(self.frame, text="Nom", font=("Helvetica", 12), bg="#f0f0f0", anchor="w").grid(row=1, column=0, sticky="ew")
        self.name_entry = tk.Entry(self.frame, font=("Helvetica", 11))
        self.name_entry.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        tk.Label(self.frame, text="Email", font=("Helvetica", 12), bg="#f0f0f0", anchor="w").grid(row=3, column=0, sticky="ew")
        self.email_entry = tk.Entry(self.frame, font=("Helvetica", 11))
        self.email_entry.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        tk.Label(self.frame, text="Mot de passe", font=("Helvetica", 12), bg="#f0f0f0", anchor="w").grid(row=5, column=0, sticky="ew")
        self.password_entry = tk.Entry(self.frame, show="*", font=("Helvetica", 11))
        self.password_entry.grid(row=6, column=0, sticky="ew", pady=(0, 20))

        tk.Button(
            self.frame, text="S'inscrire", command=self.register,
            font=("Helvetica", 11), bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5
        ).grid(row=7, column=0, sticky="ew")

        tk.Button(
            self.frame, text="Retour à la connexion", command=self.back_to_login,
            font=("Helvetica", 10), bg="#2196F3", fg="white", relief="flat", padx=10, pady=5
        ).grid(row=8, column=0, sticky="ew", pady=(10, 0))

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

    def back_to_login(self):
        from frameworks.gui.login_window import LoginWindow
        self.root.destroy()
        LoginWindow()    

        