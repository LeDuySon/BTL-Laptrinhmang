class ClientPlayer():
    def __init__(self,
                 player_number,
                 player_id,
                 conn, 
                 address):
        self.player_order = player_number
        self.player_id = player_id
        self.conn = conn
        self.address = address
    
        self.number_block_opened = 0
        self.current_score = 0 
        
        self.player_record = {}
        
    def set_record(self, info):
        self.player_record[info["questNumber"]] = info
        
    
    