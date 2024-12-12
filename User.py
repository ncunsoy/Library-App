from datetime import date, timedelta
from typing import List
from database.db_controller import *
import Book

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
        self.controller = DatabaseController()


    def reserve_book(self, book_isbn: str):
        """
        Reserve a book or add it to the waitlist if it's not available.
        :param book_isbn: ISBN of the book to reserve.
        :return: Status message indicating the result of the reservation.
        """
        try:
            # Fetch book availability and due date
            query = """
            SELECT Availability, DueDate 
            FROM Book 
            LEFT JOIN Reservation ON Book.ISBN = Reservation.BookISBN 
            WHERE Book.ISBN = ?;
            """

            result = self.controller._cursor.execute(query, (book_isbn,)).fetchone()
            if not result:
                return "Book not found."

            availability, due_date = result

            # Reserve or add to waitlist
            if availability == 1:  # If book is available
                # Update book availability
                update_query = "UPDATE Book SET Availability = 0 WHERE ISBN = ?;"
                self.controller._cursor.execute(update_query, (book_isbn,))
                self.controller._conn.commit()  # Commit the change to the database

                # Add reservation entry
                reservation_query = """
                INSERT INTO Reservation (UserID, BookISBN, ReservationDate, DueDate, Status)
                VALUES (?, ?, ?, ?, ?);
                """
                reservation_date = date.today()
                new_due_date = date.today() + timedelta(days=14)  # Example due date (2 weeks from now)
                self.controller._cursor.execute(reservation_query, (self._user_id, book_isbn, reservation_date, new_due_date, "Active"))
                self.controller._conn.commit()  # Commit the reservation to the database

                return "Book successfully reserved."

            else:  # If book is not available
                # Add to the waitlist
                waitlist_query = """
                INSERT INTO Reservation (UserID, BookISBN, ReservationDate, DueDate, Status)
                VALUES (?, ?, ?, ?, ?);
                """
                reservation_date = date.today()
                self.controller._cursor.execute(waitlist_query, (self._user_id, book_isbn, reservation_date, due_date, "Waitlisted"))
                self.controller._conn.commit()  # Commit the waitlist entry to the database

                return "Book is not available. Added to the waitlist."

        except Exception as e:
            print(f"Error reserving book: {e}")
            return "An error occurred while reserving the book."


        except Exception as e:
            self.controller._conn.rollback()  # Ensure rollback on failure
            print(f"Error reserving book: {e}")
            return "An error occurred while reserving the book."





    
    def view_due_date(self,book) -> date:
        print("Returning due date for the current book")
        # return date.today()
        # burda currentbook parametre olarak alınmalı ve onun duedatei dönülmeli
        reservation = self.controller.view_dueDate(self._user_id)
        for res in reservation:
            if res[0] == book.getTitle():
                return res[1]  # Kitap başlığını kontrol edip teslim tarihini döndürür.
        return None


    def view_past_reservation(self) -> List[str]:
        reservations = self.controller.view_reservations(self._user_id)
        self.past_reserved_books = [
            f"Kitap: {res[0]}, Rezervasyon Tarihi: {res[1]}, Teslim Tarihi: {res[2]}" 
            for res in reservations if res[3] == "Finished"
        ]
        return self.past_reserved_books
        
    def view_overdue(self) -> List[str]:
        overdueList =[overDueBook for overDueBook in self._past_reserved_books if overDueBook.DueDate < date.today]
        return overdueList
     
    def view_fine(self) -> float:
        return self.fine

    def view_description(self, book) -> str:
        return book.getDescription

    def comment(self, book: str, comment: str):
        self._comments.append(comment)
        book.addComment(comment)
        self.controller.add_comment(self._user_id, book.getISBN(), comment)

    def view_recommendations(self) -> List[str]:
        # print("Returning book recommendations")
        # return []
        recommendations = self.controller.get_recommendations(self._favourite_genre)
        return [f"{rec[1]} (ISBN: {rec[0]})" for rec in recommendations]

    def make_reading_list(self, book: str):
        print(f"Adding {book} to reading list")
        self.reading_list.append(book)
        self.controller.add_to_reading_list(self._user_id, book.getISBN())

    def change_password(self, new_password: str):
        print("Changing password")
        self.password = new_password
        self.controller.change_password("Users", self._user_id, new_password)
        self._password = new_password

    def change_user_name(self, new_name: str):
        print("Changing username")
        self.name = new_name
        self.controller.change_name("Users", self._user_id, new_name)
        self._name = new_name

    def set_favourite_genre(self, genre: str):
        self.favourite_genre = genre
        self.controller.set_favorite_genre(self._user_id, genre)
        self._favourite_genre = genre

    def extend_reservation_duration(self,book,new_date: date):
        print(f"Extending reservation duration to {new_date}")
        # burda bir currentbook parametre olarak verilip onun duedate'i baştan set edilmesi gerekmiyor mu
        self.controller.extend_due_date(self._user_id, book.getISBN(), new_date)

    def search_by_genre(self, genre: str) -> List[str]:
        # print(f"Searching books by genre: {genre}")
        # return []
        books = self.controller.search_books(genre=genre)
        return [book for book in books]

    def search_by_author(self, author: str) -> List[str]:
        # print(f"Searching books by author: {author}")
        # return []
        books = self.controller.search_books(author=author)
        return [book for book in books]
    

    def search_by_title(self, title: str) -> List[str]:
        # print(f"Searching books by title: {title}")
        # return []
        books = self.controller.search_books(title=title)
        return [book for book in books]
    
    def get_comments(self) -> List[str]:
        self._comments = self.controller._cursor.execute(
            "SELECT CommentText FROM Comment WHERE UserID = ?", (self._user_id,)
        ).fetchall()
        #self.controller._conn.commit()
        return self._comments

    def add_comment(self, book_isbn: str, comment: str):
        # Fetch the book object from the database using the ISBN  
        self._comments.append(comment)
        self.controller.add_comment(self._user_id,book_isbn, comment)
        self.controller._conn.commit()
        return "Comment Added"

    
    def getID(self) -> int:  
        return self.user_id 
    
    
