import machine
import network
import time


def connection_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Se connecter au réseau Wi-Fi
    wlan.connect('iPhone d’Arnaud', 'arnaud18')

    # Attendre la connexion
    while not wlan.isconnected():
        print("Connexion au wifi...")
        time.sleep(1)

    # Afficher les informations de connexion
    print("Connecté au réseau Wi-Fi:", "iPhone d’Arnaud")
    print("Adresse IP:", wlan.ifconfig()[0])
    
"""
from connect_wifi import connection_wifi
connection_wifi()
"""
