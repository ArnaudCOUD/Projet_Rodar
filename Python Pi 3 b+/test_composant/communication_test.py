import socket
from time import sleep
from sys import exit

class communication_ordinateur():
	def __init__(self):
		self.server_host = '172.20.10.3'
		self.server_port = 12345
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def connection(self):
		print("Connection ...")
		self.s.connect((self.server_host, self.server_port))
		print("Connecté")
		while self.reception() != "start_lidar":
			pass

	def envoie(self,data):
		self.s.sendall(str(data).encode())

	def reception(self):
		data = self.s.recv(1024).decode()
		if data == "stop_lidar":
			print("stop")
			self.s.close()
			exit()
		return data


CO = communication_ordinateur()
CO.connection()
