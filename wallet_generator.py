import os
import json
from time import sleep
from rich.console import Console
from rich.progress import track
import getpass
from web3 import Web3, Account

console = Console()

def generate_wallet():
    private_key = "0x" + os.urandom(32).hex()
    account = Account.from_key(private_key)
    return "example mnemonic", account.address, private_key

def save_to_file(wallets, file_format, save_mode, encrypt=False, filename=None):
    if save_mode == "3" and not filename:
        console.print("[red]Error: Nama file tidak boleh kosong![/red]")
        return

    if file_format == "1":
        ext = "json"
        mode = "w" if save_mode == "1" else "a"
        data = json.dumps(wallets, indent=4)
    else:
        ext = "txt"
        mode = "w" if save_mode == "1" else "a"
        data = "\n".join([f"Mnemonic: {w['mnemonic']}\nAddress: {w['address']}\nPrivate Key: {w['private_key']}\n" for w in wallets])

    if save_mode == "3":
        filepath = f"{filename}.{ext}"
    else:
        filepath = f"wallets.{ext}"

    with open(filepath, mode) as file:
        file.write(data)
    
    console.print(f"[green]Wallets berhasil disimpan ke {filepath}[/green]")
    
    if encrypt and file_format == "1":
        password = getpass.getpass("Buat satu password untuk semua Keystore JSON: ")
        for wallet in wallets:
            keystore = Account.encrypt(wallet['private_key'], password)
            keystore["address"] = wallet['address']
            keystore_filename = f"wallet_{wallet['number']}.json"
            with open(keystore_filename, "w") as f:
                json.dump(keystore, f, indent=4)
            console.print(f"[green]Keystore JSON disimpan sebagai {keystore_filename}[/green]")

def generate_qr_code(address, number):
    console.print(f"[blue]QR Code generated for {address} (Wallet {number})[/blue]")

def display_wallets():
    console.print("[yellow]Fitur ini belum diimplementasikan.[/yellow]")

def main():
    while True:
        console.print("\n[yellow]🚀 Ethereum Wallet Generator[/yellow]", style="bold")
        console.print("[blue]1.[/blue] Generate Wallet(s)")
        console.print("[blue]2.[/blue] View Saved Wallets")
        console.print("[blue]3.[/blue] Exit")
        choice = input("\nChoose an option: ").strip()
        
        if choice == "1":
            try:
                num_wallets = int(input("How many wallets do you want to generate? "))
            except ValueError:
                console.print("[red]Invalid input! Please enter a number.[/red]")
                continue
            
            wallets = []
            for i in track(range(num_wallets), description="🔄 Generating wallets..."):
                sleep(0.5)
                mnemonic, address, private_key = generate_wallet()
                wallets.append({"mnemonic": mnemonic, "address": address, "private_key": private_key, "number": i + 1})

            console.print("[yellow]Choose file format:[/yellow] 1. JSON 2. TXT")
            file_format = input("Enter choice (1/2): ").strip()
            console.print("[yellow]Choose save mode:[/yellow] 1. Overwrite 2. Append 3. New File")
            save_mode = input("Enter choice (1/2/3): ").strip()

            filename = None
            if save_mode == "3":
                filename = input("Enter the new file name (without extension): ").strip()
                if not filename:
                    console.print("[red]File name cannot be empty![/red]")
                    continue
            
            encrypt_choice = input("Do you want to encrypt the wallets as Keystore JSON (y/n)? ").strip().lower()
            save_to_file(wallets, file_format, save_mode, encrypt=(encrypt_choice == "y"), filename=filename)
            
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
