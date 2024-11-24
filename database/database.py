from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Enum, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
import pandas as pd

# Veritabanı bağlantı URL'si
DATABASE_URL = "mysql+mysqlconnector://root:@localhost/library_db"

DB_USER = "root"
DB_PASSWORD = "ceyda"  
DB_HOST = "localhost"

# Tabloları tanımla
users = Table('users',
    Column('user_id', Integer, primary_key=True),
    Column('username', String(50), nullable=False),
    Column('password', String(100), nullable=False),
    Column('email', String(100), nullable=False, unique=True),
    Column('full_name', String(100), nullable=False),
    Column('created_at', DateTime, server_default=func.current_timestamp()),
    mysql_engine='InnoDB'
)

staffs = Table('staffs', 
    Column('staff_id', Integer, primary_key=True),
    Column('username', String(50), nullable=False),
    Column('password', String(100), nullable=False),
    Column('email', String(100), nullable=False, unique=True),
    Column('full_name', String(100), nullable=False),
    Column('role', String(50), nullable=False),
    Column('created_at', DateTime, server_default=func.current_timestamp()),
    mysql_engine='InnoDB'
)

books = Table('books',
    Column('book_id', Integer, primary_key=True),
    Column('title', String(200), nullable=False),
    Column('author', String(100), nullable=False),
    Column('isbn', String(13), unique=True),
    Column('publication_year', Integer),
    Column('genre', String(50)),
    Column('quantity', Integer, server_default='1'),
    Column('available_quantity', Integer, server_default='1'),
    mysql_engine='InnoDB'
)

reading_list = Table('reading_list',
    Column('list_id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.user_id', ondelete='CASCADE')),
    Column('list_name', String(100), nullable=False),
    Column('created_at', DateTime, server_default=func.current_timestamp()),
    mysql_engine='InnoDB'
)

reading_list_items = Table('reading_list_items',
    Column('item_id', Integer, primary_key=True),
    Column('list_id', Integer, ForeignKey('reading_list.list_id', ondelete='CASCADE')),
    Column('book_id', Integer, ForeignKey('books.book_id', ondelete='CASCADE')),
    Column('added_at', DateTime, server_default=func.current_timestamp()),
    mysql_engine='InnoDB'
)

reservation = Table('reservation',
    Column('reservation_id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.user_id', ondelete='CASCADE')),
    Column('book_id', Integer, ForeignKey('books.book_id', ondelete='CASCADE')),
    Column('reservation_date', DateTime, server_default=func.current_timestamp()),
    Column('status', Enum('active', 'completed', 'cancelled'), server_default='active'),
    mysql_engine='InnoDB'
)

comment = Table('comment', 
    Column('comment_id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.user_id', ondelete='CASCADE')),
    Column('book_id', Integer, ForeignKey('books.book_id', ondelete='CASCADE')),
    Column('content', Text, nullable=False),
    Column('rating', Integer),
    Column('created_at', DateTime, server_default=func.current_timestamp()),
    mysql_engine='InnoDB'
)

notification = Table('notification',
    Column('notification_id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.user_id', ondelete='CASCADE')),
    Column('message', Text, nullable=False),
    Column('is_read', Boolean, server_default='0'),
    Column('created_at', DateTime, server_default=func.current_timestamp()),
    mysql_engine='InnoDB'
)

def create_database():
    """Veritabanı ve tabloları oluşturur"""
    try:
        # Engine oluştur
        engine = create_engine(DATABASE_URL)
        
        # Önce veritabanını oluştur
        temp_engine = create_engine("mysql+mysqlconnector://root:@localhost/")
        with temp_engine.connect() as conn:
            conn.execute("CREATE DATABASE IF NOT EXISTS library_db")
        
     
        print("Veritabanı ve tablolar başarıyla oluşturuldu!")
        return engine
    
    except Exception as e:
        print(f"Hata: {e}")
        return None

def load_csv_data(engine, csv_files):
    """CSV dosyalarından verileri yükler"""
    try:
        for table_name, file_path in csv_files.items():
            try:
                df = pd.read_csv(file_path)
                df.to_sql(table_name.replace('.csv', ''), 
                         engine, 
                         if_exists='append', 
                         index=False)
                print(f"{table_name} tablosuna veriler yüklendi.")
            except Exception as e:
                print(f"{table_name} için hata: {e}")
                continue
        
        print("Tüm veriler başarıyla yüklendi!")
        
    except Exception as e:
        print(f"Veri yükleme hatası: {e}")


def main():
    engine = create_database()
    if engine:
        # CSV dosyalarının yolları
        csv_files = {
            'users.csv': 'D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/users.csv',
            'staffs.csv': 'D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/staffs.csv',
            'books.csv': 'D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/books.csv',
            'readingList.csv': 'D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/readingList.csv',
            'reservation.csv': 'D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/reservation.csv',
            'comment.csv': 'D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/comment.csv',
            'notification.csv': 'D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/notification.csv'
        }
        
        load_csv_data(engine, csv_files)

if __name__ == "__main__":
    main()

