import tkinter as tk
from tkinter import ttk, messagebox
from interface_adapters.controllers.message_controller import MessageController
from frameworks.services.api_client import APIClient

class MessageWindow:
    def __init__(self, sender_id):
        self.root = tk.Tk()
        self.root.title("Messagerie")

        self.api_client = APIClient()
        self.controller = MessageController(self.api_client)

        self.sender_id = sender_id
        self.receiver_id = None

        # Dropdown pour choisir l'utilisateur destinataire
        tk.Label(self.root, text="Destinataire :").pack()
        self.user_select = ttk.Combobox(self.root, state="readonly")
        self.user_select.pack()
        self.user_select.bind("<<ComboboxSelected>>", self.on_user_selected)

        # Zone d'affichage des messages
        self.text_display = tk.Text(self.root, state='disabled', height=20, width=50)
        self.text_display.pack()

        # Champ d'entrée du message
        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(side=tk.LEFT)

        self.send_btn = tk.Button(self.root, text="Envoyer", command=self.send)
        self.send_btn.pack(side=tk.LEFT)

        # Définir le callback pour les messages WebSocket
        self.controller.set_message_callback(self.on_message_received)

        # Charger la liste des utilisateurs
        self.load_users()

        self.root.mainloop()

    def load_users(self):
        try:
            self.users = self.controller.get_users()
            print("Utilisateurs reçus :", self.users)
            self.user_dict = {user['email']: user['_id'] for user in self.users if user['_id'] != self.sender_id}
            if not self.user_dict:
                messagebox.showwarning("Aucun utilisateur", "Aucun autre utilisateur disponible.")
                self.user_select['values'] = ["Aucun utilisateur"]
                self.user_select.set("Aucun utilisateur")
            else:
                self.user_select['values'] = list(self.user_dict.keys())
                self.user_select.set(list(self.user_dict.keys())[0])
                self.on_user_selected(None)
        except Exception as e:
            print("Erreur lors du chargement des utilisateurs :", e)
            messagebox.showerror("Erreur", f"Impossible de charger les utilisateurs : {e}")
            self.user_select['values'] = ["Erreur de chargement"]
            self.user_select.set("Erreur de chargement")

    def on_user_selected(self, event):
        selected_name = self.user_select.get()
        if selected_name in self.user_dict:
            self.receiver_id = self.user_dict[selected_name]
            print("Destinataire sélectionné :", self.receiver_id)
            self.refresh_messages()

    def send(self):
        if not self.receiver_id:
            messagebox.showwarning("Aucun destinataire", "Veuillez sélectionner un destinataire valide")
            return

        content = self.entry.get().strip()
        if not content:
            messagebox.showwarning("Message vide", "Veuillez entrer un message")
            return

        try:
            self.controller.send_message(self.sender_id, self.receiver_id, content)
            self.entry.delete(0, tk.END)
        except Exception as e:
            print("Erreur lors de l'envoi du message :", e)
            messagebox.showerror("Erreur", f"Échec de l'envoi du message : {e}")

    def on_message_received(self, message):
        print("Message reçu pour affichage :", message)  # Journalisation
        # Filtrer les messages pour la conversation actuelle
        if (message.get('senderId') == self.sender_id and message.get('receiverId') == self.receiver_id) or \
           (message.get('senderId') == self.receiver_id and message.get('receiverId') == self.sender_id):
            self.text_display.config(state='normal')
            self.text_display.insert(tk.END, f"{message['senderId']}: {message['content']}\n")
            self.text_display.config(state='disabled')
            self.text_display.see(tk.END)

    def refresh_messages(self):
        if not self.receiver_id:
            return

        try:
            messages = self.controller.get_messages(self.sender_id, self.receiver_id)
            print("Messages reçus :", messages)
            self.text_display.config(state='normal')
            self.text_display.delete(1.0, tk.END)
            for msg in messages:
                self.text_display.insert(tk.END, f"{msg['senderId']}: {msg['content']}\n")
            self.text_display.config(state='disabled')
            self.text_display.see(tk.END)
        except Exception as e:
            print("Erreur dans refresh_messages :", e)
            messagebox.showerror("Erreur", f"Impossible de charger les messages : {e}")