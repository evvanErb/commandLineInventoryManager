import hashlib
from Crypto.Cipher import AES

key = hashlib.sha256("password").digest()
mode = AES.MODE_CBC
IV = "\x00"*16
encryptor = AES.new(key, mode, IV=IV)
outfile = open("inventory.txt", "w")
outfile.write(encryptor.encrypt("goodtogogoodtogo"))
outfile.close()
