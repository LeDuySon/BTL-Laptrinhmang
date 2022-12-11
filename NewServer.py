import socket
import json
import time

class MMConnection:
	def __init__(self):
		self.sock_stream = None
		self.mmConnect = None
		self.mmAddress = None
		self.matchData = None

		self.updateMatchIp = "104.194.240.16"
		self.updateMatchPort = 8080

		self._localIP = 'localhost'
		self._localPort = 80
		self._publicIP = "0.tcp.ap.ngrok.io"
		self._publicPort = 15856

	def create_sock_stream(self):
		self.sock_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_stream.bind((self._localIP, self._localPort))
		self.sock_stream.listen()
		return self.sock_stream

	def assign_sock_stream(self, sock_stream):
		if (sock_stream and not self.sock_stream):
			self.sock_stream = sock_stream
			return True
		else:
			return False

	def wait_mm_request(self):
		successMsg = {"result": 1, "ip": self._publicIP, "port": self._publicPort, "path": ""}
		failedMsg = {"result": 0}

		if (not self.sock_stream):
			return None, None, None

		self.mmConnect, self.mmAddress = self.sock_stream.accept()
		pkg = self.mmConnect.recv(1024)
		try:
			print ("Pkg received from mmServer: " , pkg)
			data = json.loads(pkg)
			self.mmConnect.send(json.dumps(successMsg).encode())
			return self.mmConnect, self.mmAddress, data
		except:
			print("Failed to decode request");
			self.mmConnect.send(json.dumps(failedMsg).encode())
			return None, None, None

	def run(self):
		self.sock_stream = self.create_sock_stream()
		while (self.mmConnect == None or self.mmAddress == None):
			self.mmConnect, self.mmAddress, self.matchData = self.wait_mm_request()
		return self.matchData


if __name__ == '__main__':
	mmConnection = MMConnection()
	mmConnection.run()

	