from mongorm.BaseModel import BaseModel
import datetime

class Tag(BaseModel):    
    def __init__(self):
        self.name = None
        self.slug = None
        self.added = datetime.datetime.now()

    def _presave(self, entitManager):
        self.slug = self.name.lower().replace(' ','-')



class Item(BaseModel):
    def __init__(self):
        self.title = None
        self.content = None
        self.tagIds = []
        self.added = datetime.datetime.now()


