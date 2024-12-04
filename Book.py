from typing import Any
from database.db_controller import *

class Book:
    # Controller oluşturma
    controller = DatabaseController()
    _title=None
    _ısbn=-1
    _author=None
    _genre=None
    _availability=True
    _description=None
    _comments=[]
    _reservationCount=-1
    _dueDate=None
    _currentBorrowerID=-1

    def __init__(self,title,ısbn,author,genre,availability,description,comments,reservationCount,dueDate,currentBorrowerID) :
        self._title=title
        self._ısbn=ısbn
        self._author=author
        self._genre=genre
        self._availability=availability
        self._description=description
        self._comments=comments
        self._reservationCount=reservationCount
        self._dueDate=dueDate
        self._currentBorrowerID=currentBorrowerID

    def setAvailability(self,availability):
        self.controller.update_book_availability(self._ısbn,availability)

    def getAvailability(self):
        return self._availability
    
    def getDescription(self):
        return self._description
    
    def setDescription(self,description):
        #after add db controller,update this method
        self.controller.update_book_description(self._description,description)

    def addComments(self, user_id, comment_text):
        self.controller.add_comment(user_id,self._ısbn,comment_text)
        
    def getComments(self):
        return self._comments
    
    def getReservationCount(self):
        return self._reservationCount
    
    def setReservationCount(self,user_id):
        self.controller.add_reservation(user_id,self._ısbn,self._dueDate)
    
    def getDueDate(self):
        return self._dueDate
    
    def setDueDate(self,user_id,dueDate):
        ###
        self.controller.extend_due_date(user_id,self._ısbn,dueDate)
    
    def getCurrentBorrower(self):
        return self._currentBorrowerID
    
    def setCurrentBorrower(self,user_id):
        #after add db controller,update this method
        self.controller.update_currentBorrower(self._ısbn,user_id)
