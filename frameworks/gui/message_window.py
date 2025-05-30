import os
import tkinter as tk
from tkinter import ttk, messagebox
import base64
import logging
from PIL import Image, ImageTk

from interface_adapters.controllers.message_controller import MessageController
from interface_adapters.presenters.message_presenter import MessagePresenter
from frameworks.services.api_client import APIClient

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MessageWindow:
    def __init__(self, sender_id):
        self.root = tk.Tk()
        self.root.title("Messagerie")
        self.root.geometry("600x600")

        # Clean Architecture Dependencies
        self.api_client = APIClient()
        self.controller = MessageController(self.api_client)
        self.presenter = MessagePresenter()

        # Business Logic State
        self.sender_id = sender_id
        self.receiver_id = None
        self.sender_aes_key = None
        self.receiver_aes_key = None

        # Initialize UI
        self._setup_ui()
        self._load_sender_info()
        self._setup_callbacks()
        self.load_users()

        self.root.mainloop()

    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        # Image de profil
        img_path = os.path.join("static", "profile.jpg")
        img = Image.open(img_path).resize((30, 30))
        self.profile_img_left = ImageTk.PhotoImage(img)
        self.profile_img_right = ImageTk.PhotoImage(img.transpose(Image.FLIP_LEFT_RIGHT))

        # Top frame pour sélection utilisateur
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill='x', pady=5)
        tk.Label(top_frame, text="Destinataire :").pack(side=tk.LEFT, padx=5)
        self.user_select = ttk.Combobox(top_frame, state="readonly")
        self.user_select.pack(side=tk.LEFT)
        self.user_select.bind("<<ComboboxSelected>>", self.on_user_selected)

        # Message display area
        self.text_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.text_frame.pack(expand=True, fill='both')
        self.canvas = tk.Canvas(self.text_frame, bg="#f0f0f0")
        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.canvas.yview)
        self.message_container = tk.Frame(self.canvas, bg="#f0f0f0")
        self.canvas.create_window((0, 0), window=self.message_container, anchor='nw', width=580)
        
        self.message_container.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Input area
        bottom_frame = tk.Frame(self.root, bg="#ffffff")
        bottom_frame.pack(fill="x", side="bottom")
        self.entry = tk.Entry(bottom_frame, width=50)
        self.entry.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)
        self.send_btn = tk.Button(
            bottom_frame, text="Envoyer", command=self.send, 
            bg="#007bff", fg="white"
        )
        self.send_btn.pack(side=tk.RIGHT, padx=10)

    def _load_sender_info(self):
        """Charge les informations du sender"""
        try:
            sender_info = self.controller.get_user_by_id(self.sender_id)
            # Uncomment when encryption is needed
            # self.sender_aes_key = base64.b64decode(sender_info['key'])
            # logger.debug(f"Clé AES sender : {self.sender_aes_key.hex()}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des infos sender : {e}")

    def _setup_callbacks(self):
        """Configure les callbacks"""
        self.controller.set_message_callback(self.on_message_received)

    def load_users(self):
        """Charge la liste des utilisateurs disponibles"""
        try:
            users = self.controller.get_users()
            user_dict = self.presenter.format_user_list(users, self.sender_id)
            
            if not user_dict:
                messagebox.showwarning("Aucun utilisateur", "Aucun autre utilisateur disponible.")
                self._set_no_users_available()
            else:
                self._populate_user_selection(user_dict)
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des utilisateurs : {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les utilisateurs : {e}")

    def _set_no_users_available(self):
        """Configure l'UI quand aucun utilisateur n'est disponible"""
        self.user_select['values'] = ["Aucun utilisateur"]
        self.user_select.set("Aucun utilisateur")
        self.user_dict = {}

    def _populate_user_selection(self, user_dict):
        """Peuple la sélection d'utilisateurs"""
        self.user_dict = user_dict
        self.user_select['values'] = list(user_dict.keys())
        self.user_select.set(list(user_dict.keys())[0])
        self.on_user_selected(None)

    def on_user_selected(self, event):
        """Gère la sélection d'un utilisateur"""
        selected_name = self.user_select.get()
        if selected_name in self.user_dict:
            self.receiver_id = self.user_dict[selected_name]
            logger.debug(f"Destinataire sélectionné : {self.receiver_id}")
            self._load_receiver_info()
            self.refresh_messages()

    def _load_receiver_info(self):
        """Charge les informations du receiver"""
        try:
            receiver_info = self.controller.get_user_by_id(self.receiver_id)
            # Uncomment when encryption is needed
            # self.receiver_aes_key = base64.b64decode(receiver_info['key'])
            # logger.debug(f"Clé AES receiver : {self.receiver_aes_key.hex()}")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la clé du receiver : {e}")
            self.receiver_aes_key = None

    def send(self):
        """Envoie un message"""
        if not self._validate_send_conditions():
            return

        content = self.entry.get().strip()
        try:
            self.controller.send_message(self.sender_id, self.receiver_id, content)
            self.entry.delete(0, tk.END)
            self.refresh_messages()
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message : {e}")
            messagebox.showerror("Erreur", f"Échec de l'envoi du message : {e}")

    def _validate_send_conditions(self):
        """Valide les conditions d'envoi d'un message"""
        if not self.receiver_id:
            messagebox.showwarning("Aucun destinataire", "Veuillez sélectionner un destinataire valide")
            return False
        
        content = self.entry.get().strip()
        if not content:
            messagebox.showwarning("Message vide", "Veuillez entrer un message")
            return False
        
        return True

    def on_message_received(self, message):
        """Callback pour les nouveaux messages reçus"""
        if self._is_message_for_current_conversation(message):
            try:
                decrypted_content = self._decrypt_message_content(message)
                self.display_message(message['senderId'], decrypted_content)
            except Exception as e:
                logger.error(f"Erreur de déchiffrement : {e}")
                self.display_message(message['senderId'], "[Erreur de déchiffrement]")

    def _is_message_for_current_conversation(self, message):
        """Vérifie si le message appartient à la conversation courante"""
        return (
            (message.get('senderId') == self.sender_id and message.get('receiverId') == self.receiver_id) or
            (message.get('senderId') == self.receiver_id and message.get('receiverId') == self.sender_id)
        )

    def _decrypt_message_content(self, message):
        """Décrypte le contenu d'un message"""
        content = message.get('content', {})
        encrypted = content.get(
            'forSender' if message['senderId'] == self.sender_id else 'forReceiver', 
            ''
        )
        
        # For now, return the encrypted content as-is since encryption is commented out
        # When encryption is enabled, use:
        # aes_key = self.sender_aes_key if message['senderId'] == self.sender_id else self.receiver_aes_key
        # return self.controller.decrypt_message(encrypted, aes_key)
        
        return encrypted or message.get('content', '')

    def refresh_messages(self):
        """Actualise l'affichage des messages"""
        if not self.receiver_id:
            return
        
        try:
            messages = self.controller.get_messages(self.sender_id, self.receiver_id)
            self._clear_message_display()
            self._display_all_messages(messages)
        except Exception as e:
            logger.error(f"Erreur dans refresh_messages : {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les messages : {e}")

    def _clear_message_display(self):
        """Efface l'affichage des messages"""
        for widget in self.message_container.winfo_children():
            widget.destroy()

    def _display_all_messages(self, messages):
        """Affiche tous les messages"""
        for msg in messages:
            try:
                formatted_msg = self.presenter.format_message_for_display(msg, self.sender_id)
                decrypted_content = self._decrypt_message_content(msg)
                self.display_message(formatted_msg['sender_id'], decrypted_content)
            except Exception as e:
                logger.error(f"Erreur dans refresh_messages : {e}")
                self.display_message(msg['senderId'], "[Erreur de déchiffrement]")

    def display_message(self, sender_id, text):
        """Affiche un message dans l'interface"""
        is_me = sender_id == self.sender_id
        bubble_bg = "#DCF8C6" if is_me else "#FFFFFF"
        side = tk.RIGHT if is_me else tk.LEFT
        anchor = "e" if is_me else "w"
        
        container = tk.Frame(self.message_container, bg="#f0f0f0")
        container.pack(side=tk.TOP, fill="x", padx=10, pady=4)
        
        inner = tk.Frame(container, bg="#f0f0f0", width=400)
        inner.pack(side=side, anchor=anchor)
        
        img = self.profile_img_right if is_me else self.profile_img_left
        profile_label = tk.Label(inner, image=img, bg="#f0f0f0")
        profile_label.image = img
        
        msg_label = tk.Label(
            inner, text=text, bg=bubble_bg, fg="black",
            wraplength=350, padx=10, pady=5, justify="left",
            font=("Arial", 10), relief=tk.SOLID, bd=1
        )
        
        if is_me:
            profile_label.pack(side=tk.RIGHT, padx=(0, 5))
            msg_label.pack(side=tk.RIGHT)
        else:
            profile_label.pack(side=tk.LEFT, padx=(5, 0))
            msg_label.pack(side=tk.LEFT)
        
        self.root.update_idletasks()
        self.canvas.yview_moveto(1.0)