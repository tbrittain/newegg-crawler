import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import os
import newegg_crawl_config
import json


class SymmetricEncrypt:
    def __init__(self):
        self.salt = newegg_crawl_config.salt
        self.hashed_pass = newegg_crawl_config.hashed_pass

    def encrypt_info(self):
        # TODO
        with open("info.json", "rb") as f:
            info_to_encrypt = f.read()
            encrypted_info = None

    def decrypt_info(self, filename):
        pass

    def check_password(self, raw_password):
        """
        :param raw_password: Normal UTF-8-formatted string of a password to generate hash and salt with
        :type raw_password: str
        """
        password_bytes = raw_password.encode()
        # noinspection PyTypeChecker
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self.salt, iterations=100000)
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return True if key == self.hashed_pass else False

    @staticmethod
    def generate_password_hash(raw_password):
        """
        :param raw_password: Normal UTF-8-formatted string of a password to generate hash and salt with
        :type raw_password: str
        """
        password_bytes = raw_password.encode()
        random_salt = os.urandom(16)
        # noinspection PyTypeChecker
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=random_salt, iterations=100000)
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        print("\nThe following string is a representation of the password hash in bytes. "
              "Save it to the variable hashed_pass in newegg_crawler_config")
        print(key)
        print("\nThe next string is a representation of the salt in bytes. "
              "Save it to the variable salt in newegg_crawler_config")
        print(random_salt)
        print("\nMemorize or write down the password provided, as this program will not "
              "have any sort of backup for it.")


if __name__ == "__main__":
    # password = input("Enter password: ").encode()
    encryptor = SymmetricEncrypt()
    # encryptor.generate_password_hash("testpassword123")
    print(encryptor.check_password("testpass123"))
    print(encryptor.check_password("testPassword123"))
    print(encryptor.check_password("testpassword123"))