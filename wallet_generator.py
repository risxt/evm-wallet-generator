import os
import json
import getpass
from mnemonic import Mnemonic
from eth_account import Account
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.prompt import Prompt

# Enable HD wallet features
Account.enable_unaudited_hdwallet_features()

console = Console()

def generate_wallet():
    mnemo = Mnemonic("english")
    mnemonic = mnemo.generate(strength=256)
    acct = Account.from_mnemonic(mnemonic)
    return {"mnemonic": mnemonic, "address": acct.address, "private_key": acct.key.hex()}

def encrypt_data(data, password):
    key = pad(password.encode(), AES.block_size)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted).decode()

def decrypt_data(encrypted_data, password):
    encrypted_data = base64.b64decode(encrypted_data)
    key = pad(password.encode(), AES.block_size)
    iv, encrypted_content = encrypted_data[:16], encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_content), AES.block_size)
    return decrypted.decode()

def save_to_file(data, encrypt=False):
    filename = "wallets.json"
    if encrypt:
        password = getpass.getpass("🔒 Enter encryption password: ")
        data = encrypt_data(data, password)
    
    with open(filename, "w") as f:
        f.write(data)

    console.print(f"✅ [bold green]Wallets saved to {filename}[/bold green]")

if __name__ == "__main__":
    console.print("\n[bold magenta]🚀 Ethereum Wallet Generator[/bold magenta]\n")

    num_wallets = Prompt.ask("[cyan]How many wallets do you want to generate?[/cyan]", default="1")
    num_wallets = int(num_wallets)

    wallets = []
    
    for _ in track(range(num_wallets), description="🔄 Generating wallets..."):
        wallets.append(generate_wallet())

    table = Table(title="🔑 Generated Wallets", show_lines=True)
    table.add_column("Address", style="cyan", justify="left")
    table.add_column("Private Key", style="red", justify="left")

    for wallet in wallets:
        table.add_row(wallet["address"], wallet["private_key"])

    console.print(table)

    choice = Prompt.ask("[yellow]Do you want to encrypt the file? (yes/no)[/yellow]", choices=["yes", "no"])
    save_to_file(json.dumps(wallets, indent=4), encrypt=(choice == "yes"))
