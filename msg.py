class PackageDef:
    # for decoder (client send)
    PKT_HELLO = 0
    PKT_TASK_SELECTED = 4
    PKT_SUGGEST_ANSWERS = 7
    PKT_ANSWER_SUBMIT = 9
    
    # for encoder (server send)
    PKT_ACCEPT_CONNECT = 1
    PKT_START = 2
    PKT_SELECT_TASK = 3
    PKT_TASK_REQUEST = 5
    PKT_SUGGEST_QUESTIONS = 6
    PKT_SUGGEST_RESULTS = 8
    PKT_ANSWER_CHECKED = 10
    PKT_ROUND_RESULT = 11
    PKT_END_GAME = 12

class Decoder():
    def __init__(self, byteorder="little"):
        self.byteorder = byteorder
    
    def decode(self, data):
        pkt_type = int.from_bytes(data[0:4], byteorder=self.byteorder)
        data_length = int.from_bytes(data[4:8], byteorder=self.byteorder)
        recv_data = data[8:8 + data_length]
        
        if(pkt_type == PackageDef.PKT_TASK_SELECTED):
            decoded_data = {
                "def": int.from_bytes(recv_data[0:4], byteorder=self.byteorder),
                "questNumber": int.from_bytes(recv_data[4:8], byteorder=self.byteorder),
                "taskSelected": int.from_bytes(recv_data[8:12], byteorder=self.byteorder),
                "maskTop": int.from_bytes(recv_data[12:16], byteorder=self.byteorder),
                "maskLeft": int.from_bytes(recv_data[16:20], byteorder=self.byteorder),
            } 
        elif(pkt_type == PackageDef.PKT_SUGGEST_ANSWERS):
            decoded_data = {
                "def": int.from_bytes(recv_data[0:4], byteorder=self.byteorder),
                "questNumber": int.from_bytes(recv_data[4:8], byteorder=self.byteorder),
                "index": int.from_bytes(recv_data[8:12], byteorder=self.byteorder),
                "numberQuestions": int.from_bytes(recv_data[12:16], byteorder=self.byteorder),
                "answer": []
            }
            for idx in range(decoded_data["numberQuestions"]):
                decoded_data["answer"].append(int.from_bytes(recv_data[(idx*4+16):(idx*4+20)], byteorder=self.byteorder))
            
        elif(pkt_type == PackageDef.PKT_ANSWER_SUBMIT):
            decoded_data = {
                "def": int.from_bytes(recv_data[0:4], byteorder=self.byteorder),
                "questNumber": int.from_bytes(recv_data[4:8], byteorder=self.byteorder),
                "answer": int.from_bytes(recv_data[4:8], byteorder=self.byteorder)
            }
        else:
            decoded_data = recv_data
        
        return pkt_type, data_length, decoded_data
    
    def decode_pkt_task_selected(self, data):
        pass

class Encoder():
    def __init__(self, byteorder="little"):
        self.byteorder = byteorder
        
    def get_package_length(self, data, package_type):
        length = 0
        for k, item in data.items():
            if(isinstance(item, str)):
                length += len(item.encode())
                
            elif(isinstance(item, int)):
                length += 4
                
            elif(isinstance(item, list)):
                if(isinstance(item[0], dict)): # handle PKT_SELECT_TASK
                    if(package_type == PackageDef.PKT_SELECT_TASK):
                        length += len(item) * (8 + item[0]["image"].shape[0])
                        
                    elif(package_type == PackageDef.PKT_TASK_REQUEST):
                        length += len(item) * (4 + item[0]["image"].shape[0])
                        
                    elif(package_type == PackageDef.PKT_SUGGEST_QUESTIONS):
                        length += len(item) * 8
                        for i in item:
                            length += 8 * i["num_ones"]
    
                else:
                    length += 4 * len(item)
                
        return length
    
    def encode(self, package_type, data):
        encoded_data = bytearray()
        # package type
        encoded_data.extend(package_type.to_bytes(4, byteorder = self.byteorder))
        
        # length
        package_length = self.get_package_length(data, package_type)
        encoded_data.extend(package_length.to_bytes(4, byteorder = self.byteorder))
        
        # data
        for k, item in data.items():
            print(f"Encode data {k}")
            if(isinstance(item, str)):
                encoded_data.extend(item.encode())
            elif(isinstance(item, int)):
                encoded_data.extend(item.to_bytes(4, byteorder = self.byteorder))
            elif(isinstance(item, list)):
                for i in item:
                    if(isinstance(i, dict)): # handle PKT_SELECT_TASK
                        if(package_type == PackageDef.PKT_SELECT_TASK):
                            label = int(i["label"])
                            image = i["image"] 
                            size = i["size"]
                            
                            encoded_data.extend(label.to_bytes(4, byteorder = self.byteorder))
                            encoded_data.extend(size.to_bytes(4, byteorder = self.byteorder))
                            
                            for pix in image:
                                encoded_data.extend(int(pix).to_bytes(1, byteorder = self.byteorder))
                                
                        elif(package_type == PackageDef.PKT_TASK_REQUEST):
                            image = i["image"]
                            size = i["size"]
                            
                            encoded_data.extend(size.to_bytes(4, byteorder = self.byteorder))
                            
                            for pix in image:
                                encoded_data.extend(int(pix).to_bytes(1, byteorder = self.byteorder))
                                
                        elif(package_type == PackageDef.PKT_SUGGEST_QUESTIONS):
                            size = i["size"]
                            pos = i["pos"]
                            num_ones = i["num_ones"] # count number of num 1
                            
                            encoded_data.extend(size.to_bytes(4, byteorder = self.byteorder))
                            encoded_data.extend(num_ones.to_bytes(4, byteorder = self.byteorder))
                            
                            for point in pos:
                                encoded_data.extend(point.y.to_bytes(4, byteorder = self.byteorder))
                                encoded_data.extend(point.x.to_bytes(4, byteorder = self.byteorder))
                        
                    else:
                        encoded_data.extend(i.to_bytes(4, byteorder = self.byteorder))
        
        print(f"Package type: {package_type} - Length: {package_length}")
        return encoded_data        
        
class MessageHandler():
    def __init__(self):
        self.encoder = Encoder()
        self.decoder = Decoder()
        
    def encode(self, package_type, data):
        encoded_data = self.encoder.encode(package_type, data)
        return encoded_data
    
    def decode(self, data):
        decoded_data = self.decoder.decode(data)
        return decoded_data
