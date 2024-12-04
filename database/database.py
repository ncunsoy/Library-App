from sqlalchemy import create_engine, text, inspect
import pandas as pd

# Database engine
db_path = 'sqlite:///LibraryApp.db'
engine = create_engine(db_path)

file_paths = {
    "Users": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/users.csv",
    "Staff": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/staffs.csv",
    "Book": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/books.csv",
    "Reservation": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/reservation.csv",
    "Comment": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/comment.csv",
    "ReadingList": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/readingList.csv",
    "Notification": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/notification.csv"
}

tables = ["Users", "Staff", "Book", "Comment", "Reservation", "ReadingList", "Notification"]

create_tables_sql = [
    """
    CREATE TABLE Users (
        UserID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        FavouriteGenre TEXT,
        Password TEXT NOT NULL,
        Fine REAL DEFAULT 0
    )
    """,
    """
    CREATE TABLE Staff (
        StaffID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Password TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE Book (
        ISBN TEXT PRIMARY KEY,
        Title TEXT NOT NULL,
        Authors TEXT NOT NULL,
        Description TEXT,
        Genre TEXT NOT NULL,
        Availability BOOLEAN NOT NULL
    )
    """,
    """
    CREATE TABLE Comment (
        CommentID INTEGER PRIMARY KEY,
        UserID INTEGER NOT NULL,
        BookISBN TEXT NOT NULL,
        CommentText TEXT NOT NULL,
        CommentDate TEXT NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
        FOREIGN KEY (BookISBN) REFERENCES Book(ISBN) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Reservation (
        ReservationID INTEGER PRIMARY KEY,
        UserID INTEGER NOT NULL,
        BookISBN TEXT NOT NULL,
        ReservationDate TEXT NOT NULL,
        DueDate TEXT NOT NULL,
        Status TEXT DEFAULT 'Active',
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
        FOREIGN KEY (BookISBN) REFERENCES Book(ISBN) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE ReadingList (
        ReadingListID INTEGER PRIMARY KEY,
        UserID INTEGER NOT NULL,
        BookISBN TEXT NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
        FOREIGN KEY (BookISBN) REFERENCES Book(ISBN) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Notification (
        NotificationID INTEGER PRIMARY KEY,
        UserID INTEGER NOT NULL,
        Message TEXT NOT NULL,
        NotificationDate TEXT NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
    )
    """
]

def drop_all_tables(engine):
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF;"))
        inspector = inspect(engine)
        for table_name in inspector.get_table_names():
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            print(f"Dropped table: {table_name}")
        conn.execute(text("PRAGMA foreign_keys = ON;"))

def create_schema(engine):
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))
        for sql in create_tables_sql:
            conn.execute(text(sql))
        print("Database schema created successfully.")

def load_csv_to_sql(table_name, file_path, engine):
    try:
        print(f"Loading data for table: {table_name}...")
        df = pd.read_csv(file_path)
        # Drop the "Unnamed: 0" column if it exists
        if "Unnamed: 0" in df.columns:
            df = df.drop(columns=["Unnamed: 0"])
        df = df.loc[:, ~df.columns.duplicated()]
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Successfully loaded {table_name} into the database.")
    except Exception as e:
        print(f"Error loading {table_name}: {e}")

if __name__ == "__main__":
    print("Dropping existing tables...")
    drop_all_tables(engine)

    print("\nCreating database schema...")
    create_schema(engine)

    print("\nLoading data into tables...")
    for table_name in tables:
        if table_name in file_paths:
            load_csv_to_sql(table_name, file_paths[table_name], engine)

    print("\nValidating data...")
    with engine.connect() as conn:
        for table_name in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"Table {table_name}: {count} rows loaded.")
