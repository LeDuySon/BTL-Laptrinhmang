import random
import numpy as np
from collections import defaultdict
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
class SuggestGameHandler():
    def __init__(self, image_size=(40, 40), test_case_path="data/Testcase2.out"):
        self.image_size = image_size
        # read testcase for suggest game 
        self.num_test_cases = 0
        self.test_cases = self.read_test_cases(test_case_path)
        
        # game play params
        self.player1 = None
        self.player2 = None
        
        self.player2conn = {}
        self.def2player = {}
        
        self.encoded_msg_container = defaultdict(list)
        self.quest_container = defaultdict(list)
        self.quest_index_counter = defaultdict(int) # đếm số thứ tự của lượt đấu gợi ý trog câu hỏi N
        self.quest_index_container = defaultdict(list) # Store index of test cases of question in suggest game
        
        self.current_quest = 0
        self.game_start = False
        
        self.num_quests_per_index = {k:v for k, v in zip(range(1, 6), [36, 28, 20, 12, 4])}
        
    def init_players(self, player):
        if(not self.player1):
            self.player1 = player 
        elif(not self.player2):
            self.player2 = player
        else:
            print("More than 2 players")
            
        self.player2conn[player.player_id] = player.conn
        self.def2player[player.player_id] = player
            
    def get_msg_task_request(self, 
                            conn_def, 
                            quest_num,
                            mask_img,
                            origin_region, 
                            label,
                            img_size,
                            mask_start_pos
                            ):
        msg = {
                "def": self.player1.player_id if self.player2.player_id == conn_def else self.player2.player_id,
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
            "img_size": img_size,
            "mask_start_pos": mask_start_pos
        })
        
        return msg
    
    def get_msg_suggest_quests(self, 
                               conn_def,
                               quest_num
                               ):
        self.quest_index_counter[f"{conn_def}_{quest_num}"] += 1
        
        num_quests = self.num_quests_per_index[self.quest_index_counter[f"{conn_def}_{quest_num}"]]
        quests_idx = random.sample([idx for idx in range(1, self.num_test_cases + 1)], num_quests)
        test_cases = [self.test_cases[idx] for idx in quests_idx]
        
        # store
        self.quest_index_container[f"{conn_def}_{quest_num}"].append(quests_idx)
        
        msg = {
            "def": conn_def,
            "questNumber": quest_num,
            "index": self.quest_index_counter[f"{conn_def}_{quest_num}"],
            "numberQuestions": num_quests,
            "questions": test_cases
            }
        
        return msg
    
    def get_msg_suggest_results(self,
                                conn_def,
                                quest_num,
                                index,
                                num_quests,
                                check_results):
        msg = {
            "def": conn_def,
            "questNumber": quest_num,
            "index": self.quest_index_counter[f"{conn_def}_{quest_num}"],
            "numberQuestions": num_quests,
            "suggestions": None
        }
        
        unmask_val = self.get_unmask_image(conn_def, quest_num, index, check_results)
        msg["suggestions"] = unmask_val
        
        return msg
        
    def get_unmask_image(self, 
                         conn_def,
                         quest_num,
                         index,
                         check_results):
        player_id = self.player1.player_id if self.player2.player_id == conn_def else self.player2.player_id
        quest_info = self.quest_container[player_id][quest_num - 1]
        
        print("Origin region: ", quest_info["origin_region"])
        
        mask_start_pos = quest_info["mask_start_pos"] # index question 0
        # not minus 1 in pos[1] because dx will be 1 when we start
        current_mask_start_pos = (mask_start_pos[0] + (index - 1), mask_start_pos[1] + (index-2)) # current index
        
        y, x = current_mask_start_pos # top, left
        
        turn_dir = {
            0: [1, 0],
            1: [0, 1],
            2: [-1, 0],
            3: [0, -1]
            }
        
        turn = 0
        
        unmask_val = []
        for idx, r in enumerate(check_results):
            dx, dy = turn_dir[turn]
            x += dx
            y += dy
            
            if(quest_info["mask_img"][(y + dy)*self.image_size[0] + (x+dx)] != 2):
                turn += 1
                print(f"Turn {turn}")
                
            if(r == 0): # wrong -> dont unmask
                unmask_val.append(2)
                continue
            
            quest_info["mask_img"][y*self.image_size[0] + x] = quest_info["origin_region"][y - mask_start_pos[0]][x - mask_start_pos[1]]
            unmask_val.append(quest_info["mask_img"][y*self.image_size[0] + x])
                
        return unmask_val
    
    def add_encoded_msg(self, encoded_msg, conn_def, quest_num):
        self.current_quest += 1 
        if(self.current_quest % 2 == 0): 
            self.game_start = True
        
        player_id = self.player1.player_id if self.player2.player_id == conn_def else self.player2.player_id
        self.encoded_msg_container[player_id].append(encoded_msg)
        
        if(self.game_start):
            self.game_start = False
            for player_id, data in self.encoded_msg_container.items():
                conn = self.player2conn[player_id]
                encoded_data = data[quest_num - 1] # idx start from 0
                
                conn.sendall(encoded_data)
                
    def check_answer(self, conn_def, quest_number, answer):
        server_answer = self.quest_container[conn_def][quest_number - 1]["label"]
        
        check_result = 0 # 100 no answer, 0 wrong, 1 right
        if(answer == 1):
            check_result = 1
        elif(answer == 100):
            check_result = -1
        else:
            check_result = 0 # wrong
        
        return check_result, server_answer
    
    def check_suggest_game_answer(self, 
                                  conn_def, 
                                  quest_num, 
                                  index,
                                  answer):
        indexes = self.quest_index_container[f"{conn_def}_{quest_num}"][index-1]
        server_answer = [self.test_cases[index]["res"] for index in indexes]
        
        assert len(answer) == len(server_answer), f"Client answer {len(answer)} != Server answer {len(server_answer)}"
        
        player = self.def2player[conn_def]
        
        results = []
        for c, s in zip(answer, server_answer):
            if(c != s):
                results.append(0)
            else:
                player.number_block_opened += 1
                results.append(1) 
                
        return results 
    
    def read_test_cases(self, test_case_path):
        test_cases = {}
        current_test = None
        line_inp = False
        
        with open(test_case_path, "r") as f:
            for line in f:
                elem = line.strip().split(":")
                if(elem[0] == "test"):
                    current_test = int(elem[1].strip())
                    test_cases[current_test] = {
                        "pos": [], # position of 1 in matrix
                        "res": [], # number of connected components
                        "size": None, # matrix size n*n
                        "num_ones": None
                    }
                    
                    self.num_test_cases += 1
                    line_inp = True
                elif(line_inp):
                    n, k = list(map(int, elem[0].split(" ")))
                    test_cases[current_test]["size"] = n
                    test_cases[current_test]["num_ones"] = k
                    
                    line_inp = False
                elif(elem[0] == "res"):
                    test_cases[current_test]["res"] = int(elem[1].strip())
                else:
                    x, y = elem[0].split(" ")
                    test_cases[current_test]["pos"].append(Point(int(x) - 1, int(y) - 1))
                    
        return test_cases
    
    
if __name__ == "__main__":
    test = SuggestGameHandler()
    out = test.read_test_cases()
    
    print(out[1])
            
            
        
                
        
        
        
    