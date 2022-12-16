import socket
import struct
import random


# create connect
host = "127.0.0.1"
port = 6969
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((host,port))
print("connect successfully")

# define package type name
PKT_HELLO = 0
PKT_ACCEPT_CONNECT = 1
PKT_START = 2
PKT_SELECT_TASK = 3
PKT_TASK_SELECTED = 4
PKT_TASK_REQUEST = 5
PKT_SUGGEST_QUESTIONS = 6
PKT_SUGGEST_ANSWERS = 7
PKT_SUGGEST_RESULTS = 8
PKT_ANSWER_SUBMIT = 9
PKT_ANSWER_CHECKED = 10
PKT_ROUND_RESULTS = 11
PKT_END_GAME = 12

# define user identity
defineUser = 19020046

# define a number with mapping array
class QuestionNumber:
      defineNumber = 0 # the number
      imageSize = 0 # size of mapping number by array
      mappingArr = None # mapping number by array 

class Location:
      row = 0
      col = 0
ListQuestionNumber = []
curGuessingNumberMap = None
numBlockleft = None
curSuggestQuestion = 0

def SolveSuggestQuestion(row, col, numberBlock, ListLocation):
      return random.randrange(0,50)

# encode to send data
# items contains int and string only
def Encode(*items):
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

# decode data receive
# type and len is integer, data still remain bytearray
def Decode(item):
      type = int.from_bytes(item[0 : 4], byteorder = 'little')
      len = int.from_bytes(item[4 : 8], byteorder = 'little')
      data = datarecv[8 : 8 + len]
      return type, len, data

# send Hello
Hello_package = Encode(PKT_HELLO, 4, defineUser)
print(Hello_package)
client.send(Hello_package)
print("hello package send successfully")
datarecv = client.recv(1024)

