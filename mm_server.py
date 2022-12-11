import socket
import json
import time

import websockets
import asyncio

class MMConnection:
	def __init__(self, 
              	mm_ip="104.194.240.16",
                mm_port=8080,
                game_server_public_ip="tcp://6.tcp.ngrok.io",
                game_server_public_port=19563,
                game_server_local_ip="localhost",
                game_server_local_port=6969
                ):
		self.updateMatchIp = mm_ip
		self.updateMatchPort = mm_port

		self._localIP = game_server_local_ip
		self._localPort = game_server_local_port
		self._publicIP = game_server_public_ip
		self._publicPort = game_server_public_port
    
		self.is_server_created = False
  
		self.update_endpoint = "ws://104.194.240.16/ws/channels/"

	def wait_mm_request(self, mm_connect):
		successMsg = {"result": 1, "ip": self._publicIP, "port": self._publicPort, "path": ""}
		failedMsg = {"result": 0}

		pkg = mm_connect.recv(1024)
		
		data = None
		try:
			print ("Pkg received from mmServer: " , pkg)
			data = json.loads(pkg)
			mm_connect.send(json.dumps(successMsg).encode())

			self.is_server_created = True
		except:
			print("Failed to decode request");
			mm_connect.send(json.dumps(failedMsg).encode())

		mm_connect.close()
  
		return data

	def update_to_server(self, data):
		asyncio.run(self.update(data))
	
	async def update(self, data):
		async with websockets.connect(self.update_endpoint) as websocket:
			await websocket.send(json.dumps(data))
			msg = await websocket.recv()
			print(msg)
   
if __name__ == '__main__':
	mmConnection = MMConnection()

	