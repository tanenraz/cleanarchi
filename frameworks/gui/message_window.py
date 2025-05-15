import tkinter as tk
from tkinter import ttk, messagebox
from interface_adapters.controllers.message_controller import MessageController
from frameworks.services.api_client import APIClient
from Crypto.Cipher import AES
import base64
import logging

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MessageWindow:
    def __init__(self, sender_id):
        self.root = tk.Tk()
        self.root.title("Messagerie")

        self.api_client = APIClient()
        self.controller = MessageController(self.api_client)

        self.sender_id = sender_id
        self.receiver_id = None
        # Clé AES (32 bytes pour AES-256, à remplacer par la clé fournie à l'utilisateur)
        self.aes_key = b"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDqsTt5Dv3r3ORB\n9JZcHYYafcEAdCKr60T2YKgETiA5YSnI32S4zmjdZxWnkph/9Jr5ZE+x/eAfZDlb\nhQphRxDofdm0EPZVkwFXEJJS0XaoThsmo8LtPzEBSQQd/wGf1akI4D8n7OZmd2MQ\nIYAF1EkDQi6atOK9CPLwg+TJn5/Z/HmW7bxJg7wvfvPrerFhUdYSA3kHN2z+bNRI\nLnMPYzJiuRFDRTE8OadezhkQYIdlkAf1JBr1BJYDIb/xlw9fyuLf0bktpMDAXxYK\nqzsQi/913+VWQ9cNlN6FUuQZvrRaqpk/mX5JRSZOwbQ9K+Gfe1UK6sUxFN2A1deH\nhp9lIcBRAgMBAAECggEAGs+6ip7y1UI79Wj60HUy/83EAchCub879qWeLDe8qLF3\n85HJ0O8Lvddr+uPddii8l6clD6GAPDXX86OkRu62eMj/2PljGu2bZpXnEX0KgDnE\nEkr9Ftt0PsBXrxGV3uuqzu/HZ0lCHQygjZQ2KvRQjwW9i0EE8jGWh3GZ7orE2UMt\nohXR0tL5REV0X7hIJGqBJ2cZcAOxMLed31jYZ/gRDGW+rQZLkZlhidceTkpecli+\nLdd5/llEYP1pGWD6krBvLCaErAaifTV5EnDomrZUwCMvqN0MtJpfRPGmZMmRamCb\naLKkgs6EfkGzLVhEMYyJLoi19Tx/RcF4zGxe3UPIzQKBgQD4oxrGDewFXDS2B32P\nUF+vJTXeS5kMe7LlHzSgLUFFVfB52CyIyihrn2NOFR2rkhLNfPSPuIItmF1zNcAw\nTwPfb+/2dUsIg+COTBmJP1wWBCA8leYKgHP/YbcfMSOCB55cnirAjNDFd65nWto9\nbQFqBeiHcrIc8imHirZ/I18jGwKBgQDxpGnSncQ61aio3443jKq0R8fvFQci2O61\nGi4c2ShsBn/K/RmG1n4h0nljXSprg16S597a4Hz7BrE3nCPf7oQjLpWnanMBLKoU\n/zpdehnOwhG6diTq0tguuomRMcebF6eMA/CQNd8eCReyQ3qnc6gWVtXXpXpco0zL\nJyM9Bnt1AwKBgQDbXxU9T4VByXPcc0luDA0QPDWGF49Gu1FA5MKK3MLtCQEuj/Pj\nEPKO2kdE2k6eVThvw2MH91QsJHW3M+KI/P4+wsWm3yA/uBOFmVEijhuSdTt4GQ2p\nkGJIHg/y3mkkzdIEh6zSzKtavtjK6hcKAUYxJFtgPms2LNdFdrbEABJtpwKBgEeE\n1wFMSpjzReD9kbUlQBztpeJAQgVxWW1mm0FUkJ8waUBmGtkKwPg3uE/NclGx5xrp\n386+ZJ9Tgr4ny4JqsNdM4WRUoEc3tftS8y5ZhivoyqB6eUC7ONrTwQWlSyO/I4rQ\nW7IDD89u94F+cV4AYD6EYvRZeNbUSlVSdx6HvaCLAoGAAcdr5SoEAfBG9MFmzWli\n9gKWUJzSd3PWaB0xm6WU0eUfbi7deM0qjtnD3SI/do5ZQ7w/5MLcSQ5FUb89U8Vc\nv7ffh8B3ocSB29COVVCpdPNAelcjrw/4RAb7nhBJAtZJTJiTh55fBX+uBRVeJnlt\npVcY2Joa8QMM5haKU3S5veY=\n-----END PRIVATE KEY-----\n"

        logger.debug(f"Clé AES utilisée : {self.aes_key.hex()}")

        tk.Label(self.root, text="Destinataire :").pack()
        self.user_select = ttk.Combobox(self.root, state="readonly")
        self.user_select.pack()
        self.user_select.bind("<<ComboboxSelected>>", self.on_user_selected)

        self.text_display = tk.Text(self.root, state='disabled', height=20, width=50)
        self.text_display.pack()

        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(side=tk.LEFT)

        self.send_btn = tk.Button(self.root, text="Envoyer", command=self.send)
        self.send_btn.pack(side=tk.LEFT)

        self.controller.set_message_callback(self.on_message_received)

        self.load_users()

        self.root.mainloop()

    def load_users(self):
        try:
            self.users = self.controller.get_users()
            logger.debug(f"Utilisateurs reçus : {self.users}")
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
            logger.debug(f"Tentative d'envoi de message : {content} à {self.receiver_id}")
            self.controller.send_message(self.sender_id, self.receiver_id, content)
            self.entry.delete(0, tk.END)
            self.refresh_messages()
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message : {e}")
            messagebox.showerror("Erreur", f"Échec de l'envoi du message : {e}")

    def on_message_received(self, message):
        logger.debug(f"Message reçu pour affichage : {message}")
        if (message.get('senderId') == self.sender_id and message.get('receiverId') == self.receiver_id) or \
           (message.get('senderId') == self.receiver_id and message.get('receiverId') == self.sender_id):
            try:
                content = message.get('content', {})
                encrypted_content = content.get('forSender' if message['senderId'] == self.sender_id else 'forReceiver', '')
                logger.debug(f"Contenu chiffré (Base64) : {encrypted_content}")
                decrypted_content = self.decrypt_content(encrypted_content)
                self.text_display.config(state='normal')
                self.text_display.insert(tk.END, f"{message['senderId']}: {decrypted_content}\n")
                self.text_display.config(state='disabled')
                self.text_display.see(tk.END)
            except Exception as e:
                logger.error(f"Erreur de déchiffrement : {e}")
                self.text_display.config(state='normal')
                self.text_display.insert(tk.END, f"{message['senderId']}: [Erreur de déchiffrement]\n")
                self.text_display.config(state='disabled')
                self.text_display.see(tk.END)

    def decrypt_content(self, encrypted_content):
        try:
            logger.debug(f"Déchiffrement de : {encrypted_content[:50]}... (longueur : {len(encrypted_content)})")
            # Décode le Base64
            cipher_text = base64.b64decode(encrypted_content)
            logger.debug(f"Texte chiffré (après Base64, longueur) : {len(cipher_text)} bytes")
            if len(cipher_text) < 16:
                raise ValueError("Texte chiffré trop court pour contenir un IV")
            # Extrait l'IV (16 bytes, préfixé par CryptoJS)
            iv = cipher_text[:16]
            encrypted_data = cipher_text[16:]
            logger.debug(f"IV : {base64.b64encode(iv).decode()}")
            # Crée le chiffreur AES-CBC
            cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
            # Déchiffre
            padded_text = cipher.decrypt(encrypted_data)
            # Supprime le padding PKCS7
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
            self.text_display.config(state='normal')
            self.text_display.delete(1.0, tk.END)
            for msg in messages:
                try:
                    content = msg.get('content', {})
                    encrypted_content = content.get('forSender' if msg['senderId'] == self.sender_id else 'forReceiver', '')
                    logger.debug(f"Message ID {msg['_id']} - Contenu chiffré : {encrypted_content[:50]}...")
                    decrypted_content = self.decrypt_content(encrypted_content)
                    self.text_display.insert(tk.END, f"{msg['senderId']}: {decrypted_content}\n")
                except Exception as e:
                    logger.error(f"Erreur de déchiffrement dans refresh_messages : {e}")
                    self.text_display.insert(tk.END, f"{msg['senderId']}: [Erreur de déchiffrement]\n")
            self.text_display.config(state='disabled')
            self.text_display.see(tk.END)
        except Exception as e:
            logger.error(f"Erreur dans refresh_messages : {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les messages : {e}")