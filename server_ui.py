import tkinter as tk 
from tkinter import *
from tkinter import ttk
import threading
import time

class ServerUI:

    def __init__(self):
        self.main_windows = None
        self.main_windows_size = ['712', '712']
        self.main_windows_resizable = [False, True]

        # This frame is used to display players' score
        self.score_frame = None
        self.player1_score = None
        self.player2_score = None

        # This frame is used to display when less than 2 players connected
        self.waiting_frame = None

        # This frame is used to display playing scene
        self.playing_frame = None

        # Thread used to run UI
        self.UI_thread = None


    def start_UI_thread(self):
        self.UI_thread = threading.Thread(target = self.create_UI_thread, args=())
        self.UI_thread.start() 
    
    def create_UI_thread(self):
        self.main_windows = tk.Tk()
        self.main_windows.geometry(self.main_windows_size[0] + 'x' + self.main_windows_size[1])
        self.main_windows.resizable(self.main_windows_resizable[0], self.main_windows_resizable[1])
        self.main_windows.title("Guess Number")
        ttk.Label(self.main_windows, text = "Guess Number", font = ("Arial", 20)).pack()
        self.create_waiting_frame()
        self.main_windows.mainloop()

    def create_score_frame(self):
        self.score_frame = tk.Frame(self.playing_frame)
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

    def create_playing_frame(self):
        self.playing_frame = tk.Frame(self.main_windows)
        self.playing_frame.pack(expand = False)
        separator = ttk.Separator(self.playing_frame, orient='horizontal')
        separator.pack(fill='x')
        ttk.Label(self.playing_frame, text = "Playing", font = ("Arial", 16)).pack()
        self.create_score_frame()
        self.display_score(2, 3)
        separator = ttk.Separator(self.playing_frame, orient='horizontal')
        separator.pack(fill='x')

    def change_from_waiting_to_playing_frame(self):
        self.waiting_frame.destroy()
        self.create_playing_frame()

    def change_from_playing_to_waiting_frame(self):
        self.playing_frame.destroy()
        self.score_frame.destroy()
        self.create_waiting_frame()


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
    
