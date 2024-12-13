from database.db_controller import DatabaseController
import datetime as dt
import Book

overdue_fine=5

class StaffMember:
    #constructor
    def __init__(self, name, password, staffID, db_name='LibraryApp.db'):
        self._name = name
        self._password = password
        self._staffID = staffID
        self.db = DatabaseController(db_name)

    #Staff Member methods
    def searchByGenre(self, genre):
        return self.db.search_books(genre=genre)

    def searchByAuthor(self, author):
        return self.db.search_books(author=author)
            
    def searchByTitle(self, title):
        return self.db.search_books(title=title)
            
    def addBook(self, isbn, title, authors, description, genre, availability):
        return self.db.add_book(isbn, title, authors, description, genre, availability)

    def removeBook(self, isbn):
        return self.db.remove_book(isbn)

    def updateBookAvailability(self, isbn, availability):
        if availability=="Finished":
            # Kitabın geç teslim edilip edilmediğini kontrol ederek ona göre ceza uygular 
            #book= Book(isbn)
            current_userID=self.db.get_current_borrower(isbn)
            due_date=self.db.view_dueDate(current_userID,isbn)[1]
            lateness=(dt.today()-due_date).days
            if lateness>0:
                self.chargeForOverdueBook(current_userID,overdue_fine*lateness)

             # Kullanıcılara bildirim gönderir
            users=self.db.get_users_with_reserved_book(isbn)    
            for user in users:
                self.sendNotification(user, "Rezerve ettiğiniz kitap artık mevcut.")
        return self.db.update_book_availability(isbn, availability)

    def registerUser(self, name, password, favourite_genre):
        return self.db.add_user(name, password, favourite_genre)

    def removeUser(self, user_id):
        return self.db.delete_user(user_id)

    def createBookReport(self, isbn):
        return self.db.createBookReport(isbn)

    def createUserReport(self, user_id):
        return self.db.createUserReport(user_id)

    def chargeForOverdueBook(self, user_id, charge_amount):
        return self.db.update_fine(user_id, charge_amount)

    def removeOverdueBook(self, user):
        if user in self.users:
            user.overdueBooks = []

    def sendNotification(self, user_id, message):
        return self.db.add_notification(user_id, message)


    #gets and sets
    def getName(self):
        return self._name
    
    def setName(self, x):
        self._name = x

        
    def getPassword(self):
        return self._password
    
    def setPassword(self, x):
        self._password = x
        
    def getStaffID(self):
        return self._staffID
    
    def setStaffID(self, x):
        self._staffID = x

import unittest

from datetime import datetime as dt
from unittest.mock import patch, MagicMock
from database.db_controller import DatabaseController
from Book import Book

class TestStaffMember(unittest.TestCase):
    
    def setUp(self):
        self.db_mock = MagicMock(spec=DatabaseController)
        self.staff = StaffMember(name="John Doe", password="password123", staffID="S123", db_name="LibraryApp.db")
        self.staff.db = self.db_mock
        
        # Mocking the methods used in updateBookAvailability
        self.db_mock.get_current_borrower = MagicMock(return_value="user123")
        self.db_mock.view_dueDate = MagicMock(return_value=("user123", dt(2023, 12, 1)))
        self.db_mock.update_fine = MagicMock(return_value=True)
        self.db_mock.add_notification = MagicMock(return_value=True)
            
    def test_search_by_genre(self):
        self.db_mock.search_books.return_value = ["Book 1", "Book 2"]
        result = self.staff.searchByGenre("Fiction")
        self.db_mock.search_books.assert_called_with(genre="Fiction")
        self.assertEqual(result, ["Book 1", "Book 2"])

    def test_add_book(self):
        self.db_mock.add_book.return_value = True
        result = self.staff.addBook("12345", "New Book", "Author Name", "Description", "Genre", "Available")
        self.db_mock.add_book.assert_called_with("12345", "New Book", "Author Name", "Description", "Genre", "Available")
        self.assertTrue(result)

    def test_remove_book(self):
        self.db_mock.remove_book.return_value = True
        result = self.staff.removeBook("12345")
        self.db_mock.remove_book.assert_called_with("12345")
        self.assertTrue(result)
        
    @patch('Book.Book')  # 'Book' sınıfını doğru şekilde patch ediyoruz
    @patch('StaffMember.dt')  # Tarihi patch'liyoruz
    def test_update_book_availability(self, mock_dt, MockBook):
        # Mock edilen tarih
        mock_dt.today.return_value = dt(2023, 12, 10)
        
        # Mock edilen Book nesnesi
        mock_book_instance = MagicMock(spec=Book)
        MockBook.return_value = mock_book_instance

        # Mock nesneleri
        self.db_mock.get_current_borrower.return_value = "user123"
        self.db_mock.view_dueDate.return_value = ("user123", dt(2023, 12, 1))
        self.db_mock.get_users_with_reserved_book.return_value = ["user123"]

        # Ceza hesaplamasını doğrulama
        lateness = (dt.today() - dt(2023, 12, 1)).days  # 9 gün
        expected_fine = overdue_fine * lateness  
        
        # Test edilen method
        self.staff.updateBookAvailability("12345", "Finished")

        # Beklenen çağrıları kontrol etme
        self.db_mock.update_fine.assert_called_with("user123", expected_fine)  # 45 olmalı
        self.db_mock.add_notification.assert_called_with("user123", "Rezerve ettiğiniz kitap artık mevcut.")
        self.db_mock.update_book_availability.assert_called_with("12345", "Finished")
            
    def test_register_user(self):
        self.db_mock.add_user.return_value = True
        result = self.staff.registerUser("Jane Doe", "password456", "Fantasy")
        self.db_mock.add_user.assert_called_with("Jane Doe", "password456", "Fantasy")
        self.assertTrue(result)

    def test_remove_user(self):
        self.db_mock.delete_user.return_value = True
        result = self.staff.removeUser("user123")
        self.db_mock.delete_user.assert_called_with("user123")
        self.assertTrue(result)

    def test_send_notification(self):
        self.db_mock.add_notification.return_value = True
        
        result = self.staff.sendNotification("user123", "Book available for pickup")
        
        self.db_mock.add_notification.assert_called_with("user123", "Book available for pickup")
        self.assertTrue(result)

    def test_charge_for_overdue_book(self):
        self.db_mock.update_fine.return_value = True
        result = self.staff.chargeForOverdueBook("user123", 10)
        self.db_mock.update_fine.assert_called_with("user123", 10)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()

    

        

        
        
