import socket
import json
import time

class MMConnection:
	def __init__(self, 
              	mm_ip=None,
                mm_port=None,
                game_server_public_ip=None,
                game_server_public_port=None,
                game_server_local_ip="localhost",
                game_server_local_port=6969
                ):
		self.updateMatchIp = mm_ip
		self.updateMatchPort = mm_port

		self._localIP = game_server_local_ip
		self._localPort = game_server_local_port
		self._publicIP = game_server_public_ip
		self._publicPort = game_server_public_port
  
		self.mms_data = None

	def wait_mm_request(self, mm_connect):
		successMsg = {"result": 1, "ip": self._publicIP, "port": self._publicPort, "path": ""}
		failedMsg = {"result": 0}

		pkg = mm_connect.recv(1024)
		try:
			print ("Pkg received from mmServer: " , pkg)
			data = json.loads(pkg)
			mm_connect.send(json.dumps(successMsg).encode())

			self.mms_data = data
		except:
			print("Failed to decode request");
			mm_connect.send(json.dumps(failedMsg).encode())

		mm_connect.close()

if __name__ == '__main__':
	mmConnection = MMConnection()

	