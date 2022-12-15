import socket
from _thread import *
import random
import time

from msg import MessageHandler, PackageDef
from question import QuestionGenerator
from suggest_game import SuggestGameHandler
from player import ClientPlayer
from mm_server import MMConnection
from server_ui import ServerUI

class GameServer():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # create socket
        self.server_socket = self.init_server()
        
        # create message handler
        self.msg_handler = MessageHandler()
        
        # create question generator
        self.image_size = (40, 40)
        self.quest_generator = QuestionGenerator(num_questions=5,
                                                 select_time=10,
                                                 number_task=5,
                                                 image_size=self.image_size)
        
        # init suggest game player handler
        self.suggest_game_handler = SuggestGameHandler()
        
        # init communicator between our server and matchmaking server
        self.is_mm_connect = False
        self.mm_com = MMConnection()
        self.player_ids = []
        self.server_password = None
        self.match_id = None
        
        # init gameserver ui 
        self.server_ui = ServerUI()
        
        # gameplay control
        self.max_players = 2
        self.num_players = 0
        self.address_to_def = {}
        self.connections = []
        self.addresses = []
        self.game_start = False
        self.end_score = 3
        self.sleep_time = 0
        self.is_send_pkt_round_result = False
        
        self.players = []
        self.address2player = {}
                
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
            if not data:
                print("END!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                conn.close()
            
            print(f"Receive data from {address}")
            # run main logic
            self.logic_handle(conn, address, data)
        
    def logic_handle(self, conn, address, data):
        # get player
        player = self.address2player[address]
        # decode msg 
        pkt_type, data_length, decoded_data = self.msg_handler.decode(data)
        
        print(f"Receive package {pkt_type} - {data_length} - {decoded_data}")
        
        # handle
        encoded_data = None
        if(pkt_type == PackageDef.PKT_HELLO):
            user_id = decoded_data["user_id"]
            password = decoded_data["password"]
            
            if(user_id not in self.player_ids or password != self.password):
                conn.close()
            
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
            mask_start_pos = (decoded_data["maskTop"], decoded_data["maskLeft"])
            mask_img, origin_region, label = self.quest_generator.get_mask_questions(conn_def, quest_num, task_idx, mask_start_pos)
            
            msg = self.suggest_game_handler.get_msg_task_request(conn_def,
                                                                quest_num,
                                                                mask_img,
                                                                origin_region, 
                                                                label,
                                                                self.image_size[0],
                                                                mask_start_pos
                                                                )
            
            encoded_msg = self.msg_handler.encode(PackageDef.PKT_TASK_REQUEST, msg)
            
            # timeout for display in client side
            # print("Start sleep") 
            # time.sleep(10)
            # print("Finish sleep")
            
            self.suggest_game_handler.add_encoded_msg(encoded_msg, conn_def, quest_num) 
                    
        elif(pkt_type == PackageDef.PKT_SUGGEST_ANSWERS):
            conn_def = decoded_data["def"]
            quest_num = decoded_data["questNumber"]
            index = decoded_data["index"]
            num_quests = decoded_data["numberQuestions"]
            answer = decoded_data["answer"]
            
            assert len(answer) == num_quests, "Something Wrong"
            check_results = self.suggest_game_handler.check_suggest_game_answer(conn_def,
                                                                                quest_num,
                                                                                index,
                                                                                answer)
            
            msg = self.suggest_game_handler.get_msg_suggest_results(conn_def,
                                                                    quest_num,
                                                                    index,
                                                                    num_quests,
                                                                    check_results)
            
            print("MSG: ", msg)
            
            encoded_data = self.msg_handler.encode(PackageDef.PKT_SUGGEST_RESULTS, msg)
            
            # timeout for display in client side
            # time.sleep(self.sleep_time)
            
        elif(pkt_type == PackageDef.PKT_ANSWER_SUBMIT):            
            conn_def = decoded_data["def"]
            quest_num = decoded_data["questNumber"]
            answer = decoded_data["answer"]
            check_result, server_answer = self.suggest_game_handler.check_answer(conn_def, quest_num, answer)
            
            if(check_result == -1):
                # send PKT_SUGGEST_QUESTIONS
                msg = self.suggest_game_handler.get_msg_suggest_quests(conn_def, quest_num)
                encoded_data = self.msg_handler.encode(PackageDef.PKT_SUGGEST_QUESTIONS, msg)
                
            elif(check_result == 1 or check_result == 0):
                if(check_result == 1):
                    # if answer right, increase score
                    player.current_score += 1
                    
                    # send mm server
                    mm_data = {
                        "result": 2,
                        "match": self.match_id,
                        "status": 1,
                        "id1": self.players[0].current_score,
                        "id2": self.players[1].current_score
                        }
                    
                    self.mm_com.update_to_server(mm_data)
                    
                # send PKT_ANSWER_CHECKED
                msg = {
                    "def": conn_def, 
                    "questNumber": quest_num,
                    "result": check_result,
                    "clientAnswer": int(answer),
                    "serverAnswer": server_answer,
                    "numberBlockOpened": player.number_block_opened
                 }
                
                encoded_data = self.msg_handler.encode(PackageDef.PKT_ANSWER_CHECKED, msg)
                # record history 
                player.set_record({"questNumber": quest_num,
                                   "result": check_result,
                                   "clientAnswer": int(answer),
                                   "serverAnswer": server_answer,
                                   "numberBlockOpened": player.number_block_opened
                                   })
                
                    
        if(encoded_data):
            conn.send(encoded_data)
            
        if(pkt_type == PackageDef.PKT_ANSWER_SUBMIT):
            # check if both player are submit results then we can send PKT_ROUND_RESULT
            is_send = self.send_round_results(quest_num)
            print(f"Run in {is_send}", player.player_id)
            
            if(is_send):
                winner = self.check_game_winner()
                # if no player win -> continue to the next question
                if(winner == 0):
                    print("Broadcase pkt select task")
                    time.sleep(1)
                    self.broadcast(PackageDef.PKT_SELECT_TASK) 
                    
                    self.is_send_pkt_round_result = False   
                else:
                    self.broadcast(PackageDef.PKT_END_GAME, winner=winner)
        
    def broadcast(self, pkt_type, **kwargs):
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
                                
            elif(pkt_type == PackageDef.PKT_END_GAME):
                msg = {
                    "def": conn_def,
                    "matchWinner": kwargs["winner"],
                    "player1Point": self.players[0].current_score,
                    "player2Point": self.players[1].current_score,
                }
                
                time.sleep(1)
                encoded_data = self.msg_handler.encode(PackageDef.PKT_END_GAME, msg)
                
                # send to mm server
                mm_data = {"result": 3, "match": self.match_id}
                self.mm_com.update_to_server(mm_data)
                
            conn.sendall(encoded_data)
            
    def send_round_results(self, quest_num):
        is_send = True 
        for player in self.players:
            if(quest_num not in player.player_record):
                is_send = False
        
        is_send = is_send and not self.is_send_pkt_round_result
        if(is_send):
            self.is_send_pkt_round_result = True
            
            player1 = self.players[0]
            player2 = self.players[1]
            quest_info_player1 = player1.player_record[quest_num]
            quest_info_player2 = player2.player_record[quest_num]
            
            for player in self.players:
                conn = player.conn
                
                msg = {
                    "def": player.player_id,
                    "questNumber": quest_num,
                    "code": 1,
                    "winner": self.check_winner_of_question(quest_num),
                    "player1Point": player1.current_score,
                    "player1Result": quest_info_player1["result"],
                    "player1Revealed": quest_info_player1["numberBlockOpened"],
                    "player2Point": player2.current_score,
                    "player2Result": quest_info_player2["result"],
                    "player2Revealed": quest_info_player2["numberBlockOpened"],
                    "errorLen": 0,
                    "error": ""
                }
                
                encoded_data = self.msg_handler.encode(PackageDef.PKT_ROUND_RESULT, msg)
                
                time.sleep(1)
                conn.sendall(encoded_data)
        
        return is_send
                
    def check_winner_of_question(self, quest_num):
        # return player order
        return 1
    
    def check_game_winner(self):
        for player in self.players:
            if(player.current_score >= self.end_score):
                return player.player_order
        
        return 0 # no one win
    
    def mm_server_handler(self, conn, addr):
        while True:
            if(not self.mm_com.is_server_created):
                data = self.mm_com.wait_mm_request(conn)
                if(data):
                    self.match_id = data["match"]
                    self.player_ids = [data["id1"], data["id2"]]
                    self.server_password = data["passwd"]
                else:
                    print("Something wrong")

            print(f"Receive data from {addr}")
            # run main logic
                
    def accept_connections(self):
        conn, address = self.server_socket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        if(not self.is_mm_connect):
            self.is_mm_connect = True
            start_new_thread(self.mm_server_handler, (conn, address))
        
        self.num_players += 1
        print("Current player: ", self.num_players)
        self.connections.append(conn)
        self.addresses.append(address)
        
        player_id = random.randint(1, 1000)
        self.address_to_def[address] = player_id
        player = ClientPlayer(self.num_players, player_id, conn, address)
        self.players.append(player)
        
        self.address2player[address] = player
        self.suggest_game_handler.init_players(player)
        
        if(self.num_players == 2):
            self.game_start = True
            
            # send to mm server
            mm_data = {"result": 1, "match": self.match_id}
            self.mm_com.update_to_server(mm_data)
        
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
                    time.sleep(1)
                    print("LMAO")
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