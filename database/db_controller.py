import sqlite3
from datetime import datetime

class DatabaseController:
    def __init__(self):
        try:
            self._conn = sqlite3.connect('LibraryApp.db')
            self._cursor = self._conn.cursor()
        except sqlite3.Error as e:
            print(f"Veritabanı bağlantı hatası: {e}")

    def __del__(self):
        """Destructor: Bağlantıyı güvenli bir şekilde kapat"""
        if self._conn:
            self._conn.close()

    # Kitap Arama Metodları
    def search_books(self, title=None, author=None, genre=None):
        try:
            conditions = []
            params = []
            
            if title:
                conditions.append("title LIKE ?")
                params.append(f"%{title}%")
            
            if author:
                conditions.append("authors LIKE ?")
                params.append(f"%{author}%")
                
            if genre:
                conditions.append("genre = ?")
                params.append(genre)

            query = "SELECT * FROM Book"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            self._cursor.execute(query, params)
            return self._cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f"Arama hatası: {e}")
            return []

    def get_recommendations(self, fav_genre):
        try:
            query = """
            SELECT isbn, title 
            FROM Book 
            WHERE genre = ? 
            LIMIT 3
            """
            self._cursor.execute(query, (fav_genre,))
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Öneri getirme hatası: {e}")
            return []

    # Ekleme Metodları
    def add_book(self, isbn, title, authors, description, genre, availability):
        try:
            query = """
            INSERT INTO Book (isbn, title, authors, description, genre, availability)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            self._cursor.execute(query, (isbn, title, authors, description, genre, availability))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Kitap ekleme hatası: {e}")
            self._conn.rollback()
            return False

    def add_comment(self, user_id, book_isbn, comment_text):
        try:
            query = """
            INSERT INTO Comment (user_id, book_isbn, comment_text, comment_date)
            VALUES (?, ?, ?, ?)
            """
            self._cursor.execute(query, (user_id, book_isbn, comment_text, datetime.now()))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Yorum ekleme hatası: {e}")
            self._conn.rollback()
            return False

    def add_notification(self, user_id, message):
        try:
            query = """
            INSERT INTO Notification (user_id, message, notification_date)
            VALUES (?, ?, ?)
            """
            self._cursor.execute(query, (user_id, message, datetime.now()))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Bildirim ekleme hatası: {e}")
            self._conn.rollback()
            return False

    def add_to_reading_list(self, user_id, book_isbn):
        try:
            query = """
            INSERT INTO ReadingList (user_id, book_isbn)
            VALUES (?, ?)
            """
            self._cursor.execute(query, (user_id, book_isbn))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Okuma listesine ekleme hatası: {e}")
            self._conn.rollback()
            return False

    def add_reservation(self, user_id, book_isbn, due_date):
        try:
            query = """
            INSERT INTO Reservation (user_id, book_isbn, reservation_date, due_date, status)
            VALUES (?, ?, ?, ?, 'active')
            """
            self._cursor.execute(query, (user_id, book_isbn, datetime.now(), due_date))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Rezervasyon ekleme hatası: {e}")
            self._conn.rollback()
            return False

    def add_user(self, name, password, favourite_genre):
        try:
            query = """
            INSERT INTO Users (name, password, favourite_genre, fine)
            VALUES (?, ?, ?, 0)
            """
            self._cursor.execute(query, (name, password, favourite_genre))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Kullanıcı ekleme hatası: {e}")
            self._conn.rollback()
            return False

    # Güncelleme Metodları
    def update_fine(self, user_id, amount):
        try:
            query = """
            UPDATE Users 
            SET fine = fine + ? 
            WHERE user_id = ?
            """
            self._cursor.execute(query, (amount, user_id))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ceza güncelleme hatası: {e}")
            self._conn.rollback()
            return False
        
    
    def update_book_availability(self, isbn, availability):
        try:
            query = """
            UPDATE Book 
            SET availability = ? 
            WHERE isbn = ?
            """
            self._cursor.execute(query, (availability, isbn))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Kitap durumu güncelleme hatası: {e}")
            self._conn.rollback()
            return False
        

    def createBookReport(self,isbn):
        try:
            query = """
            SELECT b.Title, b.Authors, b.Description, b.Genre, COUNT(r.ReservationID) COUNT(c.CommentID) as CommentCount 
            FROM Book as b,Reservation as r,Comment as c
            WHERE isbn = ? and
            r.BookISBN = b.ISBN and
            c.BookISBN = b.ISBN
            """
            self._cursor.execute(query, (isbn,))
            return self._cursor.fetchall()
        
        except sqlite3.Error as e:
            print(f"Rapor oluşturma hatası: {e}")
            return []
        
    
    def createUserReport(self,user_id):
        try:
            query = """
            SELECT u.Name, u.FavouriteGenre, COUNT(r.ReservationID) as ReservationCount, COUNT(c.CommentID) as CommentCount
            FROM Users as u,Reservation as r,Comment as c
            WHERE u.UserID = ? and
            r.UserID = u.UserID and
            c.UserID = u.UserID
            """
            self._cursor.execute(query, (user_id))
            return self._cursor.fetchall()
        
        except sqlite3.Error as e:
            print(f"Rapor oluşturma hatası: {e}")
            return []