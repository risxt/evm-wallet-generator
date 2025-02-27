import os
import json
import getpass
import base64
import qrcode
from time import sleep
from mnemonic import Mnemonic
from eth_account import Account
from rich.console import Console
from rich.table import Table
from rich.progress import track
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Enable HD wallet features to use mnemonics
Account.enable_unaudited_hdwallet_features()
console = Console()

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

def save_to_file(wallets, file_format, save_mode, encrypt=False):
    file_extension = "json" if file_format == "1" else "txt"
    filename = f"wallets.{file_extension}"
    
    if save_mode == "3":
        counter = 1
        while os.path.exists(filename):
            filename = f"wallets_{counter}.{file_extension}"
            counter += 1
    
    existing_data = []
    if os.path.exists(filename) and save_mode == "2":
        with open(filename, "r") as f:
            try:
                existing_data = json.load(f) if file_extension == "json" else f.readlines()
            except json.JSONDecodeError:
                pass
    
    start_number = len(existing_data) + 1 if save_mode == "2" else 1
    for i, wallet in enumerate(wallets, start=start_number):
        wallet["number"] = i  # Assign wallet numbers
    
    if file_extension == "json":
        existing_data.extend(wallets)
        data = json.dumps(existing_data, indent=4)
    else:
        lines = [f"Wallet {w['number']}:\nAddress: {w['address']}\nMnemonic: {w['mnemonic']}\nPrivate Key: {w['private_key']}\n\n" for w in wallets]
        data = "".join(lines)
        if save_mode == "2":
            data = "".join(existing_data) + data
    
    if encrypt:
        password = getpass.getpass("Enter encryption password: ")
        data = encrypt_data(data, password)
    
    with open(filename, "w") as f:
        f.write(data)
    console.print(f"\n[green]✅ Wallets saved to {filename}[/green]")

def generate_qr_code(address, number):
    qr = qrcode.make(address)
    qr_filename = f"{number}.png"
    qr.save(qr_filename)
    console.print(f"[cyan]📷 QR Code saved as {qr_filename}[/cyan]")

def display_wallets():
    filename = "wallets.json"
    if not os.path.exists(filename):
        console.print("[red]No wallets found![/red]")
        return
    
    with open(filename, "r") as f:
        try:
            wallets = json.load(f)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON format in wallets.json![/red]")
            return
    
    table = Table(title="🔑 Generated Wallets", show_header=True, header_style="bold magenta")
    table.add_column("#", justify="center")
    table.add_column("Address", justify="left")
    table.add_column("Mnemonic", justify="left")
    table.add_column("Private Key", justify="left")
    
    for wallet in wallets:
        table.add_row(str(wallet["number"]), wallet["address"], wallet["mnemonic"], wallet["private_key"])
    
    console.print(table)

def main():
    while True:
        console.print("\n[yellow]🚀 Ethereum Wallet Generator[/yellow]", style="bold")
        console.print("[blue]1.[/blue] Generate Wallet(s)")
        console.print("[blue]2.[/blue] View Saved Wallets")
        console.print("[blue]3.[/blue] Exit")
        choice = input("\nChoose an option: ").strip()
        
        if choice == "1":
            num_wallets = int(input("How many wallets do you want to generate? "))
            wallets = []
            
            for _ in track(range(num_wallets), description="🔄 Generating wallets..."):
                sleep(0.5)  # Simulate loading
                mnemonic, address, private_key = generate_wallet()
                wallets.append({"mnemonic": mnemonic, "address": address, "private_key": private_key})
            
            console.print("[yellow]Choose file format:[/yellow] 1. JSON 2. TXT")
            file_format = input("Enter choice (1/2): ").strip()
            console.print("[yellow]Choose save mode:[/yellow] 1. Overwrite 2. Append 3. New File")
            save_mode = input("Enter choice (1/2/3): ").strip()
            
            choice = input("Do you want to encrypt the file? (y/n): ").strip().lower()
            save_to_file(wallets, file_format, save_mode, encrypt=(choice == "y"))
            
            for wallet in wallets:
                generate_qr_code(wallet["address"], wallet["number"])
        
        elif choice == "2":
            display_wallets()
        
        elif choice == "3":
            console.print("[green]👋 Exiting Ethereum Wallet Generator. Goodbye![/green]")
            break
        
        else:
            console.print("[red]Invalid choice, please try again.[/red]")

if __name__ == "__main__":
    main()
