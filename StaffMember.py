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
            book= Book(isbn)
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



    

        

        
        