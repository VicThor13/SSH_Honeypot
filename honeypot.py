import socket
import threading
import paramiko
import requests
import logging
import os

# Configuration
PORT = 2222
HOST = '0.0.0.0'
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
HOST_KEY_PATH = 'server.key'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_to_discord(ip, username, password):
    """Envoie les informations de connexion à un webhook Discord."""
    if not DISCORD_WEBHOOK_URL:
        logging.warning("URL du Webhook Discord non configurée. Impossible d'envoyer l'alerte.")
        return

    data = {
        "content": f"🚨 **Tentative de connexion SSH détectée (Honeypot) !** 🚨\n"
                   f"**IP Source**: `{ip}`\n"
                   f"**Utilisateur testé**: `{username}`\n"
                   f"**Mot de passe testé**: `{password}`"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=5)
        if response.status_code in (200, 204):
            logging.info(f"Alerte envoyée sur Discord avec succès pour l'IP {ip}")
        else:
            logging.error(f"Échec de l'envoi sur Discord: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi au webhook Discord: {e}")

class SSHServer(paramiko.ServerInterface):
    """Classe serveur Paramiko qui gère les tentatives de connexion."""
    
    def __init__(self, client_ip):
        self.event = threading.Event()
        self.client_ip = client_ip

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        """Gère les tentatives d'authentification par mot de passe."""
        logging.info(f"Tentative depuis {self.client_ip} - Utilisateur: {username}, Mot de passe: {password}")
        
        # Déclenche l'envoi de l'alerte de manière asynchrone pour ne pas bloquer
        threading.Thread(target=send_to_discord, args=(self.client_ip, username, password), daemon=True).start()
        
        # Refuse systématiquement la connexion
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

def handle_connection(client_socket, addr):
    """Gère une connexion cliente individuelle dans un thread."""
    client_ip = addr[0]
    logging.info(f"Nouvelle connexion entrante de {client_ip}:{addr[1]}")
    
    try:
        transport = paramiko.Transport(client_socket)
        
        # Génère une clé RSA si elle n'existe pas déjà
        if not os.path.exists(HOST_KEY_PATH):
            logging.info("Génération de la clé hôte RSA...")
            key = paramiko.RSAKey.generate(2048)
            key.write_private_key_file(HOST_KEY_PATH)
        else:
            key = paramiko.RSAKey(filename=HOST_KEY_PATH)
            
        transport.add_server_key(key)
        
        server = SSHServer(client_ip)
        try:
            transport.start_server(server=server)
        except paramiko.SSHException as e:
            logging.error(f"Échec de la négociation SSH pour {client_ip}: {e}")
            return

        # Attend la demande de canal de la part du client
        chan = transport.accept(20)
        if chan is None:
            logging.info(f"Aucun canal ouvert par {client_ip}.")
            return
            
        # Garde la connexion ouverte brièvement pour laisser le temps aux tentatives
        server.event.wait(10)
        chan.close()
            
    except Exception as e:
        logging.error(f"Erreur lors de la gestion de la connexion de {client_ip}: {e}")
    finally:
        try:
            transport.close()
        except:
            pass
        client_socket.close()

def main():
    """Démarre le serveur honeypot SSH."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(100)  # Autorise jusqu'à 100 connexions en attente
        logging.info(f"✅ Honeypot SSH en écoute sur {HOST}:{PORT}...")

        while True:
            client_socket, addr = sock.accept()
            # Lance un nouveau thread pour chaque connexion pour gérer le multi-threading
            client_thread = threading.Thread(target=handle_connection, args=(client_socket, addr))
            client_thread.daemon = True
            client_thread.start()
            
    except Exception as e:
        logging.error(f"Erreur fatale du serveur: {e}")
    finally:
        sock.close()

if __name__ == '__main__':
    main()
