class InfoRetriever:
    def __init__(self): 
        self.value = None
        self.next = None
    
    def set_next(self, next):
        self.next = next
        return next

    def get_info(self, data):
        next_data = self.retrieve(data)
        if self.next == None:
            return self.value 
        return self.value + self.next.get_info(next_data)
    
    def retrieve(self, data): 
        return []


        
        