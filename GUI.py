import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, Listbox, Scrollbar
from PIL import Image,ImageTk
from User import User
from StaffMember import StaffMember
from database.db_controller import *

class LibraryApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.geometry("900x600")
        self.current_user = None
        self.controller = DatabaseController(db_name='LibraryApp.db')  # DatabaseController örneği oluşturma
        self.initialize_login_screen()
        self.root.mainloop()

    def initialize_login_screen(self):
        """Initialize the login screen with a background image."""
        self.clear_screen()
        # Arka plan görselini yükleme
        background_image = Image.open("library_background.png")  # Resim dosyasının yolu
        background_image = background_image.resize((900, 600), Image.LANCZOS)  # Yeni ölçeklendirme yöntemi
        self.bg_image = ImageTk.PhotoImage(background_image)
        
        # Canvas widget ile arka plan görselini yerleştirme
        canvas = tk.Canvas(self.root, width=900, height=600)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Giriş formunu Canvas üzerine yerleştirme
        frame = tk.Frame(self.root, bg="white")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Orta konuma yerleştirme
        
        tk.Label(frame, text="Library Management System", font=("Arial", 20, "bold"), bg="white").grid(row=0, columnspan=2, pady=10)
        
        tk.Label(frame, text="Username", font=("Arial", 12), bg="white").grid(row=1, column=0, pady=5, sticky=tk.W)
        username_entry = tk.Entry(frame, font=("Arial", 12))
        username_entry.grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(frame, text="Password", font=("Arial", 12), bg="white").grid(row=2, column=0, pady=5, sticky=tk.W)
        password_entry = tk.Entry(frame, font=("Arial", 12), show="*")
        password_entry.grid(row=2, column=1, pady=5, padx=10)
        
        tk.Button(frame, text="Login as User", 
                  command=lambda: self.login(username_entry.get(), password_entry.get(), is_staff=False),
                  bg="blue", fg="white", font=("Arial", 12)).grid(row=3, column=0, pady=10)
        tk.Button(frame, text="Login as Staff", 
                  command=lambda: self.login(username_entry.get(), password_entry.get(), is_staff=True),
                  bg="green", fg="white", font=("Arial", 12)).grid(row=3, column=1, pady=10)

    def login(self, username, password, is_staff):
        """Authenticate user or staff login from the database."""
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        
        if is_staff:
            # Staff login kontrolü
            query = "SELECT * FROM Staff WHERE Name = ? AND Password = ?"
            staff = self.controller._cursor.execute(query, (username, password)).fetchone()
            if staff:
                self.current_user = StaffMember(name=staff[1], password=staff[2], staffID=staff[0])  # Örnek indeksler
                self.initialize_staff_dashboard()
            else:
                messagebox.showerror("Error", "Invalid Staff credentials.")
        else:
            # User login kontrolü
            query = "SELECT * FROM Users WHERE Name = ? AND Password = ?"
            user = self.controller._cursor.execute(query, (username, password)).fetchone()
            if user:
                self.current_user = User(
                    name=user[1],  # Kullanıcı adı
                    user_id=user[0],  # Kullanıcı ID
                    password=user[3],  # Şifre
                    favourite_genre=user[2],  # Favori Tür
                    reading_list=[],  # Varsayılan
                    past_reserved_books=[],  # Varsayılan
                    current_notification=[],  # Varsayılan
                    fine=user[4],  # Ceza miktarı
                    comments=[]  # Varsayılan
                )
                self.initialize_user_dashboard()
            else:
                messagebox.showerror("Error", "Invalid User credentials.")

    def initialize_user_dashboard(self):
        """Set up the user dashboard with a search bar and notification panel."""
        self.clear_screen()

        # Başlık
        tk.Label(self.root, text="Library Management System", font=("Arial", 18, "bold")).pack(pady=10)

        # Kullanıcı Hoş Geldiniz Mesajı
        tk.Label(self.root, text=f"Welcome, {self.current_user._name}!", font=("Arial", 14)).pack(pady=5)

        # Arama Çubuğu Çerçevesi
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10, padx=20, anchor="nw")

        # Title
        tk.Label(search_frame, text="Title:", font=("Arial", 12)).grid(row=0, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        title_entry = tk.Entry(search_frame, font=("Arial", 12), width=20)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Author
        tk.Label(search_frame, text="Author:", font=("Arial", 12)).grid(row=1, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        author_entry = tk.Entry(search_frame, font=("Arial", 12), width=20)
        author_entry.grid(row=1, column=1, padx=5, pady=5)

        # Genre
        tk.Label(search_frame, text="Genre:", font=("Arial", 12)).grid(row=1, column=2, padx=(10, 5), pady=5, sticky=tk.E)
        genre_combobox = ttk.Combobox(search_frame, font=("Arial", 12), state="readonly", width=15)
        genre_combobox['values'] = self.fetch_genres_from_db()  # Türleri veritabanından çek
        genre_combobox.set("Select Genre")
        genre_combobox.grid(row=1, column=3, padx=5, pady=5)

        # Search Button
        tk.Button(search_frame, text="Search", bg="blue", fg="white", font=("Arial", 12),
                command=lambda: self.update_search_results(
                    title=title_entry.get().strip(),
                    author=author_entry.get().strip(),
                    genre=genre_combobox.get() if genre_combobox.get() != "Select Genre" else None)
                ).grid(row=0, column=3, rowspan=2, padx=(10, 0), pady=5)

        # Sonuç Çerçevesi
        self.results_frame = tk.Frame(self.root, width=600)  # ÖNEMLİ: `self.results_frame` tanımlanıyor
        self.results_frame.pack(side=tk.LEFT, padx=(20, 10), pady=(10, 0), fill=tk.Y)
        tk.Label(self.results_frame, text="Search Results:", font=("Arial", 14, "bold"), anchor="w").pack(anchor="w")

        # Treeview
        columns = ("Title", "Author", "Genre")
        self.tree = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=15)
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Genre", text="Genre")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Scrollbar ekleme
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bildirim Paneli
        self.notifications_frame = tk.Frame(self.root, bg="red", width=200)
        self.notifications_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        tk.Label(self.notifications_frame, text="Notifications", font=("Arial", 14, "bold"), bg="red", fg="white").pack(pady=10)
        self.notification_list = tk.Listbox(self.notifications_frame, font=("Arial", 12), bg="white", height=20, width=25)
        self.notification_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bildirimleri yükle
        notifications = self.load_notifications()
        for note in notifications:
            self.notification_list.insert(tk.END, note)



    def initialize_user_dashboard(self):
        """Set up the user dashboard with a search bar and notification panel."""
        self.clear_screen()


        # Başlık
        tk.Label(self.root, text="Library Management System", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Label(self.root, text=f"Welcome, {self.current_user._name}!", font=("Arial", 14)).pack(pady=5)

    
        # Arama Çubuğu Çerçevesi
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10, padx=20, anchor="nw")

        # Title
        tk.Label(search_frame, text="Title:", font=("Arial", 12)).grid(row=0, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        title_entry = tk.Entry(search_frame, font=("Arial", 12), width=20)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Author
        tk.Label(search_frame, text="Author:", font=("Arial", 12)).grid(row=1, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        author_entry = tk.Entry(search_frame, font=("Arial", 12), width=20)
        author_entry.grid(row=1, column=1, padx=5, pady=5)

        # Genre
        tk.Label(search_frame, text="Genre:", font=("Arial", 12)).grid(row=1, column=2, padx=(10, 5), pady=5, sticky=tk.E)
        genre_combobox = ttk.Combobox(search_frame, font=("Arial", 12), state="readonly", width=15)
        genres = [""] + self.fetch_genres_from_db()  # Boş değer ekleniyor
        genre_combobox['values'] = genres
        genre_combobox.set("Select Genre")
        genre_combobox.grid(row=1, column=3, padx=5, pady=5)

        # Search Icon
        search_icon = Image.open("search_icon.png")  # Simge dosyasını yükleme
        search_icon = search_icon.resize((25, 25), Image.LANCZOS)  # Simgeyi yeniden boyutlandırma
        search_image = ImageTk.PhotoImage(search_icon)

        search_button = tk.Button(
            search_frame,
            image=search_image,
            command=lambda: self.update_search_results(
                title=title_entry.get().strip(),
                author=author_entry.get().strip(),
                genre=genre_combobox.get() if genre_combobox.get() not in ["", "Select Genre"] else None
            ),
            bg="white",
            bd=0
        )
        search_button.grid(row=0, column=3, rowspan=1, padx=(10, 0), pady=5)
        self.search_icon = search_image  # Simge referansı korunuyor

        # Sonuç Çerçevesi
        self.results_frame = tk.Frame(self.root, width=600)  # ÖNEMLİ: `self.results_frame` tanımlanıyor
        self.results_frame.pack(side=tk.LEFT, padx=(20, 10), pady=(10, 0), fill=tk.Y)
        tk.Label(self.results_frame, text="Search Results:", font=("Arial", 14, "bold"), anchor="w").pack(anchor="w")

        # Treeview
        columns = ("Title", "Author", "Genre")
        self.tree = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=15)
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Genre", text="Genre")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Scrollbar ekleme
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bildirim Paneli
        self.notification_frame = tk.Frame(self.root, bg="red", width=200, height=600)  # Genişlik ve yükseklik sabitlendi
        self.notification_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.notification_frame.pack_propagate(False)  # İçeriklere göre yeniden boyutlanmayı engeller

        # Başlık
        tk.Label(
            self.notification_frame,
            text="Notifications",
            font=("Arial", 14, "bold"),
            bg="red",
            fg="white"
        ).pack(pady=10)

        # Bildirim Listesi
        self.notification_list = tk.Listbox(
            self.notification_frame,
            font=("Arial", 12),
            bg="white",
            height=25,  # Listbox yüksekliği artırıldı
            width=30    # Listbox genişliği sabitlendi
        )
        self.notification_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)







    
    def fetch_genres_from_db(self):
        """Fetch unique genres from the database."""
        try:
            query = "SELECT DISTINCT Genre FROM Book"  # Benzersiz türleri getirir
            genres = [row[0] for row in self.controller._cursor.execute(query).fetchall()]
            return genres
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching genres: {e}")
            return []

        


        try:
            if title:
                title_results = self.current_user.search_by_title(title)
                results.update(title_results)

            if author:
                author_results = self.current_user.search_by_author(author)
                results.update(author_results)

            if genre:
                genre_results = self.current_user.search_by_genre(genre)
                results.update(genre_results)

            # Display results
            if results:
                result_message = "\n".join(results)
                messagebox.showinfo("Search Results", f"Found {len(results)} book(s):\n\n{result_message}")
            else:
                messagebox.showinfo("Search Results", "No books found matching your criteria.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while searching: {e}")


    def update_search_results(self, title=None, author=None, genre=None):
        """Update the search results in the dashboard."""
        # Mevcut sonuçları temizle
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Treeview widget'ı oluştur
        columns = ("Title", "Author", "Genre")
        tree = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=10)
        tree.heading("Title", text="Title")
        tree.heading("Author", text="Author")
        tree.heading("Genre", text="Genre")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar ekleme ve Treeview'e bağlama
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        results = None

        # Kullanıcı sınıfından kitapları ara
        try:
            if title:
                title_results = set(self.current_user.search_by_title(title))
                results = title_results if results is None else results.intersection(title_results)

            if author:
                author_results = set(self.current_user.search_by_author(author))
                results = author_results if results is None else results.intersection(author_results)

            if genre:
                genre_results = set(self.current_user.search_by_genre(genre))
                results = genre_results if results is None else results.intersection(genre_results)


            
            # Sonuçları ekrana yazdır
            if not results:
                tk.Label(self.results_frame, text="No books found.", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
            else:
                for book in results:
                    # book: (isbn, title, authors, description, genre, availability)
                    tree.insert("", "end", values=(book[1], book[2], book[4]))

                # Seçim olayını bağlama
                def on_item_select(event):
                    selected_item = tree.focus()  # Seçilen öğenin ID'sini al
                    item_values = tree.item(selected_item, "values")  # Seçilen öğenin değerlerini al
                    messagebox.showinfo(
                        "Book Selected",
                        f"You selected:\n\nTitle: {item_values[0]}\nAuthor: {item_values[1]}\nGenre: {item_values[2]}"
                    )

                tree.bind("<<TreeviewSelect>>", on_item_select)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while searching: {e}")


    def load_notifications(self):
        """Kullanıcının bildirimlerini güncellemek için kullanılan fonksiyon."""
        # Bildirim çerçevesini temizle
        for widget in self.notification_frame.winfo_children():  # Doğru isimlendirme
            widget.destroy()

        # Kullanıcının bildirimlerini al
        notifications_list = self.current_user.get_current_notification()

        # Bildirimleri ekle
        if not notifications_list:
            tk.Label(self.notification_frame, text="No notifications.", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        else:
            for notification in notifications_list:
                tk.Label(self.notification_frame, text=notification, font=("Arial", 12), bg="white").pack(anchor="w", pady=2)




    def clear_screen(self):
        # Clear all widgets from the current screen
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = LibraryApp()
