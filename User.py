from datetime import date
from typing import List
from database.db_controller import DatabaseController
from Book import *
class User:
    dbCont = DatabaseController()
    _name= None
    _user_id = 0
    _password = None
    _favourite_genre = None
    _reading_list = None
    _past_reserved_books = None
    _current_notification = None
    _fine = 0
    _comments = None
      
    def __init__(self, name: str, user_id: int, password: str, favourite_genre: str, 
                 reading_list: List[str], past_reserved_books: List[str], 
                 current_notification: List[str], fine: float, comments: List[str]):
        self._name = name
        self._user_id = user_id
        self._password = password
        self._favourite_genre = favourite_genre
        self._reading_list = reading_list
        self._past_reserved_books = past_reserved_books
        self._current_notification = current_notification
        self._fine = fine
        self._comments = comments  

    def reserve_book(self, book_isbn,due_date):
        self.dbCont.add_reservation(self._user_id,book_isbn,reservation_date=date.today,due_date)
        #status nasıl olucak tam olarak
    def view_due_date(self) :
        return self.dbCont.view_dueDate(self.user_id)
        #

    def view_past_reservation(self) -> List[str]:
        return self.dbCont.view_reservations(self._user_id)
        #db'de past reservations için status finished olucak yazıyor, ekstra bişey eklememe gerek var mı 
    def view_overdue(self) -> List[str]:
        overdueList =[overDueBook for overDueBook in self.view_due_date if overDueBook < date.today]
        return overdueList
        # bu method tam olarak nasıl olmalı 
    def view_fine(self) -> float:
        return self.fine
        #
    def view_description(self, book:Book) -> str:
        return book.getDescription
        # book u import da ettim ama getDescription methodunu göremiyor

    def view_recommendations(self) -> List[str]:
        return self.dbCont.get_recommendations(self._favourite_genre)
        #
    def make_reading_list(self, book_isbn):
        self.dbCont.make_reading_list(self._user_id,book_isbn)
        #self.reading_list.append(book)

    def change_password(self, new_password: str):
        self.dbCont.change_name(type= User,user_id=self._user_id,new_password=new_password)
        #self._password=new_password demeye gerek var mı yoksa method hallediyor mu kendisi databasede
    def change_user_name(self, new_name: str):
        self.dbCont.change_name(type= User,user_id=self._user_id,new_name=new_name)
        #self._name=new_name
    def set_favourite_genre(self, genre: str):
        self.dbCont.set_favorite_genre(self._user_id, genre=genre)
        #self.favourite_genre = genre
        
    def extend_reservation_duration(self, book_isbn, new_date):
        self.dbCont.extend_due_date(self._user_id,book_isbn=book_isbn,new_due_date=new_date)

    def search_by_genre(self, genre: str) -> List[str]:
        return self.dbCont.search_books(genre=genre)
        #
    def search_by_author(self, author: str) -> List[str]:
        return self.dbCont.search_books(author=author)
        #
    def search_by_title(self, title: str) -> List[str]:
        return self.dbCont.search_books(title=title)
        #
    def get_comments(self) -> List[str]:
        return self._comments

    def add_comment(self, comment: str, book_isbn):
        self.dbCont.add_comment(self._user_id,book_isbn,comment) 
        # book_isbn ekledim parametre olarak
        # userın içindeki comment listine de bu comment i  eklemem gerekiyor mu
    def getID(self) -> int:  
        return self.user_id 
        #
    
#parametre olarak book_isbn aldım genel olarak çünkü get isbn methodu olmadığı için görmüyor