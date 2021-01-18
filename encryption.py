import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os
import newegg_crawl_config


class SymmetricEncrypt:
    def __init__(self, salt, hashed_key):
        self.salt = salt
        self.hashed_key = hashed_key

    def encrypt(self, raw_password, filename):
        if self.check_password(raw_password):
            with open(filename, "rb") as f:
                info_to_encrypt = f.read()

            password_bytes = raw_password.encode()
            kdf = Scrypt(salt=self.salt, length=32, n=2 ** 20, r=8, p=1)
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            cipher = Fernet(key)

            encrypted_info = cipher.encrypt(info_to_encrypt)

            with open(filename + ".enc", "wb") as ef:
                ef.write(encrypted_info)
        else:
            raise Exception("Incorrect password entered")

    def decrypt(self, raw_password, filename):
        if self.check_password(raw_password):
            with open(filename, "rb") as f:
                info_to_decrypt = f.read()

            password_bytes = raw_password.encode()
            kdf = Scrypt(salt=self.salt, length=32, n=2 ** 20, r=8, p=1)
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            cipher = Fernet(key)

            return cipher.decrypt(info_to_decrypt)
        else:
            raise Exception("Incorrect password entered")

    def check_password(self, raw_password):
        """
        :param raw_password: Normal UTF-8-formatted string of a password to check against the stored password hash
        :type raw_password: str
        """
        password_bytes = raw_password.encode()

        kdf = Scrypt(salt=self.salt, length=32, n=2 ** 20, r=8, p=1)
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return True if key == self.hashed_key else False

    @staticmethod
    def generate_password_hash(raw_password):
        """
        :param raw_password: Normal UTF-8-formatted string of a password to generate hash and salt with
        :type raw_password: str
        """
        password_bytes = raw_password.encode()
        random_salt = os.urandom(16)

        # password key
        kdf = Scrypt(salt=random_salt, length=32, n=2**20, r=8, p=1)
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))

        print("\nThe following string is a representation of the password hash in bytes. "
              "Save it to the variable hashed_key in newegg_crawler_config")
        print(key)
        del key
        print("\nThe next string is a representation of the salt in bytes. "
              "Save it to the variable salt in newegg_crawler_config")
        print(random_salt)

        print("\nMemorize or write down the password you provided, as this program will not "
              "have any sort of backup for it.")


if __name__ == "__main__":
    encryptor = SymmetricEncrypt(salt=newegg_crawl_config.salt, hashed_key=newegg_crawl_config.hashed_key)
    # encryptor.generate_password_hash("testpassword123")
    # print(encryptor.check_password("testpass123"))
    # print(encryptor.check_password("testPassword123"))
    # print(encryptor.check_password("testpassword123"))
    # encryptor.encrypt(raw_password="testpassword123", filename="info.json")
    print(encryptor.decrypt(filename="info.json.enc", raw_password="testpassword123"))
