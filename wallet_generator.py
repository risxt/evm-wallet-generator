import os
import json
import getpass
from mnemonic import Mnemonic
from eth_account import Account
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

def generate_wallet():
    mnemo = Mnemonic("english")
    mnemonic = mnemo.generate(strength=256)
    acct = Account.from_mnemonic(mnemonic)
    return mnemonic, acct.address, acct.key.hex()

def encrypt_data(data, password):
    key = pad(password.encode(), AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv=b'0123456789abcdef')
    encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + encrypted).decode()

def decrypt_data(encrypted_data, password):
    encrypted_data = base64.b64decode(encrypted_data)
    key = pad(password.encode(), AES.block_size)
    iv = encrypted_data[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)
    return decrypted.decode()

def save_to_file(data, encrypt=False):
    filename = "secret.txt"
    if encrypt:
        password = getpass.getpass("Enter encryption password: ")
        data = encrypt_data(data, password)
    
    with open(filename, "w") as f:
        f.write(data)

    print(f"Saved to {filename}")

if name == "main":
    num_wallets = int(input("How many wallets do you want to generate? "))
    wallets = []
    
    for _ in range(num_wallets):
        mnemonic, address, private_key = generate_wallet()
        wallets.append({"mnemonic": mnemonic, "address": address, "private_key": private_key})

    wallets_json = json.dumps(wallets, indent=4)
    
    choice = input("Do you want to encrypt the file? (yes/no): ").strip().lower()
    save_to_file(wallets_json, encrypt=(choice == "yes"))

Added wallet generator script
