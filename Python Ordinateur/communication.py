import socket
from time import sleep
ADDR_LIDAR = '172.20.10.11'
ADDR_MOTEUR = '172.20.10.14'

class communication_robot():
    def __init__(self):
        self.HOST = '0.0.0.0'  # Adresse IP du serveur (0.0.0.0 pour toutes les interfaces)
        self.PORT = 12345 # Port d'écoute du serveur
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_lidar = None
        self.conn_moteur = None

    def connexion(self,nbr_apareil=2):
        nbr_connexion = 0
        self.s.bind((self.HOST, self.PORT)) # Initialise la plage d'adresses et le port d'écoute
        while nbr_connexion !=nbr_apareil:
            self.s.listen() # Ecoute si un appareil souhaite se connecter
            print("En attente de connexions...")
            # Accepter une connexion entrante
            self.conn, self.addr = self.s.accept()
            if self.addr[0] == ADDR_LIDAR and self.conn_lidar == None:
                self.conn_lidar = self.conn
                print("Connecté au Lidar")
                nbr_connexion += 1
            if self.addr[0] == ADDR_MOTEUR and self.conn_moteur == None:
                self.conn_moteur = self.conn
                print("Connecté au Moteur")
                nbr_connexion += 1
        print("Tous les composants sont connectés")
        #self.envoie_moteur("start_moteur")
        #self.envoie_lidar("start_lidar")
        
    def envoie_lidar(self,data):
        try:
            self.conn_lidar.sendall(str(data).encode()) # Data : information que je souhaite envoyer
        except:
            pass
    
    def envoie_moteur(self,data):
        try:
            self.conn_moteur.sendall(str(data).encode())
        except:
            pass
        
    def reception_lidar(self,timeout=None):
        try:
            self.conn_lidar.settimeout(timeout)
            data = self.conn_lidar.recv(32_000).decode()
            if data != None:
                print(data)
            if data[0:6]=="moteur":
                self.envoie_moteur(data[6:])
                return None
            return data
        except socket.timeout:
            return None
        except Exception as e:
            #print(e)
            pass
    
    def reception_moteur(self,timeout=None):
        try:
            self.conn_moteur.settimeout(timeout)
            data = self.conn_moteur.recv(1024).decode()
            if data[0:5]=="lidar":
                self.envoie_lidar(data[5:])
                return None
            return data
        except socket.timeout:
            return None
        except:
            pass
    
    
    def shutdown(self):
        self.envoie_moteur("stop_moteur")
        sleep(0.05)
        self.envoie_lidar("stop_lidar")
        #self.s.shutdown(1)
        self.s.close()
        
        
        """time out recv:
            self.conn_lidar.settimeout(3)
            try:
                self.conn_lidar.recv(1024)
            except self.conn_lidar.timeout:
                time out
        """