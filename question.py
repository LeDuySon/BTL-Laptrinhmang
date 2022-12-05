import pandas as pd
import numpy as np
import random
from collections import defaultdict

import cv2

class QuestionGenerator:
    def __init__(self, 
                 num_questions,
                 select_time,
                 number_task,
                 data_path="data/mnist_test.csv",
                 image_size=(40, 40),
                 mask_size=(10, 10)):
        self.num_questions = num_questions
        # time for client select question
        self.select_time = select_time
        self.number_task = number_task
        self.image_size = image_size
        self.mask_size = mask_size
        # image data
        self.df = pd.read_csv(data_path)
                
        # store question generated
        self.questions = defaultdict(list)
        # store num question for each player
        self.questions_counter = defaultdict(int)
       
    def generate(self, player_id):
        self.questions_counter[player_id] += 1
        questions = self.get_questions()
        
        send_msg = {
            "def": player_id,
            "questNumber": self.questions_counter[player_id],
            "time": self.select_time,
            "numberTask": self.number_task
        }
        
        send_questions = []
        for idx, row in questions.iterrows():
            label = row["label"]
            print(row)
            image = row[1:].to_numpy()
            
            send_image = self.preprocess_image(image)
            send_questions.append({"label": label, "image": send_image, "size": self.image_size[0]})
            
        send_msg["taskList"] = send_questions
        self.questions[player_id].append(send_msg)
        return send_msg
    
    def get_mask_questions(self, conn_def, quest_num, task_idx, mask_start_pos):
        print(conn_def, quest_num, task_idx)
        print(self.questions[conn_def])
        
        selected_question = self.questions[conn_def][quest_num - 1]["taskList"][task_idx] # start from
        label = selected_question["label"]
        
        image = selected_question["image"] 
        image = np.reshape(image, self.image_size)
        
        mask_img, origin_region = self.get_mask_image(image, mask_start_pos) 
        
        return mask_img.reshape(-1), origin_region, label
        
    def get_mask_image(self, image, mask_start_pos):
        mask_value = 2
        mask = np.full(self.mask_size, mask_value)
        
        start_row = mask_start_pos[0]
        # start_row = random.randint(0, self.image_size[0] - self.mask_size[0])
        end_row = min(self.image_size[0], start_row + self.mask_size[0])
        
        start_col = mask_start_pos[1]
        # start_col = random.randint(0, self.image_size[1] - self.mask_size[0])
        end_col = min(self.image_size[1], start_col + self.mask_size[1])
        
        origin_region = image[start_row:end_row, start_col:end_col].copy()
        image[start_row:end_row, start_col:end_col] = mask 
        
        return image, origin_region
        
    def preprocess_image(self, image, default_size=(28, 28)): 
        n_image = image.reshape(default_size)
        n_image[n_image < 50] = 0
        n_image[n_image >= 50] = 1
                
        if(default_size != self.image_size):
            n_image = cv2.resize(n_image.astype(np.uint8), self.image_size)
            # cv2.imshow('test', n_image_resized.astype(np.uint8))
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

        return n_image.reshape(-1)
        
    def get_questions(self):
        questions = self.df.sample(self.number_task)
        self.df.drop(questions.index, inplace=True)
        
        questions = questions.reset_index(drop=True)
        # drop selected question -> avoid duplicates
        
        return questions
    
if __name__ == "__main__":
    gen = QuestionGenerator(2, 1, 1)
    print(gen.df.shape)
    
    print(gen.generate(1))
    
