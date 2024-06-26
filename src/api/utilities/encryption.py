from cryptography.fernet import Fernet, InvalidToken
import os


class SecretCipher:
    def get_cipher(self):
        # Get the encryption key from environment variables
        encryption_key = os.getenv("ENCRYPTION_KEY")
        # Convert the encryption key to bytes
        encryption_key_bytes = encryption_key.encode()
        # Create a cipher using the encryption key
        cipher = Fernet(encryption_key_bytes)
        return cipher

    def encrypt_string(self, s):
        """Encrypt a string."""
        cipher = self.get_cipher()
        # Convert the string to bytes
        s_bytes = s.encode("utf-8")
        # Encrypt the bytes
        encrypted_bytes = cipher.encrypt(s_bytes)
        return encrypted_bytes

    def decrypt_string(self, encrypted_string):
        """Decrypt a string."""
        cipher = self.get_cipher()
        # Decrypt the bytes
        decrypted_bytes = cipher.decrypt(encrypted_string)
        # Convert the decrypted bytes to a string
        decrypted_string = decrypted_bytes.decode("utf-8")
        return decrypted_string

    def is_encrypted(self, s):
        """Check if a string is encrypted."""
        try:
            # Try to decrypt the string
            self.decrypt_string(s.encode())
            return True
        except (InvalidToken, TypeError):
            # If decryption raises an InvalidToken or TypeError exception, the string is not encrypted
            return False
