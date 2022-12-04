import socket
from _thread import *
import random
from msg import MessageHandler, PackageDef
from question import QuestionGenerator

class GameServer():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # create socket
        self.server_socket = self.init_server()
        
        # create message handler
        self.msg_handler = MessageHandler()
        
        # create question generator
        self.quest_generator = QuestionGenerator(num_questions=5,
                                                 select_time=10,
                                                 number_task=5,
                                                 image_size=(40, 40))
        
        # gameplay control
        self.max_players = 2
        self.num_players = 0
        self.address_to_def = {}
        self.connections = []
        self.addresses = []
        self.game_start = False
        self.suggest_game_start = False
        
    def init_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
        print(f'Server is listing on the port {self.port}...')

        return server_socket
    
    def client_handler(self, conn, address):
        while True:
            data = conn.recv(4096)
            
            # run main logic
            self.logic_handle(conn, address, data)
            
        conn.close()
        
    def logic_handle(self, conn, address, data):
        # decode msg 
        pkt_type, data_length, decoded_data = self.msg_handler.decode(data)
        
        # handle
        encoded_data = b""
        if(pkt_type == PackageDef.PKT_HELLO):
            msg = {
                    "def": self.address_to_def[address], 
                    "acceptStatus": 1 if self.num_players <= self.max_players else 0,
                    "playerOrder": self.num_players if self.num_players <= self.max_players else -1
                 }
            
            encoded_data = self.msg_handler.encode(PackageDef.PKT_ACCEPT_CONNECT, msg)
        
        elif(pkt_type == PackageDef.PKT_TASK_SELECTED):
            conn_def = decoded_data["def"]
            quest_num = decoded_data["questNumber"]
            task_idx = decoded_data["taskSelected"]
            send_quest = self.quest_generator.get_mask_questions(conn_def, quest_num, task_idx)
            
        conn.sendall(encoded_data)
        
    def broadcast(self, pkt_type):
        for idx, conn in enumerate(self.connections):
            addr = self.addresses[idx]
            conn_def = self.address_to_def[addr] 
            print(f"Send message to {addr}")
            
            encoded_data = b""
            if(pkt_type == PackageDef.PKT_START):
                msg = {
                    "def": conn_def
                }
                encoded_data = self.msg_handler.encode(PackageDef.PKT_START, msg)
                
            elif(pkt_type == PackageDef.PKT_SELECT_TASK):
                msg = self.quest_generator.generate(conn_def)
                encoded_data = self.msg_handler.encode(PackageDef.PKT_SELECT_TASK, msg)
                
            conn.sendall(encoded_data)
            
    
    def accept_connections(self):
        conn, address = self.server_socket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        
        self.num_players += 1
        self.connections.append(conn)
        self.addresses.append(address)
        self.address_to_def[address] = random.randint(1, 1000)
        
        if(self.num_players == 2):
            self.game_start = True
        
        start_new_thread(self.client_handler, (conn, address))
    
    def run(self):
        # start listen for connections
        self.server_socket.listen()
        
        # main control
        try:
            while True:
                self.accept_connections()     
                
                if(self.game_start):
                    self.game_start = False
                    # send start signal to all client
                    self.broadcast(PackageDef.PKT_START)
                    # send question to all client
                    self.broadcast(PackageDef.PKT_SELECT_TASK)
                        
        except Exception as e:
            raise e
    
        finally:
            self.server_socket.close()   
            
if __name__ == "__main__":
    game_server = GameServer("127.0.0.1", 6969)
    
    game_server.run()