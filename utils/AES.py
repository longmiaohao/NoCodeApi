import Crypto
import binascii
import random
import string
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class Aes(object):
    """
    对称加密
    """
    secret_key = ""
    ciphertext = ""

    def __init__(self, key_len=32, secret_key=None):
        self.__key_len = key_len
        self.mode = AES.MODE_CBC
        if not secret_key:
            self.generate_secret_key()
        else:
            self.secret_key = secret_key

    def generate_secret_key(self):
        for i in range(0, int(self.__key_len/8)):
            self.secret_key += "".join(random.sample(string.ascii_letters + string.digits, 8))

    def encrypt(self, plaintext):
        plaintext = plaintext.encode('utf-8')
        cryptor = AES.new(self.secret_key.encode('utf-8'), self.mode, b'0000000000000000')
        length = 16
        plaintext_len = len(plaintext)
        if plaintext_len < length:
            add = (length-plaintext_len)    # \0 backspace
            plaintext = plaintext + ('\0' * add).encode('utf-8')
        elif plaintext_len > length:
            add = (length-(plaintext_len % length))
            plaintext = plaintext + ('\0' * add).encode('utf-8')
        self.ciphertext = b2a_hex(cryptor.encrypt(plaintext))
        return str(self.ciphertext, encoding="utf-8")

    @staticmethod
    def decrypt(cypher="", secret_key=""):
        cryptor = AES.new(secret_key.encode("utf-8"), AES.MODE_CBC, b'0000000000000000')
        plain_text = cryptor.decrypt(a2b_hex(cypher))
        plain_text = bytes.decode(plain_text).rstrip('\0')
        return plain_text


# if __name__ == '__main__':
#     aes = Aes(32)       # 自定义secret_key
#     cipher = aes.encrypt("Shuang00")                               # 密文
#     secret_key = aes.secret_key
#     print('secret_key:', secret_key)
#     print('cipher:', cipher)
#     print('decrypt:', aes.decrypt(cipher, aes.secret_key))
