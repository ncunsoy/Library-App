from sqlalchemy import create_engine, text, inspect
import pandas as pd

# File paths
file_paths = {
    "Users": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/users.csv",
    "Staff": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/staffs.csv",
    "Book": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/books.csv",
    "Reservation": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/reservation.csv",
    "Comment": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/comment.csv",
    "ReadingList": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/readingList.csv",
    "Notification": "D:/Datalarım/Desktop/bil481/Library App/database/data_prepreation/Tables/notification.csv"
}

# Database engine
db_path = 'sqlite:///LibraryApp.db'
engine = create_engine(db_path)

# Tables in order of creation (to handle foreign key dependencies)
tables = ["Users", "Staff", "Book", "Reservation", "Comment", "ReadingList", "Notification"]

# Create table statements
create_tables_sql = [
    """
    CREATE TABLE Users (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        FavouriteGenre TEXT,
        Password TEXT NOT NULL,
        Fine REAL DEFAULT 0
    )
    """,
    """
    CREATE TABLE Staff (
        StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Password TEXT NOT NULL,
    )
    """,
    """
    CREATE TABLE Book (
        ISBN TEXT PRIMARY KEY,
        Title TEXT NOT NULL,
        Authors TEXT NOT NULL,
        Description TEXT,
        Genre TEXT NOT NULL,
        Availability INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE Reservation (
        ReservationID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        BookISBN TEXT NOT NULL,
        ReservationDate TEXT NOT NULL,
        DueDate TEXT NOT NULL,
        Status TEXT DEFAULT 'active',
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
        FOREIGN KEY (BookISBN) REFERENCES Book(ISBN) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Comment (
        CommentID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        BookISBN TEXT NOT NULL,
        CommentText TEXT NOT NULL,
        CommentDate TEXT NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
        FOREIGN KEY (BookISBN) REFERENCES Book(ISBN) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE ReadingList (
        ReadingListID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        BookISBN TEXT NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
        FOREIGN KEY (BookISBN) REFERENCES Book(ISBN) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Notification (
        NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        Message TEXT NOT NULL,
        NotificationDate TEXT NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
    )
    """
]

def get_existing_tables(engine):
    inspector = inspect(engine)
    return inspector.get_table_names()

def drop_all_tables(engine):
    existing_tables = get_existing_tables(engine)
    with engine.connect() as conn:
        # Temporarily disable foreign key constraints
        conn.execute(text("PRAGMA foreign_keys = OFF;"))
        
        for table in existing_tables:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                conn.commit()
                print(f"Dropped table: {table}")
            except Exception as e:
                print(f"Error dropping table {table}: {e}")
        
        # Re-enable foreign key constraints
        conn.execute(text("PRAGMA foreign_keys = ON;"))
        conn.commit()

def create_schema(engine):
    with engine.connect() as conn:
        # Enable foreign key support
        conn.execute(text("PRAGMA foreign_keys = ON;"))
        conn.commit()
        
        # Create tables
        for create_sql in create_tables_sql:
            try:
                conn.execute(text(create_sql))
                conn.commit()
            except Exception as e:
                print(f"Error creating table: {e}")
                raise
        
        print("Database schema created successfully.")

def load_csv_to_sql(table_name, file_path, engine):
    try:
        # Load CSV into a DataFrame
        df = pd.read_csv(file_path)
        
        # Drop any 'Unnamed' columns
        unnamed_cols = [col for col in df.columns if 'Unnamed' in col]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
            
        # Drop duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Insert the data into the pre-defined table
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Successfully loaded {table_name} into the database.")
        
    except Exception as e:
        print(f"Error loading {table_name}: {e}")
        raise

# Main script
if __name__ == "__main__":
    try:
        # Step 1: Drop all existing tables
        print("Dropping existing tables...")
        drop_all_tables(engine)
        
        # Step 2: Create fresh schema
        print("\nCreating new schema...")
        create_schema(engine)

        # Step 3: Load data into the database in the correct order
        print("\nLoading data...")
        for table_name in tables:
            if table_name in file_paths:
                load_csv_to_sql(table_name, file_paths[table_name], engine)
            
    except Exception as e:
        print(f"An error occurred during database setup: {e}")