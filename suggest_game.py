from collections import defaultdict

class SuggestGameHandler():
    def __init__(self):
        self.player1 = None
        self.player2 = None
        
        self.player2conn = {}
        
        self.encoded_msg_container = defaultdict(list)
        self.quest_container = defaultdict(list)
        
        self.current_quest = 0
        self.game_start = False
        
    def init_players(self, conn, player_id):
        if(not self.player1):
            self.player1 = player_id 
        elif(not self.player2):
            self.player2 = player_id
        else:
            print("More than 2 players")
            
        self.player2conn[player_id] = conn
            
    def get_msg(self, 
                conn_def, 
                quest_num,
                mask_img,
                origin_region, 
                label,
                img_size,
                mask_start_pos
                ):
        msg = {
                "def": self.player1 if self.player2 == conn_def else self.player2,
                "questNumber": quest_num,
                "time": 10,
                "taskRequest": [{
                    "image": mask_img,
                    "size": img_size
                }],
                "maskTop": mask_start_pos[0], 
                "maskLeft": mask_start_pos[1]
            }
        
        self.quest_container[conn_def].append({
            "mask_img": mask_img,
            "origin_region": origin_region,
            "label": label,
            "img_size": img_size
        })
        
        return msg
    
    def add_encoded_msg(self, encoded_msg, conn_def, quest_num):
        self.current_quest += 1 
        if(self.current_quest % 2 == 0): 
            self.game_start = True
        
        player_id = self.player1 if self.player2 == conn_def else self.player2
        self.encoded_msg_container[player_id].append(encoded_msg)
        
        if(self.game_start):
            self.game_start = False
            for player_id, data in self.encoded_msg_container.items():
                conn = self.player2conn[player_id]
                encoded_data = data[quest_num - 1] # idx start from 0
                
                conn.sendall(encoded_data)
                
    def check_answer(self, conn_def, quest_number, answer):
        # print(conn_def, quest_number)
        # print(len(self.quest_container[conn_def]))
        
        server_answer = self.quest_container[conn_def][quest_number - 1]["label"]
        
        check_result = 0 # -1 nothing, 0 wrong, 1 right
        if(answer == int(server_answer)):
            check_result = 1
        elif(answer == -1):
            check_result = -1
        
        return check_result, server_answer
            
            
        
                
        
        
        
    