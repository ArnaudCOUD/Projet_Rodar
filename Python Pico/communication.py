import socket
from time import sleep
from connect_wifi import connection_wifi
connection_wifi()


class communication_ordinateur():
    def __init__(self):
        self.server_host = '172.20.10.3'  # Adresse IP du serveur 
        self.server_port = 12345 # Port d'écoute du serveur
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connexion(self):
        print("Connexion ...")
        self.s.connect((self.server_host, self.server_port))
        print("Connecté")
        
    def envoie(self,data):
        self.s.sendall(str(data).encode())
        
    def reception(self):
        data = self.s.recv(1024).decode()
        return data
