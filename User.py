from datetime import date
from typing import List
#from book import book

class User:

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

    def reserve_book(self, book):
        print(f"Reserving book: {book}")
        # reserve hangi şartlarda yapılacak 1.durum olmayan kitabı ayırtmak(bu durumda availability kontrolü yapılıp false olduğu durumda reservation count 1 arttırılmalı (? birden fazla kişi reserve ederse önce hangisi alıcak/ sadece setreservationCount metodu var nasıl handle edicek bu durumu))
        # 2.durum direk kitabı available ise alsın ve current borrower olarak atansın user.
    
    def view_due_date(self) -> date:
        print("Returning due date for the current book")
        return date.today()
        # burda currentbook parametre olarak alınmalı ve onun duedatei dönülmeli

    def view_past_reservation(self) -> List[str]:
        return self.past_reserved_books
        
    def view_overdue(self) -> List[str]:
        overdueList =[overDueBook for overDueBook in self._past_reserved_books if overDueBook.DueDate < date.today]
        return overdueList
     
    def view_fine(self) -> float:
        return self.fine

    def view_description(self, book) -> str:
        return book.getDescription

    def comment(self, book: str, comment: str):
        self.comments.append(comment)
        book.addComment(comment)

    def view_recommendations(self) -> List[str]:
        print("Returning book recommendations")
        return []

    def make_reading_list(self, book: str):
        print(f"Adding {book} to reading list")
        self.reading_list.append(book)

    def change_password(self, new_password: str):
        print("Changing password")
        self.password = new_password

    def change_user_name(self, new_name: str):
        print("Changing username")
        self.name = new_name

    def set_favourite_genre(self, genre: str):
        self.favourite_genre = genre

    def extend_reservation_duration(self, new_date: date):
        print(f"Extending reservation duration to {new_date}")
        # burda bir currentbook parametre olarak verilip onun duedate'i baştan set edilmesi gerekmiyor mu

    def search_by_genre(self, genre: str) -> List[str]:
        print(f"Searching books by genre: {genre}")
        return []

    def search_by_author(self, author: str) -> List[str]:
        print(f"Searching books by author: {author}")
        return []

    def search_by_title(self, title: str) -> List[str]:
        print(f"Searching books by title: {title}")
        return []

    def get_comments(self) -> List[str]:
        return self.comments

    def add_comment(self, comment: str):
        self.comments.append(comment)
        #yukarıdaki comment ile farkı ne tam olarak 
    
    def getID(self) -> int:  
        return self.user_id 
    
    
