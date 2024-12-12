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
import unittest
from unittest.mock import MagicMock
from datetime import datetime as dt
from Book import Book
from database.db_controller import DatabaseController
from Comment import Comment  # Corrected import

class TestBook(unittest.TestCase):

    def setUp(self):
        # Mocking DatabaseController
        self.db_mock = MagicMock(spec=DatabaseController)
        
        # Create a Book instance with the mocked DatabaseController
        self.book = Book(
            title="Test Book",
            ısbn="123456789",
            author="Author Name",
            genre="Fiction",
            availability=True,
            description="A test book description",
            comments=[],
            reservationCount=0,
            dueDate=None,
            currentBorrowerID=None
        )
        
        # Mock methods for controller interaction
        self.book.controller = self.db_mock  # Inject the mock controller into the book

    def test_set_availability(self):
        # Test for setAvailability method
        self.db_mock.update_book_availability.return_value = True
        
        # Change availability
        self.book.setAvailability(False)
        
        # Assert the update method was called
        self.db_mock.update_book_availability.assert_called_with("123456789", False)
        self.assertEqual(self.book.getAvailability(), False)

    def test_set_description(self):
        # Test for setDescription method
        self.db_mock.update_book_description.return_value = True
        
        # Change description
        self.book.setDescription("Updated description")
        
        # Assert the update method was called
        self.db_mock.update_book_description.assert_called_with("A test book description", "Updated description")
        self.assertEqual(self.book.getDescription(), "Updated description")

    

    def test_get_comments(self):
        # Mock for retrieving comments from the database
        cursor_mock = MagicMock()
        self.db_mock._cursor = cursor_mock
        cursor_mock.execute.return_value.fetchall.return_value = [("Great book!",), ("Interesting read",)]
        
        # Get comments
        comments = self.book.getComments()
        
        # Assert that the comments list is populated correctly
        self.assertEqual(comments, ["Great book!", "Interesting read"])

    def test_get_reservation_count(self):
        # Mock for fetching reservation count
        cursor_mock = MagicMock()
        self.db_mock._cursor = cursor_mock
        cursor_mock.execute.return_value.fetchone.return_value = (5,)
        
        # Get reservation count
        count = self.book.getReservationCount()
        
        # Assert the correct count is fetched
        self.assertEqual(count, 5)

    def test_set_due_date(self):
        # Mock for extending the due date
        self.db_mock.extend_due_date.return_value = True
        
        # Set a new due date
        self.book.setDueDate("user123", dt(2024, 12, 31))
        
        # Assert the extend_due_date method was called
        self.db_mock.extend_due_date.assert_called_with("user123", "123456789", dt(2024, 12, 31))
        self.assertEqual(self.book.getDueDate(), dt(2024, 12, 31))

    def test_get_current_borrower(self):
        # Mock for fetching current borrower
        cursor_mock = MagicMock()
        self.db_mock._cursor = cursor_mock
        cursor_mock.execute.return_value.fetchone.return_value = ("user123",)
        
        # Get current borrower
        borrower = self.book.getCurrentBorrower()
        
        # Assert the correct borrower is fetched
        self.assertEqual(borrower, "user123")

    def test_set_current_borrower(self):
        # Set current borrower and verify it
        self.book.setCurrentBorrower("user123")
        self.assertEqual(self.book._currentBorrowerID, "user123")

if __name__ == '__main__':
    unittest.main()
