import sqlite3
from datetime import datetime as dt

class DatabaseController:
    def __init__(self, db_name='LibraryApp.db'):
        try:
            self._conn = sqlite3.connect('LibraryApp.db')
            self._cursor = self._conn.cursor()
            self._db_name = db_name
        except sqlite3.Error as e:
            print(f"Veritabanı bağlantı hatası: {e}")

    def __del__(self):
        """Destructor: Bağlantıyı güvenli bir şekilde kapat"""
        if self._conn:
            self._conn.close()

    # For both user and staff member classes
    # SearchBook
    def search_books(self, title=None, author=None, genre=None):
        try:
            conditions = []
            params = []
            
            if title:
                conditions.append("Title LIKE ?")
                params.append(f"%{title}%")
            
            if author:
                conditions.append("Authors LIKE ?")
                params.append(f"%{author}%")
                
            if genre:
                conditions.append("Genre = ?")
                params.append(genre)

            query = "SELECT * FROM Book"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            self._cursor.execute(query, params)
            return self._cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f"Arama hatası: {e}")
            return []
    

    # type kısmına user ise Users, staff ise Staff yazılmalı
    def change_name(self, type,user_id, new_name):
        try:
            query = """
            UPDATE ?
            SET Name = ?
            WHERE UserID = ?
            """
            self._cursor.execute(query, (type,new_name, user_id))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Şifre değiştirme hatası: {e}")
            self._conn.rollback()
            return False
        
        
    # type kısmına user ise Users, staff ise Staff yazılmalı
    def change_password(self, type,user_id, new_password):
        try:
            query = """
            UPDATE ?
            SET Password = ?
            WHERE UserID = ?
            """
            self._cursor.execute(query, (type,new_password, user_id))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Şifre değiştirme hatası: {e}")
            self._conn.rollback()
            return False

    


    # This part for user class


    # GetReccomendations for a user
    # Get the top 3 most reserved books in the user's favourite genre
    def get_recommendations(self, fav_genre):
        try:
            query = """
            SELECT b.ISBN, b.Title, COUNT(*) as ReservationCount
            FROM Book b
            LEFT JOIN Reservation r ON b.ISBN = r.BookISBN
            WHERE b.Genre = ?
            GROUP BY b.ISBN, b.Title
            ORDER BY ReservationCount DESC
            LIMIT 3
            """
            self._cursor.execute(query, (fav_genre,))
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Öneri getirme hatası: {e}")
            return []
        
    # addComment method for user class
    def add_comment(self, user_id, book_isbn, comment_text):
        try:
            query = """
            INSERT INTO Comment (UserID,BookISBN,CommentText,CommentDate)
            VALUES (?, ?, ?, ?)
            """
            self._cursor.execute(query, (user_id, book_isbn, comment_text, dt.now().strftime("%Y-%m-%d")))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Yorum ekleme hatası: {e}")
            self._conn.rollback()
            return False
        

    # addReadingList method for user class
    def add_to_reading_list(self, user_id, book_isbn):
        try:
            query = """
            INSERT INTO ReadingList (UserID,BookISBN)
            VALUES (?, ?)
            """
            self._cursor.execute(query, (user_id, book_isbn))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Okuma listesine ekleme hatası: {e}")
            self._conn.rollback()
            return False
        

    # addReservation method 
    # It is used in reserveBook method in user class
    def add_reservation(self, user_id, book_isbn, reservation_date,due_date,status):
        try:
            query = """
            INSERT INTO Reservation (UserID,BookISBN,ReservationDate,DueDate,Status)
            VALUES (?, ?, ?, ?, ?)
            """
            self._cursor.execute(query, (user_id, book_isbn,reservation_date , due_date,status))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Rezervasyon ekleme hatası: {e}")
            self._conn.rollback()
            return False
        
    # view_dueDate method
    def view_dueDate(self, user_id):
        try:
            query = """
            SELECT b.Title,r.DueDate
            FROM Reservation r, Book b, Users u
            WHERE r.UserID = ?
            AND r.BookISBN = b.ISBN
            AND r.UserID = u.UserID
            """
            self._cursor.execute(query, (user_id,))
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Teslim tarihi görüntüleme hatası: {e}")
            return []
        
    # view_user_reservations method
    # Kullanıcı tüm rezervasyonlarını görecek. past_reservations için status = "Finished" olacak. Overdue olanlar için ise DueDate'i geçmiş olanlar olacak
    def view_reservations(self, user_id):
        try:
            query = """
            SELECT b.Title, r.ReservationDate, r.DueDate, r.Status
            FROM Reservation r, Book b, Users u
            WHERE r.UserID = ?
            AND r.BookISBN = b.ISBN
            AND r.UserID = u.UserID
            """
            self._cursor.execute(query, (user_id,))
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Geçmiş rezervasyonları görüntüleme hatası: {e}")
            return []
        
        
    
    def make_reading_list(self, user_id,book_isbn):
        try:
            query = """
            INSERT INTO ReadingList (UserID,BookISBN)
            VALUES (?, ?)
            """
            self._cursor.execute(query, (user_id, book_isbn))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Okuma listesi oluşturma hatası: {e}")
            self._conn.rollback()
            return False
        

    def set_favorite_genre(self, user_id, genre):
        try:
            query = """
            UPDATE Users
            SET FavouriteGenre = ?
            WHERE UserID = ?
            """
            self._cursor.execute(query, (genre, user_id))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Beğenilen türü ayarlama hatası: {e}")
            self._conn.rollback()
            return False
        
    
    def extend_due_date(self, user_id, book_isbn, new_due_date):
        try:
            query = """
            UPDATE Reservation
            SET DueDate = ?
            WHERE UserID = ? AND BookISBN = ?
            """
            self._cursor.execute(query, (new_due_date, user_id, book_isbn))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Teslim tarihini uzatma hatası: {e}")
            self._conn.rollback()
            return False










    # This part for staff member class

    # AddBook method for staff member class
    def add_book(self, isbn, title, authors, description, genre, availability):
        try:
            query = """
            INSERT INTO Book (ISBN,Title,Authors,Description,Genre,Availability)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            self._cursor.execute(query, (isbn, title, authors, description, genre, availability))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Kitap ekleme hatası: {e}")
            self._conn.rollback()
            return False
    
    
    # add_notification method for staff member class
    def add_notification(self, user_id, message):
        try:
            query = """
            INSERT INTO Notification (UserID,Message,NotificationDate
)
            VALUES (?, ?, ?)
            """
            self._cursor.execute(query, (user_id, message, dt.now().strftime("%Y-%m-%d")))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Bildirim ekleme hatası: {e}")
            self._conn.rollback()
            return False


    # addUser method for staff member class
    def add_user(self, name, password, favourite_genre):
        try:
            query = """
            INSERT INTO Users (Name,FavouriteGenre,Password,Fine)
            VALUES (?, ?, ?, 0)
            """
            self._cursor.execute(query, (name, password, favourite_genre))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Kullanıcı ekleme hatası: {e}")
            self._conn.rollback()
            return False

    # updateFine method for staff member class
    def update_fine(self, user_id, amount):
        try:
            query = """
            UPDATE Users
            SET Fine = fine + ? 
            WHERE UserID = ?
            """
            self._cursor.execute(query, (amount, user_id))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ceza güncelleme hatası: {e}")
            self._conn.rollback()
            return False
        
    # updateBookAvailability method for staff member class
    # Kullanıcı kitabı teslim ettiğinde staff member kitabın durumunu günceller
    def update_book_availability(self, isbn, availability):
        try:
            query = """
            UPDATE Book 
            SET Availability = ? 
            WHERE ISBN = ?
            """
            self._cursor.execute(query, (availability, isbn))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Kitap durumu güncelleme hatası: {e}")
            self._conn.rollback()
            return False
        
    # createBookReport method for staff member class
    def createBookReport(self, isbn):
        try:
            query = """
            SELECT 
                b.Title, 
                b.Authors, 
                b.Description, 
                b.Genre, 
                (SELECT COUNT(*) FROM Reservation as r WHERE b.ISBN = r.BookISBN) AS ReservationCount,
                (SELECT COUNT(*) FROM Comment as c WHERE c.BookISBN = b.ISBN) AS CommentCount
            FROM Book AS b
            WHERE b.ISBN = ?
            """
            self._cursor.execute(query, (isbn,))
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Rapor oluşturma hatası: {e}")
            return []

        
 
    # createUserReport method for staff member class
    def createUserReport(self,user_id):
        try:
            query = """
            SELECT u.Name, u.FavouriteGenre, 
               (SELECT COUNT(*) FROM Reservation as r WHERE  r.UserID = u.UserID) as ReservationCount,
               (SELECT COUNT(*) FROM Comment as c WHERE c.UserID = u.UserID) as CommentCount
            FROM Users as u
            WHERE u.UserID = ?
            """
            self._cursor.execute(query, (user_id,))
            return self._cursor.fetchall()
        
        except sqlite3.Error as e:
            print(f"Rapor oluşturma hatası: {e}")
            return []
        

class main:
    def test1():
        db = DatabaseController()
        # print(db.search_books(title='Harry Potter'))
        print(db.get_recommendations('Fiction'))
        # print(db.add_book('9781408855652', 'Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', 'The book that started it all.', 'Fantasy', 5))
        # print(db.add_comment(10050, '9781408855652', 'This is a great book!'))
        # print(db.add_notification(10050, 'You have a new notification!'))
        # print(db.add_to_reading_list(10050, '9781408855652'))
        # print(db.add_reservation(10050, '9781408855652', '2021-12-31','2021-12-31',"Active"))
        # print(db.add_user('John Doe', 'password', 'Fantasy'))
        # print(db.update_fine(10050, 5))
        # print(db.update_book_availability('9781408855652', 4))
        # print(db.createBookReport('9781408855652'))
        # print(db.createUserReport(10050))
        # print(dt.now().strftime("%Y-%m-%d"))
        # db._cursor.execute("SELECT COUNT(*) FROM Users WHERE UserID = ?", (10050,))
        # if db._cursor.fetchone()[0] == 0:
        #     print(f"UserID {10050} not found.")
        #     return []



    def test2():
        # Veritabanı kontrolcüsü nesnesi oluştur
        db = DatabaseController()

        # Test 1: Kitap ekleme
        print("Kitap ekleme testi...")
        success = db.add_book(
            isbn="97831614841",
            title="Test Kitabı",
            authors="Yazar Adı",
            description="Bu bir test kitabıdır.",
            genre="Bilim Kurgu",
            availability=True
        )
        print("Kitap ekleme başarılı mı:", success)

        # Test 2: Kullanıcı ekleme
        print("\nKullanıcı ekleme testi...")
        success = db.add_user(
            name="Test Kullanıcı",
            password="12345",
            favourite_genre="Bilim Kurgu"
        )
        print("Kullanıcı ekleme başarılı mı:", success)

        # Test 3: Kitap arama
        print("\nKitap arama testi...")
        books = db.search_books(title="Test")
        print("Bulunan kitaplar:", books)

        # Test 4: Yorum ekleme
        print("\nYorum ekleme testi...")
        if books:
            book_isbn = books[0][0]  # İlk bulunan kitabın ISBN'si
            success = db.add_comment(
                user_id=1,  # Varsayılan bir kullanıcı ID'si
                book_isbn=book_isbn,
                comment_text="Bu bir test yorumudur."
            )
            print("Yorum ekleme başarılı mı:", success)

        # Test 5: Rezervasyon ekleme
        print("\nRezervasyon ekleme testi...")
        success = db.add_reservation(
            user_id=10035,
            book_isbn="97831614841",
            reservation_date="2024-12-05",
            due_date="2024-12-15",
            status="Active"
        )
        print("Rezervasyon ekleme başarılı mı:", success)

        # Test 6: Kullanıcı rezervasyonlarını görüntüleme
        print("\nRezervasyon görüntüleme testi...")
        reservations = db.view_reservations(user_id=10035)
        print("Kullanıcı rezervasyonları:", reservations)

        # Test 7: Kullanıcıya öneri alma
        print("\nÖneri alma testi...")
        recommendations = db.get_recommendations(fav_genre="Fiction")
        print("Önerilen kitaplar:", recommendations)

        # Test 8: Teslim tarihi uzatma
        print("\nTeslim tarihi uzatma testi...")
        success = db.extend_due_date(
            user_id=1,
            book_isbn="97831614841",
            new_due_date="2024-12-20"
        )
        print("Teslim tarihi uzatma başarılı mı:", success)

        # Test 9: Kullanıcı raporu oluşturma
        print("\nKullanıcı raporu testi...")
        user_report = db.createUserReport(user_id=10035)
        print("Kullanıcı raporu:", user_report)

        # Test 10: Kitap raporu oluşturma
        print("\nKitap raporu testi...")
        book_report = db.createBookReport(isbn="97831614841")
        print("Kitap raporu:", book_report)



if __name__ == "__main__":
    # main.test1()
    main.test2()