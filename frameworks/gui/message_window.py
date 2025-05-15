import os
import tkinter as tk
from tkinter import ttk, messagebox
from interface_adapters.controllers.message_controller import MessageController
from frameworks.services.api_client import APIClient
from Crypto.Cipher import AES
import base64
import logging
from PIL import Image, ImageTk

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MessageWindow:
    def __init__(self, sender_id):
        self.root = tk.Tk()
        self.root.title("Messagerie")
        self.root.geometry("600x600")

        self.api_client = APIClient()
        self.controller = MessageController(self.api_client)

        self.sender_id = sender_id
        self.receiver_id = None

        # Clé AES factice (remplacer par la vraie clé)
        self.aes_key = b'ThisIsA32ByteLongSecretKeyForAES!!'

        logger.debug(f"Clé AES utilisée : {self.aes_key.hex()}")
        # Images de profil
        img_path = os.path.join("static", "profile.jpg")
        img = Image.open(img_path).resize((30, 30))
        self.profile_img_left = ImageTk.PhotoImage(img)
        self.profile_img_right = ImageTk.PhotoImage(img.transpose(Image.FLIP_LEFT_RIGHT))

        # Haut : sélection utilisateur
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill='x', pady=5)

        tk.Label(top_frame, text="Destinataire :").pack(side=tk.LEFT, padx=5)
        self.user_select = ttk.Combobox(top_frame, state="readonly")
        self.user_select.pack(side=tk.LEFT)
        self.user_select.bind("<<ComboboxSelected>>", self.on_user_selected)

        # Centre : affichage messages
        self.text_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.text_frame.pack(expand=True, fill='both')

        self.canvas = tk.Canvas(self.text_frame, bg="#f0f0f0")
        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.canvas.yview)
        self.message_container = tk.Frame(self.canvas, bg="#f0f0f0")

        # Ajuster la largeur du Canvas
        self.canvas.create_window((0, 0), window=self.message_container, anchor='nw', width=580)  # Largeur fixe pour l'alignement
        self.message_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bas : champ de saisie + bouton
        bottom_frame = tk.Frame(self.root, bg="#ffffff")
        bottom_frame.pack(fill="x", side="bottom")

        self.entry = tk.Entry(bottom_frame, width=50)
        self.entry.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)

        self.send_btn = tk.Button(bottom_frame, text="Envoyer", command=self.send, bg="#007bff", fg="white")
        self.send_btn.pack(side=tk.RIGHT, padx=10)

        self.controller.set_message_callback(self.on_message_received)
        self.load_users()

        self.root.mainloop()

    def load_users(self):
        try:
            self.users = self.controller.get_users()
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
            logger.error(f"Erreur lors du chargement des utilisateurs : {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les utilisateurs : {e}")

    def on_user_selected(self, event):
        selected_name = self.user_select.get()
        if selected_name in self.user_dict:
            self.receiver_id = self.user_dict[selected_name]
            logger.debug(f"Destinataire sélectionné : {self.receiver_id}")
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
            self.refresh_messages()
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message : {e}")
            messagebox.showerror("Erreur", f"Échec de l'envoi du message : {e}")

    def on_message_received(self, message):
        if (message.get('senderId') == self.sender_id and message.get('receiverId') == self.receiver_id) or \
           (message.get('senderId') == self.receiver_id and message.get('receiverId') == self.sender_id):
            try:
                content = message.get('content', {})
                encrypted_content = content.get('forSender' if message['senderId'] == self.sender_id else 'forReceiver', '')
                decrypted_content = self.decrypt_content(encrypted_content)
                self.display_message(message['senderId'], decrypted_content)
            except Exception as e:
                logger.error(f"Erreur de déchiffrement : {e}")
                self.display_message(message['senderId'], "[Erreur de déchiffrement]")

    def display_message(self, sender_id, text):
        is_me = sender_id == self.sender_id
        bubble_bg = "#DCF8C6" if is_me else "#FFFFFF"
        side = tk.RIGHT if is_me else tk.LEFT
        anchor = "e" if is_me else "w"

        # Conteneur principal pour le message
        container = tk.Frame(self.message_container, bg="#f0f0f0")
        container.pack(side=tk.TOP, fill="x", padx=10, pady=4)

        # Conteneur interne pour aligner le contenu
        inner = tk.Frame(container, bg="#f0f0f0", width=400)  # Largeur fixe pour un alignement clair
        inner.pack(side=side, anchor=anchor)

        # Image de profil
        img = self.profile_img_right if is_me else self.profile_img_left
        profile_label = tk.Label(inner, image=img, bg="#f0f0f0")
        profile_label.image = img  # Garder une référence

        # Bulle de message
        msg_label = tk.Label(
            inner,
            text=text,
            bg=bubble_bg,
            fg="black",
            wraplength=350,  # Réduire pour éviter des messages trop larges
            padx=10,
            pady=5,
            justify="left",
            font=("Arial", 10),
            relief=tk.SOLID,
            bd=1
        )

        # Ordre dans inner
        if is_me:
            profile_label.pack(side=tk.RIGHT, padx=(0, 5))
            msg_label.pack(side=tk.RIGHT)
        else:
            profile_label.pack(side=tk.LEFT, padx=(5, 0))
            msg_label.pack(side=tk.LEFT)

        self.root.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def decrypt_content(self, encrypted_content):
        try:
            logger.debug(f"Déchiffrement de : {encrypted_content[:50]}... (longueur : {len(encrypted_content)})")
            cipher_text = base64.b64decode(encrypted_content)
            logger.debug(f"Texte chiffré (après Base64, longueur) : {len(cipher_text)} bytes")
            if len(cipher_text) < 16:
                raise ValueError("Texte chiffré trop court pour contenir un IV")
            iv = cipher_text[:16]
            encrypted_data = cipher_text[16:]
            logger.debug(f"IV : {base64.b64encode(iv).decode()}")
            logger.debug(f"Utilisation de la clé AES (longueur : {len(self.aes_key)} bytes)")
            cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
            padded_text = cipher.decrypt(encrypted_data)
            pad_length = padded_text[-1]
            if pad_length < 1 or pad_length > 16 or any(padded_text[-i] != pad_length for i in range(1, pad_length + 1)):
                raise ValueError("Padding PKCS7 invalide")
            unpadded_text = padded_text[:-pad_length]
            decrypted_text = unpadded_text.decode('utf-8')
            logger.debug(f"Texte déchiffré : {decrypted_text}")
            return decrypted_text
        except Exception as e:
            logger.error(f"Erreur dans decrypt_content : {e}")
            raise

    def refresh_messages(self):
        if not self.receiver_id:
            return
        try:
            messages = self.controller.get_messages(self.sender_id, self.receiver_id)
            logger.debug(f"Messages reçus : {messages}")
            for widget in self.message_container.winfo_children():
                widget.destroy()

            for msg in messages:
                try:
                    content = msg.get('content', {})
                    encrypted_content = content.get('forSender' if msg['senderId'] == self.sender_id else 'forReceiver', '')
                    logger.debug(f"Message ID {msg['_id']} - Contenu chiffré : {encrypted_content[:50]}...")
                    decrypted_content = self.decrypt_content(encrypted_content)
                    self.display_message(msg['senderId'], decrypted_content)
                except Exception as e:
                    logger.error(f"Erreur de déchiffrement dans refresh_messages : {e}")
                    self.display_message(msg['senderId'], "[Erreur de déchiffrement]")
        except Exception as e:
            logger.error(f"Erreur dans refresh_messages : {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les messages : {e}")