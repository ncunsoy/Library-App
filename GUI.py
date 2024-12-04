import tkinter as tk
from tkinter import ttk, messagebox
from database.db_controller import DatabaseController
from User import User
from Book import Book
from Notification import Notification
from Comment import Comment




class LibraryApp:
    def __init__(self):
        self.controller = DatabaseController()
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.geometry("900x600")
        self.current_user = None  # Instance of User
        self.build_login_screen()

    def build_login_screen(self):
        """Build the login screen."""
        self.clear_screen()

        bg_frame = tk.Frame(self.root, bg="white")
        bg_frame.pack(fill="both", expand=True)

        title = tk.Label(bg_frame, text="Library Management System", font=("Arial", 28, "bold"), bg="white")
        title.pack(pady=20)

        login_frame = tk.Frame(bg_frame, bg="white")
        login_frame.pack(pady=50)

        tk.Label(login_frame, text="Username:", font=("Arial", 14), bg="white").grid(row=0, column=0, padx=10, pady=10)
        username_entry = tk.Entry(login_frame, font=("Arial", 14))
        username_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(login_frame, text="Password:", font=("Arial", 14), bg="white").grid(row=1, column=0, padx=10, pady=10)
        password_entry = tk.Entry(login_frame, show="*", font=("Arial", 14))
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(login_frame, text="Login", font=("Arial", 14),
                  command=lambda: self.login(username_entry.get(), password_entry.get())).grid(row=2, column=0, pady=20)

    def build_login_screen(self):
        """Build the login screen."""
        self.clear_screen()

        bg_frame = tk.Frame(self.root, bg="white")
        bg_frame.pack(fill="both", expand=True)

        title = tk.Label(bg_frame, text="Library Management System", font=("Arial", 28, "bold"), bg="white")
        title.pack(pady=20)

        login_frame = tk.Frame(bg_frame, bg="white")
        login_frame.pack(pady=50)

        tk.Label(login_frame, text="Username:", font=("Arial", 14), bg="white").grid(row=0, column=0, padx=10, pady=10)
        username_entry = tk.Entry(login_frame, font=("Arial", 14))
        username_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(login_frame, text="Password:", font=("Arial", 14), bg="white").grid(row=1, column=0, padx=10, pady=10)
        password_entry = tk.Entry(login_frame, show="*", font=("Arial", 14))
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        login_button = tk.Button(login_frame, text="Login", font=("Arial", 14), bg="red", fg="white",
                                 command=lambda: self.login(username_entry.get(), password_entry.get()))
        login_button.grid(row=2, columnspan=2, pady=20)

    def login(self, username, password):
        """Authenticate user or staff login using the database."""
        try:
            query = "SELECT * FROM Users WHERE Name = ? AND Password = ?"
            result = self.controller._cursor.execute(query, (username, password)).fetchone()
            if result:
                self.current_user = User(user_id=result[0], name=result[1], password=result[2], favourite_genre=result[3],)#Eklemeler yapılacak 
                self.build_user_dashboard()
            else:
                query = "SELECT * FROM Staff WHERE Name = ? AND Password = ?"
                result = self.controller._cursor.execute(query, (username, password)).fetchone()
                if result:
                    self.current_user = StaffMember() #Düzenlecek 
                    self.build_user_dashboard()
                else:
                    messagebox.showerror("Error", "Invalid credentials")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def build_user_dashboard(self):
        """Build the user dashboard."""
        self.clear_screen()
        tk.Label(self.root, text=f"Welcome, {self.current_user['name']}!", font=("Arial", 20)).pack(pady=20)

        frame = tk.Frame(self.root)
        frame.pack()

        tk.Button(frame, text="Search Books", font=("Arial", 14), width=15, command=self.search_books_screen).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(frame, text="View Notifications", font=("Arial", 14), width=15, command=self.view_notifications).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(frame, text="View Reservations", font=("Arial", 14), width=15, command=self.view_reservations).grid(row=0, column=2, padx=10, pady=10)
        tk.Button(frame, text="Manage Profile", font=("Arial", 14), width=15, command=self.manage_profile).grid(row=1, column=1, pady=10)

    

    def clear_screen(self):
        """Clear all widgets from the screen."""
        for widget in self.root.winfo_children():
            widget.destroy()





    def run(self):
        """Run the main application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = LibraryApp()
    app.run()
