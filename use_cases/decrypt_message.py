from Crypto.Cipher import AES
import base64
import logging

logger = logging.getLogger(__name__)

class DecryptMessageUseCase:
    def __init__(self):
        pass

    def execute(self, encrypted_content, aes_key):
        """
        Décrypte un message avec la clé AES fournie
        """
        try:
            encrypted_data = base64.b64decode(encrypted_content)
            iv = b'\x00' * 16
            cipher = AES.new(aes_key[:32], AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(encrypted_data)
            pad_len = decrypted[-1]
            if not 1 <= pad_len <= 16:
                raise ValueError("Padding incorrect")
            return decrypted[:-pad_len].decode('utf-8')
        except Exception as e:
            logger.error(f"Erreur dans decrypt_content : {e}")
            return "[Erreur de déchiffrement]"