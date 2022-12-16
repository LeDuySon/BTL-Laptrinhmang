import socket
import struct
import random
import numpy as np
import tkinter as tk 
from tkinter import *
from tkinter import ttk
import threading
from guess_number import NumberGuesser

# define a number with mapping array
class QuestionNumber:
      defineNumber = 0 # the number
      imageSize = 0 # size of mapping number by array
      mappingArr = None # mapping number by array 

class Location:
      def __init__(self, row, col):
            self.row = row
            self.col = col

class Client2:
      

      def __init__(self):
            # create connect
            self.host = None
            self.port = 0

            # define package type name
            self.PKT_HELLO = 0
            self.PKT_ACCEPT_CONNECT = 1
            self.PKT_START = 2
            self.PKT_SELECT_TASK = 3
            self.PKT_TASK_SELECTED = 4
            self.PKT_TASK_REQUEST = 5
            self.PKT_SUGGEST_QUESTIONS = 6
            self.PKT_SUGGEST_ANSWERS = 7
            self.PKT_SUGGEST_RESULTS = 8
            self.PKT_ANSWER_SUBMIT = 9
            self.PKT_ANSWER_CHECKED = 10
            self.PKT_ROUND_RESULTS = 11
            self.PKT_END_GAME = 12

            self.datarecv = None

            # define user identity
            self.defineUser = 19020046

            self.ListQuestionNumber = []
            self.curGuessingNumberMap = None
            self.curGuessingNumberSmallMap = None #10x10 
            self.numBlockleft = None
            self.curSuggestQuestion = 0
            self.CurGuessingLocation = None
            self.curTaskImageSize = None
            self.AnsweredGuessQuestion = 0
            self.curTotalAnsweredGuess = 0

            # for finding connected
            self.VisitedLocation = None
            self.curGuessingMap = None
            self.curListLocation = None
            self.curArraySize = None
            self.curNumberBlock = None
            self.dx = [0, 1, -1, 0]
            self.dy = [1, 0, 0, -1]

            self.HashingMapForSmallMap = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                    [36, 37, 38, 39, 40, 41, 42, 43, 44, 11],
                                    [35, 64, 65, 66, 67, 68, 69, 70, 45, 12],
                                    [34, 63, 84, 85, 86, 87, 88, 71, 46, 13],
                                    [33, 62, 83, 96, 97, 98, 89, 72, 47, 14],
                                    [32, 61, 82, 95, 100, 99, 90, 73, 48, 15],
                                    [31, 60, 81, 94, 93, 92, 91, 74, 49, 16],
                                    [30, 59, 80, 79, 78, 77, 76, 75, 50, 17],
                                    [29, 58, 57, 56, 55, 54, 53, 52, 51, 18],
                                    [28, 27, 26, 25, 24, 23, 22, 21, 20, 19]]


            # UI
            self.main_windows = None
            self.login_frame_name = 'Login'
            self.login_frame = None

            self.playing_frame_name = 'Playing'
            self.playing_frame = None
            
            self.score_frame_name = 'Score'
            self.scoreFrame = None
            self.yourScoreDisplaying = None
            self.opponentScoreDisplaying = None
            
            self.select_task_frame_name = 'Select Task'
            self.select_task_frame = None
            
            self.task_list_frame_name = 'Task List'
            self.taskListDisplaying = None
            self.taskSelectInput = None
            self.maskXInput = None
            self.maskYInput = None
            
            self.answer_frame_name = 'Answer'
            self.answer_frame = None
            self.question = None
            self.question_canvas = None
            self.submit_frame = None
            self.answer_input = None
            
            self.color = ['white', 'gray', 'black']
            self.taskList = []

            #Threading
            self.data_thread = None

            self.AIGuessing = NumberGuesser("checkpoints/mnist-12.onnx")

            self.questionNumber = 0

      
      


      def GetLocationGuessNumber(self, x):
            for i in range(10):
                  for j in range(10):
                        if(self.HashingMapForSmallMap[i][j] == x):
                              return i, j

      def SolveSuggestQuestion(self):
            ans = 0
            self.VisitedLocation = np.zeros((self.curArraySize, self.curArraySize),dtype = np.int32)
            self.curGuessingMap = np.zeros((self.curArraySize, self.curArraySize),dtype = np.int32)
            for item in self.curListLocation:
                  self.curGuessingMap[item.row][item.col] = 1
            for i in range(self.curArraySize):
                  for j in range(self.curArraySize):
                        print(self.curGuessingMap[i][j], end = "")
                  print("")
            for i in range(self.curArraySize):
                  for j in range(self.curArraySize):
                        self.curLocation = Location(i, j)
                        if(self.curGuessingMap[i][j] == 0 and  self.VisitedLocation[i][j] == 0):
                              ans = ans + 1
                              print("i j:", i, j)
                              self.DFS(i, j)

            return ans

      def DFS(self, i, j):
            self.VisitedLocation[i][j] = 1
            for t in range(4):
                  x = i + self.dx[t]
                  y = j + self.dy[t]
                  if(x < 0 or x >= self.curArraySize):
                        continue
                  if(y < 0 or y >= self.curArraySize):
                        continue
                  self.curLocation = Location(x, y)
                  if(self.curGuessingMap[x][y] == 0 and  self.VisitedLocation[x][y] == 0):
                        print("x y:",x,y)
                        self.DFS(x, y)

      # encode to send data
      # items contains int and string only
      def Encode(self, *items):
            data = bytearray()
            for item in items:
                  if(isinstance(item, str)):
                        data.extend(item.encode())
                  elif(isinstance(item, int)):
                        data.extend(item.to_bytes(4, byteorder = 'little'))
                  elif(isinstance(item, list)):
                        for i in item:
                              data.extend(i.to_bytes(4, byteorder = 'little'))
            return data

      #print(Encode(100))
      # decode data receive
      # type and len is integer, data still remain bytearray
      def Decode(self, item):
            type = int.from_bytes(item[0 : 4], byteorder = 'little')
            Len = int.from_bytes(item[4 : 8], byteorder = 'little')
            data = self.datarecv[8 : 8 + Len]
            return type, Len, data

      def create_connect(self, ip, port):
            self.host = ip
            self.port = int(port)
            self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.client.connect((self.host,self.port))
            print("connect successfully")

      def send_hello(self, user_id, password):
            # send Hello
            Hello_package = self.Encode(self.PKT_HELLO, 8, user_id, password)
            print(Hello_package)
            self.client.send(Hello_package)
            print("hello package send successfully")
            self.datarecv = self.client.recv(12400)

      def start_data_transfer(self):
            # start the loop
            while(self.datarecv):
                  # decode datarecv
                  type, Len, data = self.Decode(self.datarecv);
                  while(len(data) < Len):
                        leftoverData = self.client.recv(12400)
                        data = data + leftoverData
                  # server allow to connect
                  if(type == self.PKT_ACCEPT_CONNECT): #status of people joining
                        print(data)
                        self.defineUser = int.from_bytes(data[0 : 4], byteorder = 'little')

                  # send verify package
                  if(type == self.PKT_START):
                        print(data)

                  # list questions from server
                  if(type == self.PKT_SELECT_TASK):
                        #data[0 : 4] is defineUser
                        self.questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
                        time = int.from_bytes(data[8 : 12], byteorder = 'little')
                        numberTask = int.from_bytes(data[12 : 16], byteorder = 'little')
                        print("questNumber: ", self.questNumber,"\n")
                        print("numberTask: ", numberTask,"\n")
                        #get list questions
                        oldIndex = 16
                        for task in range(numberTask):
                              self.curQuestion = QuestionNumber()

                              #get defineNumber
                              defineNumber = int.from_bytes(data[oldIndex + 0 : oldIndex + 4], byteorder = 'little')
                              self.curQuestion.defineNumber = defineNumber

                              #get imageSize
                              imageSize = int.from_bytes(data[oldIndex + 4 : oldIndex + 8], byteorder = 'little')
                              self.curQuestion.imageSize = imageSize
                              print("defineNumber: ", defineNumber)
                              print("imageSize: ", imageSize)
                              oldIndex = oldIndex + 8
                              #get mappingArr
                              mappingArr = np.zeros((imageSize,imageSize),dtype = np.int32)
                              for i in range(imageSize):
                                    for j in range(imageSize):
                                          mappingArr[i][j] = int.from_bytes(data[oldIndex + 0: oldIndex + 1], byteorder = 'little')
                                          oldIndex = oldIndex + 1
                              self.curQuestion.mappingArr = mappingArr

                              # debug mappingArr
                              for i in range(imageSize):
                                    for j in range(imageSize):
                                          print(mappingArr[i][j], end = "")
                                    print("")

                              #add curquestion to list question
                              self.ListQuestionNumber.append(self.curQuestion)
                        self.display_task_list_frame(self.ListQuestionNumber)

                        #select question index then send to server
                        # finalSelectquestionIndex = random.randrange(numberTask)
                        # Task_selected_package = self.Encode(self.PKT_TASK_SELECTED, 20, self.defineUser, questNumber, finalSelectquestionIndex, 20, 20) #assume that blank cover is from (1,1) to (10,10)
                        # self.client.send(Task_selected_package)

                  #receive question from server
                  if(type == self.PKT_TASK_REQUEST):
                        # get data from task
                        #data[0 : 4] is defineUser
                        self.questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
                        time = int.from_bytes(data[8 : 12], byteorder = 'little')

                        taskImagesize = int.from_bytes(data[12 : 16], byteorder = 'little')
                        self.curTaskImageSize = taskImagesize

                        self.curGuessingNumberMap = np.zeros((taskImagesize,taskImagesize),dtype = np.int32)
                        self.curGuessingNumberSmallMap = np.zeros((10,10),dtype = np.int32)
                        for i in range(10):
                              for j in range(10):
                                    self.curGuessingNumberSmallMap[i][j] = 2
                        print("questNumber: ", self.questNumber)
                        print("imageSize: ", taskImagesize)
                        oldIndex = 16
                        for i in range(taskImagesize):
                              for j in range(taskImagesize):
                                    self.curGuessingNumberMap[i][j] = int.from_bytes(data[oldIndex + 0: oldIndex + 1], byteorder = 'little')
                                    oldIndex = oldIndex + 1
                        x = int.from_bytes(data[oldIndex + 0: oldIndex + 4], byteorder = 'little')
                        y = int.from_bytes(data[oldIndex + 4: oldIndex + 8], byteorder = 'little')
                        self.CurGuessingLocation = Location(x, y)
                        for i in range(taskImagesize):
                              for j in range(taskImagesize):
                                    print(self.curGuessingNumberMap[i][j], end = "")
                              print("")

                        self.display_question(40, self.curGuessingNumberMap.reshape(-1))
                        self.curSuggestQuestion = 0
                        
                  # receive suggestion questions
                  if(type == self.PKT_SUGGEST_QUESTIONS):
                        #data[0 : 4] is defineUser
                        questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
                        index = int.from_bytes(data[8 : 12], byteorder = 'little')
                        numberQuestions = int.from_bytes(data[12 : 16], byteorder = 'little')
                        print("numberQuestions: ", numberQuestions)
                        oldIndex = 16
                        AnswerArray = []
                        for i in range(numberQuestions):
                              ArraySize = int.from_bytes(data[oldIndex + 0 : oldIndex + 4], byteorder = 'little')
                              self.curArraySize = ArraySize
                              print("ArraySize: ", ArraySize)

                              numberBlock = int.from_bytes(data[oldIndex + 4 : oldIndex + 8], byteorder = 'little')
                              self.curNumberBlock = numberBlock

                              oldIndex = oldIndex + 8
                              ListLocation = []
                              print("numberBlock:", numberBlock)
                              for j in range(numberBlock):
                                    Numberrow = int.from_bytes(data[oldIndex + 0 : oldIndex + 1], byteorder = 'little')
                                    Numbercol = int.from_bytes(data[oldIndex + 1 : oldIndex + 2], byteorder = 'little')
                                    print(Numbercol, " ", Numberrow)
                                    oldIndex = oldIndex + 2
                                    LocationNum = Location(Numberrow, Numbercol)
                                    ListLocation.append(LocationNum)
                              self.curListLocation = ListLocation
                              AnswerArray.append(self.SolveSuggestQuestion())
                        Suggest_answers_package = self.Encode(self.PKT_SUGGEST_ANSWERS, 16 + numberQuestions * 4, self.defineUser, questNumber, index, numberQuestions, AnswerArray)
                        self.client.send(Suggest_answers_package)
                  #receive results
                  if(type == self.PKT_SUGGEST_RESULTS):
                        self.AnsweredGuessQuestion = self.AnsweredGuessQuestion + 1
                        if(self.curTotalAnsweredGuess == 100):
                              self.curTotalAnsweredGuess = 0
                        #data[0 : 4] is defineUser
                        questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
                        index = int.from_bytes(data[8 : 12], byteorder = 'little')
                        numberQuestions = int.from_bytes(data[12 : 16], byteorder = 'little')
                        oldIndex = 16
                        for i in range(numberQuestions):
                              suggestionValue = int.from_bytes(data[oldIndex + 0 : oldIndex + 1], byteorder = 'little')
                              oldIndex = oldIndex + 1
                              self.curTotalAnsweredGuess = self.curTotalAnsweredGuess + 1
                              print(suggestionValue)
                              tempRow, tempCol = self.GetLocationGuessNumber(self.curTotalAnsweredGuess)
                              self.curGuessingNumberSmallMap[tempRow][tempCol] = suggestionValue
                        print("curTaskImageSize: ",self.curTaskImageSize)
                        for i in range(10):
                              for j in range(10):
                                    self.curGuessingNumberMap[self.CurGuessingLocation.row + i][self.CurGuessingLocation.col + j] = self.curGuessingNumberSmallMap[i][j]

                        print("curGuessingNumberSmallMap:")
                        for i in range(10):
                              for j in range(10):
                                    print(self.curGuessingNumberSmallMap[i][j], end = "")
                              print("")

                        print("curGuessingNumberMap:")
                        for i in range(self.curTaskImageSize):
                              for j in range(self.curTaskImageSize):
                                    print(self.curGuessingNumberMap[i][j], end = "")
                              print("")
                        guessednumber = self.AIGuessing.run(self.curGuessingNumberMap)
                        print("guessednumber: ", guessednumber)
                        Answer_submit_package = self.Encode(self.PKT_ANSWER_SUBMIT, 12, self.defineUser, questNumber, int(guessednumber))
                        self.client.send(Answer_submit_package)

                  #confirm the answers from server
                  if(type == self.PKT_ANSWER_CHECKED):
                        #data[0 : 4] is defineUser
                        questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
                        result = int.from_bytes(data[8 : 12], byteorder = 'little')
                        clientAnswer = int.from_bytes(data[12 : 16], byteorder = 'little')
                        serverAnswer = int.from_bytes(data[16 : 20], byteorder = 'little')
                        numBlockOpened = int.from_bytes(data[20 : 24], byteorder = 'little')
                        print("result: ", result)
                  #server sent result
                  if(type == self.PKT_ROUND_RESULTS):
                        #data[0 : 4] is defineUser
                        questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
                        code = int.from_bytes(data[8 : 12], byteorder = 'little')
                        winner = int.from_bytes(data[12 : 16], byteorder = 'little')
                        playerPoint = int.from_bytes(data[16 : 20], byteorder = 'little')
                        playerResult = int.from_bytes(data[20 : 24], byteorder = 'little')
                        playerRevealed = int.from_bytes(data[24 : 28], byteorder = 'little')
                        errorLen = int.from_bytes(data[28 : 32], byteorder = 'little')
                        error = data[32: 32 + errorLen];

                  # #end game
                  if(type == self.PKT_END_GAME):
                        #data[0 : 4] is defineUser
                        matchWinner = int.from_bytes(data[4 : 8], byteorder = 'little')
                        player1Point = int.from_bytes(data[8 : 12], byteorder = 'little')
                        player2Point = int.from_bytes(data[12 : 16], byteorder = 'little')
                  # get package from server
                  self.datarecv = self.client.recv(12400)

      def start_data_thread(self):
            self.data_thread = threading.Thread(target = self.start_data_transfer, args=())
            self.data_thread.start() 

      def run(self):
            self.main_windows = tk.Tk()
            self.main_windows.geometry('712x712')
            self.main_windows.resizable(False, True)
            self.main_windows.title("Guess Number")
            ttk.Label(self.main_windows, text = "Guess Number", font = ("Arial", 20)).pack()
            self.create_login_frame()
            
            self.main_windows.mainloop()

            

            

      def create_frame(self, frame_name):
            if (frame_name == self.login_frame_name):
                  self.create_login_frame()
            elif (frame_name == self.playing_frame_name):
                  self.create_playing_frame()
            elif (frame_name == self.score_frame_name):
                  self.create_score_frame()
            elif (frame_name == self.select_task_frame_name):
                  self.create_select_tasks_frame()
            elif (frame_name == self.answer_frame_name):
                  self.create_answer_frame()
            elif (frame_name == self.task_list_frame_name):
                  self.display_task_list_frame()

      def create_login_frame(self):
            self.login_frame = ttk.Frame(self.main_windows) 
            self.login_frame.pack(padx=10, pady=10, fill='x', expand=True)
            ttk.Label(self.login_frame, text = "Connect to server", font = ("Arial", 16)).pack()
            ip_label = ttk.Label(self.login_frame, text="IP Address:") 
            ip_label.pack(fill='x', expand=True) 
            ip_entry = ttk.Entry(self.login_frame, textvariable=tk.StringVar() ) 
            ip_entry.pack(fill='x', expand=True) 
            ip_entry.insert(0, "127.0.0.1")
            port_label = ttk.Label(self.login_frame, text="Port Number:") 
            port_label.pack(fill='x', expand=True) 
            port_entry = ttk.Entry(self.login_frame, textvariable=tk.StringVar() ) 
            port_entry.pack(fill='x', expand=True) 
            port_entry.insert(0, "6969")
            uid_label = ttk.Label(self.login_frame, text="User Id:")
            uid_label.pack(fill='x', expand=True)
            uid_entry = ttk.Entry(self.login_frame, textvariable=tk.StringVar() )
            uid_entry.pack(fill='x', expand=True)
            uid_entry.insert(0, "22")
            pass_label = ttk.Label(self.login_frame, text="Password:")
            pass_label.pack(fill='x', expand=True)
            pass_entry = ttk.Entry(self.login_frame, textvariable=tk.StringVar() )
            pass_entry.pack(fill='x', expand=True)
            pass_entry.insert(0, "111")
            login_button = ttk.Button(self.login_frame, text="Connect now!", command= lambda: self.onclick_login(ip_entry.get(), port_entry.get(), uid_entry.get(), pass_entry.get())) 
            login_button.pack(fill='x', expand=True, pady=10)

      def onclick_login(self, ip_address, port_number, user_id, password):
            print("login ", ip_address , " ", port_number, " ", user_id)
            if (True):
                  self.change_frame(self.login_frame_name, self.playing_frame_name)
            else:
                  print("Failed to connect")
            # if connect successfully, destroy login frame and create playing frame
            self.create_connect(ip_address, port_number)
            self.send_hello(user_id, password)
            self.start_data_thread()
            

      def create_playing_frame(self):
            self.playing_frame = ttk.Frame(self.main_windows)
            self.playing_frame.pack()
            ttk.Label(self.playing_frame, text = "Playing", font = ("Arial", 16)).pack()
            self.create_frame(self.score_frame_name)
            separator = ttk.Separator(self.playing_frame, orient='horizontal')
            separator.pack(fill='x')
            self.create_frame(self.select_task_frame_name)
            

      def create_score_frame(self):
            self.scoreFrame = tk.Frame(self.playing_frame, height = 800, width = 200)
            self.scoreFrame.pack(expand = False)

            ttk.Label(self.scoreFrame, text = "Your score:", font='Arial 12').grid(column=0, row=0, padx = 0, pady = 0)
            self.yourScoreDisplaying = ttk.Label(self.scoreFrame, font='Arial 12')	
            self.yourScoreDisplaying.grid(column=1, row=0, padx = 0, pady = 0)
            ttk.Label(self.scoreFrame, text = "Opponent score:", font='Arial 12').grid(column=0, row=1, padx = 0, pady = 0)
            self.opponentScoreDisplaying = ttk.Label(self.scoreFrame, font='Arial 12')
            self.opponentScoreDisplaying.grid(column=1, row=1, padx = 0, pady = 0)
            self.display_score(0, 0)

      def display_score(self, yourScore, opponentScore):
            self.yourScoreDisplaying['text'] = str(yourScore)
            self.opponentScoreDisplaying['text'] = str(opponentScore)


      def create_select_tasks_frame(self):
            if (self.select_task_frame):
                  self.select_task_frame.destroy()

            self.select_task_frame = ttk.Frame(self.playing_frame)
            self.select_task_frame.pack()
            
            ttk.Label(self.select_task_frame, text = "Select Task", font = ("Arial", 16)).pack()

      def display_task_list_frame(self, taskList):
            if (not self.select_task_frame):
                  self.create_select_tasks_frame()
            self.taskListDisplaying = ttk.Notebook(self.select_task_frame) 
            self.taskListDisplaying.pack(pady=10, expand=False)
            for task in taskList:
                  if (task):
                        self.taskList.append(task)
                        self.display_select_task(400, 400, [2, 2], 'Task ', task.imageSize, task.mappingArr.reshape(-1), 400, 30, task.defineNumber)
            
            frame = tk.Frame(self.select_task_frame, height = 200, width = 600)
            frame.pack(expand = False)
            ttk.Label(frame, text="Task selected:").grid(column=0, row=0, padx=5, pady=5)
            self.taskSelectInput = tk.Text(frame, height = 1, width = 10)
            self.taskSelectInput.grid(column = 1, row = 0)
            ttk.Label(frame, text="Mask X:").grid(column=2, row=0, padx=5, pady=5)
            self.maskXInput = tk.Text(frame, height = 1, width = 10)
            self.maskXInput.grid(column = 3, row = 0)
            ttk.Label(frame, text="Mask Y:").grid(column=4, row=0,padx=5, pady=5)
            self.maskYInput = tk.Text(frame, height = 1, width = 10)
            self.maskYInput.grid(column = 5, row = 0)
            AIButton = tk.Button(self.select_task_frame, text = 'AI choose', command = lambda: [self.AI_choose_the_task()])
            AIButton.pack()
            submitButton = tk.Button(self.select_task_frame, text = 'Submit', command = lambda: [self.send_task_selected(), self.change_frame(self.select_task_frame_name, self.answer_frame_name)])
            submitButton.pack()
      
      def AI_choose_the_task(self):
            self.taskSelectInput.delete('1.0', 'end')
            self.maskXInput.delete('1.0', 'end')
            self.maskYInput.delete('1.0', 'end')
            finalSelectquestionIndex = random.randrange(5)
            xMaskPos = random.randrange(30)
            yMaskPos = random.randrange(30)
            self.taskSelectInput.insert('1.0', str(finalSelectquestionIndex))
            self.maskXInput.insert('1.0', str(xMaskPos))
            self.maskYInput.insert('1.0', str(yMaskPos))

      def send_task_selected(self):
            print ('Task ', int(self.taskSelectInput.get('1.0', 'end')), ' is selected.')
            print (self.taskList[int(self.taskSelectInput.get('1.0', 'end')) - 1])
            print ('Mask is placed in (' , int(self.maskXInput.get('1.0', 'end')), ',', int(self.maskYInput.get('1.0', 'end')), ')')
            seletion = int(self.taskSelectInput.get('1.0', 'end'))
            xMaskPos = int(self.maskXInput.get('1.0', 'end'))
            yMaskPos = int(self.maskYInput.get('1.0', 'end'))
            Task_selected_package = self.Encode(self.PKT_TASK_SELECTED, 20, self.defineUser, self.questNumber, seletion, xMaskPos, yMaskPos) 
            self.client.send(Task_selected_package)

      def display_select_task(self, w, h, offset, title, imageSize, image, valueW, valueH, value):
            canvas = tk.Canvas(self.taskListDisplaying, width = w + offset[0], height = h + offset[1] + valueH)
            canvas.pack(fill='both', expand=False)
            self.taskListDisplaying.add(canvas, text=title)
            for row in range(imageSize):
                  for col in range(imageSize):
                        imageStartPos = (col * int(w / imageSize) + offset[0], row * int(h / imageSize) + offset[1])
                        imageEndPos = ((col + 1) * int(w / imageSize) + offset[0], (row + 1) * int(h / imageSize) + offset[1])
                        canvas.create_rectangle(imageStartPos, imageEndPos, fill = self.color[image[row * imageSize + col]])
                        canvas.create_text((200, 415), text = "Value = " + str(value), font = 'Arial 12')

      def create_answer_frame(self):
            if (not self.answer_frame):
                  print("Create answer frame")
                  self.answer_frame = ttk.Frame(self.playing_frame)
                  self.answer_frame.pack()
            


      def display_question(self, imageSize, image):
            if (not self.answer_frame) :
                  print("Create answer frame")
                  self.answer_frame = ttk.Frame(self.playing_frame)
                  self.answer_frame.pack()
            
            ttk.Label(self.answer_frame, text = "Answer the question", font = ("Arial", 16)).pack()
            
            self.question_canvas = tk.Canvas(self.answer_frame, width = 402, height = 402)
            self.question_canvas.pack(fill='both', expand = False)
            if (self.submit_frame):
                  self.submit_frame.destroy()
            for row in range(imageSize):
                  for col in range(imageSize):
                        imageStartPos = (col * int(400 / imageSize) + 2, row * int(400 / imageSize) + 2)
                        imageEndPos = ((col + 1) * int(400 / imageSize) + 2, (row + 1) * int(400 / imageSize) + 2)
                        self.question_canvas.create_rectangle(imageStartPos, imageEndPos, fill = self.color[image[row * imageSize + col]])
            self.display_answer_submition()

      def display_answer_submition(self):
            self.submit_frame = tk.Frame(self.answer_frame)
            self.submit_frame.pack()
            ttk.Label(self.submit_frame, text="Your answer:").grid(column=1, row=0,padx=5, pady=5)
            self.answer_input = tk.Text(self.submit_frame, height = 1, width = 10)
            self.answer_input.grid(column = 2, row = 0,padx=5, pady=5)
            AIBtn = tk.Button(self.submit_frame, text='AI guess')
            AIBtn['command'] = lambda: [print('AI guessed'), self.ai_guess_the_number()]
            AIBtn.grid(column= 1, row = 1, padx = 5, pady = 5)
            submitBtn = tk.Button(self.submit_frame, text='Submit answer')
            submitBtn['command'] = lambda: [print('Answer submited', int(self.answer_input.get('1.0', 'end'))), self.answer_submit()]
            submitBtn.grid(column= 2, row = 1, padx = 5, pady = 5)
            submitLaterBtn = tk.Button(self.submit_frame, text='Answer later')
            submitLaterBtn['command'] = lambda: [print('Answer later'), self.answer_later()]
            submitLaterBtn.grid(column= 3, row = 1, padx = 5, pady = 5)

      def answer_suggest_questions(self):
            # answer and send package here
            print("Answer the suggest questions")

      def ai_guess_the_number(self):
            # ai guess here
            print("AI, guess the number")
            guessednumber = self.AIGuessing.run(self.curGuessingNumberMap)
            print("guessednumber: ", guessednumber)
            if (int(guessednumber) < 10):
                  self.answer_input.insert('1.0', str(guessednumber))
            else:
                  self.answer_suggest_questions()
      
      def answer_submit(self):
            # submit the answer here
            print("Server, this is my answer for ur question")
            Answer_submit_package = self.Encode(self.PKT_ANSWER_SUBMIT, 12, self.defineUser, self.questNumber, int(self.answer_input.get('1.0', 'end')))
            print(Answer_submit_package)
            self.client.send(Answer_submit_package)
            self.change_frame(self.playing_frame_name, self.playing_frame_name)
      
      def answer_later(self):
            # tell server about the delay of the answer here
            print("Server, I will give you my answer later")



      def change_frame(self, close_frame_name, open_frame_name):
            self.destroy_frame(close_frame_name)
            self.create_frame(open_frame_name)

      def destroy_frame(self, frame_name):
            if (frame_name == self.login_frame_name):
                  self.login_frame.destroy()
            elif (frame_name == self.playing_frame_name):
                  self.playing_frame.destroy()
            elif (frame_name == self.select_task_frame_name):
                  self.select_task_frame.destroy()
            elif (frame_name == self.answer_frame_name):
                  self.answer_frame.destroy()

if __name__ == "__main__":
      client = Client2()
      client.run()