import tkinter as tk 
from tkinter import *
from tkinter import ttk
from _thread import *
import time

class ServerUI:

    def __init__(self):
        self.main_windows = None
        self.main_windows_size = ['1000', '820']
        self.main_windows_resizable = [False, True]

        self.players = None
        # This frame is used to display players' score
        self.score_frame = None
        self.player1_score = None
        self.player2_score = None

        # This frame is used to display when less than 2 players connected
        self.waiting_frame = None
        
        # This frame is used to display when player finished select task
        self.select_task_frame = None
        self.taskListDisplaying = None
        
        # This frame is used to display when player finished select task
        self.task_selected_frame = None

        # This frame is used to display playing scene
        self.suggest_playing_frame = None
        
        self.color = ['white', 'gray', 'black']

    def start_UI_thread(self):
        start_new_thread(self.create_UI_thread, ()) 
    
    def create_UI_thread(self):
        self.main_windows = tk.Tk()
        self.main_windows.geometry(self.main_windows_size[0] + 'x' + self.main_windows_size[1])
        self.main_windows.resizable(self.main_windows_resizable[0], self.main_windows_resizable[1])
        self.main_windows.title("Guess Number")
        ttk.Label(self.main_windows, text = "Guess Number", font = ("Arial", 20)).pack()
        self.create_score_frame()
        self.create_waiting_frame()
        self.main_windows.mainloop()

    def create_score_frame(self):
        self.score_frame = tk.Frame(self.main_windows)
        self.score_frame.pack(expand = False)

        ttk.Label(self.score_frame, text = "", font = 'Arial 12').grid(column=2, row=0, padx=0, pady=0)
        ttk.Label(self.score_frame, text = "Player 1 score:", font='Arial 12').grid(column=0, row=1, padx = 0, pady = 0)
        self.player1_score = ttk.Label(self.score_frame, font='Arial 12')	
        self.player1_score.grid(column=1, row=1, padx = 0, pady = 0)
        ttk.Label(self.score_frame, text = "                     ", font = 'Arial 12').grid(column=2, row=1, padx=0, pady=0)
        ttk.Label(self.score_frame, text = "Player 2 score:", font='Arial 12').grid(column=3, row=1, padx = 0, pady = 0)
        self.player2_score = ttk.Label(self.score_frame, font='Arial 12')
        self.player2_score.grid(column=4, row=1, padx = 0, pady = 0)
        ttk.Label(self.score_frame, text = "", font = 'Arial 12').grid(column=2, row=2, padx=0, pady=0)
        self.display_score(0, 0)

    def display_score(self, player1_score, player2_score):
        self.player1_score['text'] = str(player1_score)
        self.player2_score['text'] = str(player2_score)

    def create_waiting_frame(self):
        self.waiting_frame = tk.Frame(self.main_windows)
        self.waiting_frame.pack(expand = False)
        separator = ttk.Separator(self.waiting_frame, orient='horizontal')
        separator.pack(fill='x')
        ttk.Label(self.waiting_frame, text = "Waiting player connect", font = ("Arial", 16)).pack()
        
    def create_select_tasks_frame(self):
        if (self.select_task_frame):
            self.select_task_frame.destroy()

        self.select_task_frame = ttk.Frame(self.main_windows)
        self.select_task_frame.pack()
        
        ttk.Label(self.select_task_frame, text = "Select Tasks Phase", font = ("Arial", 16)).grid(column=1, row=0, padx=0, pady=0)
        ttk.Separator(self.select_task_frame, orient='horizontal').grid(column=1, row=1, padx=0, pady=0)
        ttk.Label(self.select_task_frame, text = "                     ", font = 'Arial 12').grid(column=1, row=3, padx=0, pady=0)
        
    def display_task_list_frame_all(self, infos):
        if (not self.select_task_frame):
            self.create_select_tasks_frame()
        
        self.display_score(self.players[0].current_score, self.players[1].current_score)
        
        for info in infos:
            playerOrder, taskList = info 
            self.display_task_list_frame(playerOrder, taskList)
        
    def display_task_list_frame(self, playerOrder, taskList):
        col_idx = int(playerOrder) - 1
        if(int(playerOrder) == 2):
            col_idx += 1
        
        ttk.Label(self.select_task_frame, text = f"Player {playerOrder}", font = 'Arial 12').grid(column=col_idx, row=2, padx=0, pady=0)
        self.taskListDisplaying = ttk.Notebook(self.select_task_frame) 
        self.taskListDisplaying.grid(column=col_idx, row=3, padx=10, pady=10)
        for task in taskList:
                if (task):
                    self.display_task(400, 400, [2, 2], 'Task ', task["size"], task["image"], 400, 30, task["label"])
    
    def display_task(self, w, h, offset, title, imageSize, image, valueW, valueH, value=None):
        canvas = tk.Canvas(self.taskListDisplaying, width = w + offset[0], height = h + offset[1] + valueH)
        canvas.pack(fill='both', expand=False)
        self.taskListDisplaying.add(canvas, text=title)
        for row in range(imageSize):
            for col in range(imageSize):
                imageStartPos = (col * int(w / imageSize) + offset[0], row * int(h / imageSize) + offset[1])
                imageEndPos = ((col + 1) * int(w / imageSize) + offset[0], (row + 1) * int(h / imageSize) + offset[1])
                canvas.create_rectangle(imageStartPos, imageEndPos, fill = self.color[image[row * imageSize + col]])
                if(value):
                    canvas.create_text((200, 415), text = "Value = " + str(value), font = 'Arial 12')
                
    def create_task_selected_frame(self):
        if (self.task_selected_frame):
            self.task_selected_frame.destroy()

        self.task_selected_frame = ttk.Frame(self.main_windows)
        self.task_selected_frame.pack()
        
        ttk.Label(self.task_selected_frame, text = "Task Selected Phase", font = ("Arial", 16)).grid(column=1, row=0, padx=0, pady=0)
        # self.create_score_frame(self.task_selected_frame)
        
    def display_selected_task_frame(self, infos):
        if (not self.task_selected_frame):
            self.create_task_selected_frame()
        
        self.display_score(self.players[0].current_score, self.players[1].current_score)
        for info in infos:
            playerOrder, maskImg = info
            self.display_selected_task_each(playerOrder, maskImg)
        
    def display_selected_task_each(self, playerOrder, taskSelected):
        col_idx = int(playerOrder) - 1
        if(int(playerOrder) == 2):
            col_idx += 1
        
        ttk.Label(self.task_selected_frame, text = f"Player {playerOrder} selected", font = 'Arial 12').grid(column=col_idx, row=4, padx=0, pady=0)
        self.display_selected_task(self.task_selected_frame, col_idx, 400, 400, [2, 2], 'Task ', taskSelected["size"], taskSelected["image"], 400, 30, taskSelected["label"])
            
    def display_selected_task(self, target_frame, col_idx, w, h, offset, title, imageSize, image, valueW, valueH, value=None):
        canvas = tk.Canvas(target_frame, width = w + offset[0], height = h + offset[1] + valueH)
        canvas.grid(column=col_idx, row=5, padx=0, pady=0)
        for row in range(imageSize):
            for col in range(imageSize):
                imageStartPos = (col * int(w / imageSize) + offset[0], row * int(h / imageSize) + offset[1])
                imageEndPos = ((col + 1) * int(w / imageSize) + offset[0], (row + 1) * int(h / imageSize) + offset[1])
                canvas.create_rectangle(imageStartPos, imageEndPos, fill = self.color[image[row * imageSize + col]])
                if(value):
                    canvas.create_text((200, 415), text = "Value = " + str(value), font = 'Arial 12')
    
    def create_suggest_playing_frame(self):
        if (self.suggest_playing_frame):
            self.suggest_playing_frame.destroy()

        self.suggest_playing_frame = ttk.Frame(self.main_windows)
        self.suggest_playing_frame.pack()
        
        ttk.Label(self.suggest_playing_frame, text = "Playing Phase", font = ("Arial", 16)).grid(column=1, row=0, padx=0, pady=0)
        
    def display_suggest_playing_frame(self, infos):
        if (not self.suggest_playing_frame):
            self.create_suggest_playing_frame()
        
        self.display_score(self.players[0].current_score, self.players[1].current_score)
        for info in infos:
            playerOrder, maskImg = info
            self.display_suggest_playing_each(playerOrder, maskImg)
        
    def display_suggest_playing_each(self, playerOrder, taskSelected):
        col_idx = int(playerOrder) - 1
        if(int(playerOrder) == 2):
            col_idx += 1
        
        ttk.Label(self.suggest_playing_frame, text = f"Player {playerOrder}", font = 'Arial 12').grid(column=col_idx, row=4, padx=0, pady=0)
        self.display_selected_task(self.suggest_playing_frame, col_idx, 400, 400, [2, 2], 'Task ', taskSelected["size"], taskSelected["image"], 400, 30)
        
    def change_from_waiting_to_select_tasks_frame(self):
        self.waiting_frame.destroy()
        self.create_playing_frame()
        
    def change_from_select_tasks_to_task_selected_frame(self, infos):
        if(self.select_task_frame):
            self.select_task_frame.destroy()
        self.task_selected_frame = None
        self.display_selected_task_frame(infos)

    def change_from_waiting_to_select_tasks_frame(self, taskList):
        self.waiting_frame.destroy()
        self.display_task_list_frame_all(taskList)
        
    def change_from_selected_task_to_select_tasks_frame(self, taskList):
        if(self.select_task_frame):
            self.select_task_frame.destroy()
            self.select_task_frame = None
        if(self.task_selected_frame):
            self.task_selected_frame.destroy()
        if(self.suggest_playing_frame):
            self.suggest_playing_frame.destroy()
            self.suggest_playing_frame = None
            
        self.display_task_list_frame_all(taskList)
        
    def change_from_task_selected_to_play_frame(self, taskList):
        if(self.task_selected_frame):
            self.task_selected_frame.destroy()
        self.task_selected_frame = None
        self.display_suggest_playing_frame(taskList)
    


if __name__ == "__main__":
    # Start the UI thread
    serverUI = ServerUI()
    serverUI.start_UI_thread()

    # Run code logic (if exists)
    for i in range (5):
        print (str(4 - i), " seconds to start the game...")
        time.sleep(1)
    serverUI.change_from_waiting_to_playing_frame()
    for i in range (5):
        print (str(4 - i), " seconds to end the game...")
        time.sleep(1)
    serverUI.change_from_playing_to_waiting_frame()

    
    # while(True):
    #     time.sleep(1)
    #     print("Son gae")
    