# start the loop
while(datarecv):
      # decode datarecv
      type, len, data = Decode(datarecv);
      print(type," ",len," ",data)

      # server allow to connect
      if(type == PKT_ACCEPT_CONNECT): #status of people joining
            print(data)

      # send verify package
      if(type == PKT_START):
            print(data)

      # list questions from server
      if(type == PKT_SELECT_TASK):
            #data[0 : 4] is defineUser
            questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
            numberTask = int.from_bytes(data[8 : 12], byteorder = 'little')

            #get list questions
            oldIndex = 12
            for task in range(numberTask):
                  curQuestion = QuestionNumber()

                  #get defineNumber
                  defineNumber = int.from_bytes(data[oldIndex + 0 : oldIndex + 4], byteorder = 'little')
                  curQuestion.defineNumber = defineNumber

                  #get imageSize
                  imageSize = int.from_bytes(data[oldIndex + 4 : oldIndex + 8], byteorder = 'little')
                  curQuestion.imageSize = imageSize

                  oldIndex = oldIndex + 8
                  #get mappingArr
                  mappingArr = [[0] * imageSize] * imageSize
                  for i in range(imageSize):
                        for j in range(imageSize):
                              mappingArr[i][j] = int.from_bytes(data[oldIndex + 0: oldIndex + 1], byteorder = 'little')
                              oldIndex = oldIndex + 1
                  curQuestion.mappingArr = mappingArr

                  #add curquestion to list question
                  ListQuestionNumber.append(curQuestion)

            #select question index then send to server
            finalSelectquestionIndex = random.randrange(numberTask)
            Task_selected_package = Encode(PKT_TASK_SELECTED, 20, defineUser, questNumber, finalSelectquestionIndex, 0, 0) #assume that blank cover is from (1,1) to (10,10)
            client.send(Task_selected_package)

      #receive question from server
      if(type == PKT_TASK_REQUEST):
            # get data from task
            #data[0 : 4] is defineUser
            questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
            time = int.from_bytes(data[8 : 12], byteorder = 'little')

            taskImagesize = int.from_bytes(data[12 : 16], byteorder = 'little')

            curGuessingNumberMap = [[0] * taskImagesize] * taskImagesize
            oldIndex = 16
            for i in range(taskImagesize):
                  for j in range(taskImagesize):
                        curGuessingNumberMap[i][j] = int.from_bytes(data[oldIndex + 0: oldIndex + 1], byteorder = 'little')
                        oldIndex = oldIndex + 1
            curSuggestQuestion = 0
      # receive suggestion questions
      if(type == PKT_SUGGEST_QUESTIONS):
            #data[0 : 4] is defineUser
            questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
            index = int.from_bytes(data[8 : 12], byteorder = 'little')
            numberQuestions = int.from_bytes(data[12 : 16], byteorder = 'little')
            oldIndex = 16
            AnswerArray = []
            for i in range(numberQuestions):
                  row = int.from_bytes(data[oldIndex + 0 : oldIndex + 4], byteorder = 'little')
                  col = int.from_bytes(data[oldIndex + 4 : oldIndex + 8], byteorder = 'little')
                  numberBlock = int.from_bytes(data[oldIndex + 8 : oldIndex + 12], byteorder = 'little')
                  oldIndex = oldIndex + 12
                  ListLocation = []
                  for j in range(numberBlock):
                        Numberrow = int.from_bytes(data[oldIndex + 0 : oldIndex + 4], byteorder = 'little')
                        Numbercol = int.from_bytes(data[oldIndex + 4 : oldIndex + 8], byteorder = 'little')
                        oldIndex = oldIndex + 8
                        Location.row = Numberrow
                        Location.col = Numbercol
                        ListLocation.append(Location)
                  AnswerArray.append(SolveSuggestQuestion(row, col, numberBlock, ListLocation))
            Suggest_answers_package = Encode(PKT_SUGGEST_ANSWERS, 16 + numberQuestions * 4, defineUser, questNumber, index, numberQuestions, AnswerArray)
            client.send(Suggest_answers_package)

      #receive results
      if(type == PKT_SUGGEST_RESULTS):
            #data[0 : 4] is defineUser
            questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
            index = int.from_bytes(data[8 : 12], byteorder = 'little')
            numberQuestions = int.from_bytes(data[12 : 16], byteorder = 'little')
            oldIndex = 16
            # for i in range(numberQuestions):
            #       suggestionValue = int.from_bytes(data[oldIndex + 0 : oldIndex + 1], byteorder = 'little')
            #       oldIndex = oldIndex + 1
            Answer_submit_package = Encode(PKT_ANSWER_SUBMIT, 12, defineUser, questNumber, 1) #assume that all answers is 1
            client.send(Answer_submit_package)

      #confirm the answers from server
      if(type == PKT_ANSWER_CHECKED):
            #data[0 : 4] is defineUser
            questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
            result = int.from_bytes(data[8 : 12], byteorder = 'little')
            clientAnswer = int.from_bytes(data[12 : 16], byteorder = 'little')
            serverAnswer = int.from_bytes(data[16 : 20], byteorder = 'little')
            numBlockOpened = int.from_bytes(data[20 : 24], byteorder = 'little')

      #server sent result
      if(type == PKT_ROUND_RESULTS):
            #data[0 : 4] is defineUser
            questNumber = int.from_bytes(data[4 : 8], byteorder = 'little')
            code = int.from_bytes(data[8 : 12], byteorder = 'little')
            winner = int.from_bytes(data[12 : 16], byteorder = 'little')
            playerPoint = int.from_bytes(data[16 : 20], byteorder = 'little')
            playerResult = int.from_bytes(data[20 : 24], byteorder = 'little')
            playerRevealed = int.from_bytes(data[24 : 28], byteorder = 'little')
            errorLen = int.from_bytes(data[28 : 32], byteorder = 'little')
            error = data[32: 32 + errorLen];

      #end game
      if(type == PKT_END_GAME):
            #data[0 : 4] is defineUser
            matchWinner = int.from_bytes(data[4 : 8], byteorder = 'little')
            player1Point = int.from_bytes(data[8 : 12], byteorder = 'little')
            player2Point = int.from_bytes(data[12 : 16], byteorder = 'little')
      # get package from server
      datarecv = client.recv(4096)

