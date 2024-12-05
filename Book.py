from typing import Any
from database.db_controller import *
import Comment

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
        is_updated=self.controller.update_book_availability(self._ısbn,availability),
        if is_updated:
            self._availability=availability

    def getAvailability(self):
        return self._availability
    
    def getDescription(self):
        return self._description
    
    def setDescription(self,description):
        #after add db controller,update this method
        is_set=self.controller.update_book_description(self._description,description)
        if is_set:
            self._description=description

    def addComments(self, user_id, comment_text):
        is_added=self.controller.add_comment(user_id,self._ısbn,comment_text)
        if is_added:
            self._comments.append(Comment(user_id,comment_text))
        
    def getComments(self):
        comments = self.controller._cursor.execute(
        "SELECT CommentText FROM Comment WHERE BookISBN = ?", (self._ısbn,)
        ).fetchall()
        self._comments = [c[0] for c in comments]
        return self._comments
    
    def getReservationCount(self):
        self._reservationCount = self.controller._cursor.execute(
        "SELECT COUNT(*) FROM Reservation WHERE BookISBN = ?", (self._ısbn,)
        ).fetchone()[0]
        return self._reservationCount
    
    def setReservationCount(self,user_id):
        self.controller.add_reservation(user_id,self._ısbn,self._dueDate)
    
    def getDueDate(self):
        return self._dueDate
    
    def setDueDate(self,user_id,dueDate):
        ###
        is_set=self.controller.extend_due_date(user_id,self._ısbn,dueDate)
        if is_set:
            self._dueDate=dueDate
    
    def getCurrentBorrower(self):
        result = self.controller._cursor.execute(
        "SELECT UserID FROM Reservation WHERE BookISBN = ? AND Status = 'Active'", (self._ısbn,)
        ).fetchone()
        self._currentBorrowerID = result[0] if result else None
        return self._currentBorrowerID
    
    def setCurrentBorrower(self,user_id):
        ###
        self._currentBorrowerID=user_id
