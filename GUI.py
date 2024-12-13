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


        # Profil simgesini ekleme
        profile_icon = Image.open("user_icon.png")  # İkon dosyasını yükle
        profile_icon = profile_icon.resize((100, 100), Image.LANCZOS)  # Boyutlandır
        profile_image = ImageTk.PhotoImage(profile_icon)

        profile_button = tk.Button(
            self.root,
            image=profile_image,
            command=self.open_profile_screen,  # Yeni ekran açacak fonksiyon
            bg="white",
            bd=0
        )
        profile_button.image = profile_image  # Referansı kaybetmemek için sakla
        profile_button.place(relx=0.85, rely=0.1)  # Sağ üst köşeye yerleştir


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



    def initialize_staff_dashboard(self):
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


        # Profil simgesini ekleme
        profile_icon = Image.open("user_icon.png")  # İkon dosyasını yükle
        profile_icon = profile_icon.resize((100, 100), Image.LANCZOS)  # Boyutlandır
        profile_image = ImageTk.PhotoImage(profile_icon)

        profile_button = tk.Button(
            self.root,
            image=profile_image,
            command=self.open_profile_screen,  # Yeni ekran açacak fonksiyon
            bg="white",
            bd=0
        )
        profile_button.image = profile_image  # Referansı kaybetmemek için sakla
        profile_button.place(relx=0.85, rely=0.1)  # Sağ üst köşeye yerleştir


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

    

    def open_profile_screen(self):
        """Kullanıcı profili için yeni bir ekran aç."""
        profile_window = tk.Toplevel(self.root)
        profile_window.title("User Profile")
        profile_window.geometry("800x400")  # Yeni pencere boyutu

        if isinstance(self.current_user, User):
            tk.Label(profile_window, text="User Profile", font=("Arial", 16, "bold")).pack(pady=10)
            
        if isinstance(self.current_user, StaffMember):
            tk.Label(profile_window, text="Admin Panel", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(profile_window, text=f"Username: {self.current_user._name}", font=("Arial", 12)).pack(pady=5)
        user_frame = tk.Frame(profile_window)
        user_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.BOTH, expand=True)

        book_frame = tk.Frame(profile_window)
        book_frame.pack(side=tk.RIGHT, padx=20, pady=10, fill=tk.BOTH, expand=True)

        def open_readingList_window():      
        
            reading_window = tk.Toplevel(profile_window)
            reading_window.title("Reading List")
            reading_window.geometry("300x300")  # Yeni pencere boyutu
            tk.Label(reading_window, text="My Reading Wish List", font=("Arial", 16, "bold")).pack(pady=10)
            frame = tk.Frame(reading_window)
            frame.pack(expand=True, fill=tk.BOTH)

            
        
            text_widget = tk.Text(frame, wrap=tk.WORD, height=10, width=30)
            text_widget.grid(row=0, column=0, padx=5, pady=5)
            scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
            scrollbar.grid(row=0, column=1, sticky="ns", padx=5, pady=5)  # Sağ tarafa hizalanır
        
            text_widget.config(yscrollcommand=scrollbar.set)

            # Grid düzenlemesi için ortalama
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            
            readingList = self.current_user._reading_list
            #just_comment= [item[0] for item in comments]
            #readingList = [''.join(readingList)]
             # Yorumları Text widget'a ekle
            for read in readingList:
                query="SELECT Title FROM Book WHERE ISBN = ?"
                title=self.controller._cursor.execute(query, (read,)).fetchone()
                text_widget.insert(tk.END, f"- {title}\n")
        
            # Scrollbar
            scrollbar = ttk.Scrollbar(reading_window, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)

        def open_recommend_window():      
        
            recommend_window = tk.Toplevel(profile_window)
            recommend_window.title("Recommendations")
            recommend_window.geometry("300x300")  # Yeni pencere boyutu
            tk.Label(recommend_window, text="My Recommendations", font=("Arial", 16, "bold")).pack(pady=10)
            frame = tk.Frame(recommend_window)
            frame.pack(expand=True, fill=tk.BOTH)

            
        
            text_widget = tk.Text(frame, wrap=tk.WORD, height=10, width=30)
            text_widget.grid(row=0, column=0, padx=5, pady=5)
            scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
            scrollbar.grid(row=0, column=1, sticky="ns", padx=5, pady=5)  # Sağ tarafa hizalanır
        
            text_widget.config(yscrollcommand=scrollbar.set)

            # Grid düzenlemesi için ortalama
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            
            recommend = self.current_user.view_recommendations()
            #just_comment= [item[0] for item in comments]

             # Yorumları Text widget'a ekle
            for reco in recommend:
                text_widget.insert(tk.END, f"- {reco}\n")
        
            # Scrollbar
            scrollbar = ttk.Scrollbar(recommend_window, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)

        def open_commands_window():      
        
            commands_window = tk.Toplevel(profile_window)
            commands_window.title("All Comments")
            commands_window.geometry("300x300")  # Yeni pencere boyutu
            tk.Label(commands_window, text="My All Commands", font=("Arial", 16, "bold")).pack(pady=10)
            frame = tk.Frame(commands_window)
            frame.pack(expand=True, fill=tk.BOTH)

            
        
            text_widget = tk.Text(frame, wrap=tk.WORD, height=10, width=30)
            text_widget.grid(row=0, column=0, padx=5, pady=5)
            scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
            scrollbar.grid(row=0, column=1, sticky="ns", padx=5, pady=5)  # Sağ tarafa hizalanır
        
            text_widget.config(yscrollcommand=scrollbar.set)

            # Grid düzenlemesi için ortalama
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            
            comments = self.current_user.get_comments()
            just_comment= [item[0] for item in comments]

             # Yorumları Text widget'a ekle
            for comment in just_comment:
                text_widget.insert(tk.END, f"- {comment}\n")
        
            # Scrollbar
            scrollbar = ttk.Scrollbar(commands_window, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)

        # Save button
        def save_changes():
            if isinstance(self.current_user, User):
                new_name = username_entry.get()
                new_password = password_entry.get()
                new_genre = genre_entry.get()
                #readinglist = read_entry.get()

                #if readinglist.strip():
                #self.current_user._reading_list = readinglist
                    
                if new_name.strip():
                    self.current_user._name = new_name
                    self.controller.change_name(User, self.current_user.getID,new_name)
                if new_genre.strip():
                    self.current_user._favourite_genre = new_genre
                    self.controller.set_favorite_genre(self.current_user.getID, new_genre)
                if new_password.strip():
                    self.current_user._password = new_password
                    self.controller.change_password(User, self.current_user.getID, new_password)

                tk.messagebox.showinfo("Success", "Profile updated successfully!")
                profile_window.destroy()
            
        def register_user():
            if isinstance(self.current_user, StaffMember):
                new_users_name = users_username_entry.get()
                new_users_password = users_password_entry.get()
                new_users_genre = users_favorite_genre.get()
                self.controller.register_user(new_users_name, new_users_password, new_users_genre)
            tk.messagebox.showinfo("Success", "User registered successfully!")
            profile_window.destroy()

        def remove_user():
            if isinstance(self.current_user, StaffMember):
                deleted_users_id = users_id_entry.get()
                self.controller.delete_user(deleted_users_id)
            tk.messagebox.showinfo("Success", "User removed successfully!")
            profile_window.destroy()

        def user_report():
            if isinstance(self.current_user, StaffMember):
                report_users_id = users_id_entry.get()
                self.controller.createUserReport(report_users_id)
                tk.messagebox.showinfo("Success", "User report made successfully!")
                tk.messagebox.showinfo("User Report", self.current_user.createUserReport(report_users_id))
                profile_window.destroy()

        def charge_amount():
            if isinstance(self.current_user, StaffMember):
                user = username_fine.get()
                amount = fine_amount.get()
                self.controller.update_fine(user, amount)
                tk.messagebox.showinfo("Success", "Fine charged successfully!")
                profile_window.destroy()

        def remove_fine():
            if isinstance(self.current_user, StaffMember):
                user = username_fine.get()
                self.controller.update_fine(user, 0)
                tk.messagebox.showinfo("Success", "Fine removed successfully!")
                profile_window.destroy()

        def add_book():
            if isinstance(self.current_user, StaffMember):
                added_book_name = book_name.get()
                added_book_author = book_author.get()
                added_book_description = book_description.get()
                added_book_genre = book_genre.get()
                added_book_availability = book_availability.get()
                added_book_isbn = book_isbn.get()
                self.controller.add_book(added_book_isbn,added_book_name,added_book_author,added_book_description,added_book_genre,added_book_availability)
                tk.messagebox.showinfo("Success", "Book added successfully!")
                profile_window.destroy()

        def remove_book():
            if isinstance(self.current_user, StaffMember):
                removed_book_isbn = book_isbn.get()
                self.controller.remove_book(removed_book_isbn)
                tk.messagebox.showinfo("Success", "Book removed successfully!")
                profile_window.destroy()

        def book_report():
            if isinstance(self.current_user, StaffMember):
                report_book_isbn = book_isbn.get()
                self.controller.createBookReport(report_book_isbn)
                tk.messagebox.showinfo("Success", "Book report made successfully!")
                tk.messagebox.showinfo("Book Report", self.current_user.createBookReport(report_book_isbn))
                profile_window.destroy()
 
            
        # Cancel button
        def cancel_changes():
            profile_window.destroy()


        if isinstance(self.current_user, User):

            tk.Label(profile_window, text=f"User ID: {self.current_user._user_id}", font=("Arial", 12)).pack(pady=5)
            tk.Label(profile_window, text=f"Fine: {self.current_user._fine}", font=("Arial", 12)).pack(pady=5)
            tk.Label(profile_window, text=f"Favourite Genre: {self.current_user._favourite_genre}", font=("Arial", 12)).pack(pady=5)
            tk.Label(profile_window, text="Change Username:", font=("Arial", 12)).pack(pady=5)

            # Add input field for changing username
            username_entry = tk.Entry(user_frame, font=("Arial", 12))
            username_entry.pack(pady=5)
            username_entry.insert(0, self.current_user._name)  # Pre-fill with current username

            # Add input field for changing password
            tk.Label(user_frame, text="Change Password:", font=("Arial", 12)).pack(pady=5)
            password_entry = tk.Entry(user_frame, font=("Arial", 12), show="*")
            password_entry.pack(pady=5)

            tk.Label(user_frame, text="Edit Favourite Genre:", font=("Arial", 12)).pack(pady=5)
            genre_entry = tk.Entry(user_frame, font=("Arial", 12))
            genre_entry.pack(pady=5)
            genre_entry.insert(0, self.current_user._favourite_genre)  # Pre-fill with current genre

            # Add input field for adding reading List
            #tk.Label(profile_window, text="Add Reading List:", font=("Arial", 12)).pack(pady=5)
            #read_entry = tk.Entry(profile_window, font=("Arial", 12))
            #read_entry.pack(pady=5)
            #read_entry.insert(0,self.current_user._reading_list)

            tk.Button(profile_window, text="Save Changes", font=("Arial", 12), command=save_changes).pack(pady=10)
            tk.Button(profile_window, text="See Comments", font=("Arial", 12), command=open_commands_window).pack(pady=10)
            tk.Button(profile_window, text="See Recommendations", font=("Arial", 12), command=open_recommend_window).pack(pady=10)
            tk.Button(profile_window, text="See Reading List", font=("Arial", 12), command=open_readingList_window).pack(pady=10)

        elif isinstance(self.current_user, StaffMember):
            tk.Label(user_frame, text="Username:", font=("Arial", 12)).pack(pady=5)
            users_username_entry = tk.Entry(user_frame, font=("Arial", 12))
            users_username_entry.pack(pady=5)
            users_username_entry.insert(0, "Type here...")

            tk.Label(user_frame, text="Password:", font=("Arial", 12)).pack(pady=5)
            users_password_entry = tk.Entry(user_frame, font=("Arial", 12), show="*")
            users_password_entry.pack(pady=5)
            users_password_entry.insert(0, "Type here...")

            tk.Label(user_frame, text="Favorite Genre:", font=("Arial", 12)).pack(pady=5)
            users_favorite_genre = tk.Entry(user_frame, font=("Arial", 12))
            users_favorite_genre.pack(pady=5)
            users_favorite_genre.insert(0, "Type here...")
            tk.Button(user_frame, text="Register User", font=("Arial", 12), command=register_user).pack(pady=10)

            tk.Label(user_frame, text="User ID:", font=("Arial", 12)).pack(pady=5)
            users_id_entry = tk.Entry(user_frame, font=("Arial", 12))
            users_id_entry.pack(pady=5)
            users_id_entry.insert(0, "Type here...")
            tk.Button(user_frame, text="Remove User", font=("Arial", 12), command=remove_user).pack(pady=10)

            tk.Label(book_frame, text="Book Name:", font=("Arial", 12)).pack(pady=5)
            book_name = tk.Entry(book_frame, font=("Arial", 12))
            book_name.pack(pady=5)
            book_name.insert(0, "Type here...")

            tk.Label(book_frame, text="Book Author:", font=("Arial", 12)).pack(pady=5)
            book_author = tk.Entry(book_frame, font=("Arial", 12))
            book_author.pack(pady=5)
            book_author.insert(0, "Type here...")

            tk.Label(book_frame, text="Book Description:", font=("Arial", 12)).pack(pady=5)
            book_description = tk.Entry(book_frame, font=("Arial", 12))
            book_description.pack(pady=5)
            book_description.insert(0, "Type here...")

            tk.Label(book_frame, text="Book Genre:", font=("Arial", 12)).pack(pady=5)
            book_genre = tk.Entry(book_frame, font=("Arial", 12))
            book_genre.pack(pady=5)
            book_genre.insert(0, "Type here...")
            

            tk.Label(book_frame, text="Book Availability:", font=("Arial", 12)).pack(pady=5)
            book_availability = tk.Entry(book_frame, font=("Arial", 12))
            book_availability.pack(pady=5)
            book_availability.insert(0, "Type here...")
            

            tk.Label(book_frame, text="Book ISBN:", font=("Arial", 12)).pack(pady=5)
            book_isbn = tk.Entry(book_frame, font=("Arial", 12))
            book_isbn.pack(pady=5)
            book_isbn.insert(0, "Type here...")
            tk.Button(book_frame, text="Add Book", font=("Arial", 12), command=add_book).pack(pady=10)
            tk.Button(book_frame, text="Remove Book", font=("Arial", 12), command=remove_book).pack(pady=10)
            tk.Button(book_frame, text="Make Book Report", font=("Arial", 12), command=book_report).pack(pady=5)
            tk.Button(user_frame, text="Make User Report", font=("Arial", 12), command=user_report).pack(pady=5)

            tk.Label(user_frame, text=f"Handle Fines", font=("Arial", 12, "bold")).pack(pady=5)
            tk.Label(user_frame, text="Username:", font=("Arial", 12)).pack(pady=5)
            username_fine = tk.Entry(user_frame, font=("Arial", 12))
            username_fine.pack(pady=5)
            username_fine.insert(0, "Type here...")

            tk.Label(user_frame, text="Fine Amount:", font=("Arial", 12)).pack(pady=5)
            fine_amount = tk.Entry(user_frame, font=("Arial", 12))
            fine_amount.pack(pady=5)
            fine_amount.insert(0, "Type here...")
            tk.Button(user_frame, text="Charge Amount", font=("Arial", 12), command=charge_amount).pack(pady=5)
            tk.Button(user_frame, text="Remove Fine", font=("Arial", 12), command=remove_fine).pack(pady=5)

        tk.Button(profile_window, text="Cancel", font=("Arial", 12), command=cancel_changes).pack(pady=5)

    def show_book_details(self, item_values,book_isbn):
        """Show the selected book's details in a new window with separate frames for details and comments."""
        # Create a new window for book details
        details_window = tk.Toplevel(self.root)
        details_window.title("Book Details")
        details_window.geometry("500x500")  # Set window size

        # Frame for Book Details
        details_frame = tk.Frame(details_window, borderwidth=2, relief="groove", padx=10, pady=10)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Fetch the current availability from the database
        query = "SELECT Availability FROM Book WHERE ISBN = ?;"
        availability = self.controller._cursor.execute(query, (book_isbn,)).fetchone()[0]

        # Book Details
        tk.Label(details_frame, text=f"Title: {item_values[0]}", font=("Arial", 12)).pack(anchor="w", pady=5)
        tk.Label(details_frame, text=f"Author: {item_values[1]}", font=("Arial", 12)).pack(anchor="w", pady=5)
        tk.Label(details_frame, text=f"Genre: {item_values[2]}", font=("Arial", 12)).pack(anchor="w", pady=5)

        # Placeholder description and availability
        description = "A detailed description of the book."  # Replace with real description from the database
        availability = "Available" if availability == True else "Reserved"
        availability_label = tk.Label(details_frame, text=f"Availability: {availability}", font=("Arial", 12))
        tk.Label(details_frame, text=f"Description: {description}", font=("Arial", 12), wraplength=400, justify="left").pack(anchor="w", pady=5)
        availability_label.pack(anchor="w", pady=5)


        # Frame for Comments
        comment_frame = tk.Frame(details_window, borderwidth=2, relief="groove", padx=10, pady=10)
        comment_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add Comment Label and Entry
        tk.Label(comment_frame, text="Add a Comment:", font=("Arial", 12)).pack(anchor="w", pady=5)
        comment_entry = tk.Entry(comment_frame, font=("Arial", 12), width=40)
        comment_entry.pack(anchor="w", pady=5)

        # Scrollable Comment Box
        comment_scroll = tk.Scrollbar(comment_frame, orient="vertical")
        comment_list = tk.Listbox(comment_frame, font=("Arial", 12), yscrollcommand=comment_scroll.set, height=10)
        comment_scroll.config(command=comment_list.yview)
        comment_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        comment_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        


        # Add Comment Button
        def add_comment():
            comment = comment_entry.get().strip()
            if comment:
                result = self.current_user.add_comment(item_values[0], comment)  # Pass the ISBN and comment
                if result == "Comment Added":
                    comment_entry.delete(0, tk.END)
                    comment_list.insert(tk.END, comment)
                    messagebox.showinfo("Comment Added", "Your comment has been added!")
                else:
                    messagebox.showerror("Error", result)
            else:
                messagebox.showerror("Error", "Please enter a comment.")


        tk.Button(
            comment_frame,
            text="Add Comment",
            command=add_comment,
            font=("Arial", 12),
            bg="blue",
            fg="white"
        ).pack(anchor="w", pady=10)

        

        # Reserve Book Button
        def reserve_book():
            print([book_isbn])
            result = self.current_user.reserve_book(book_isbn)  # Pass the ISBN
            if result == "Book successfully reserved.":
                messagebox.showinfo("Success", "The book has been successfully reserved.")
            elif result == "Added to Waitlist":
                messagebox.showinfo("Waitlist", "The book is unavailable. You have been added to the waitlist.")
            else:
                messagebox.showerror("Error", result)

            # Refresh availability dynamically
            updated_availability = self.controller._cursor.execute(query, (book_isbn,)).fetchone()[0]
            availability_label.config(text=f"Availability: {'Available' if updated_availability == True else 'Reserved'}")

        tk.Button(
            details_frame,
            text="Reserve Book",
            command=reserve_book,
            font=("Arial", 12),
            bg="green",
            fg="white"
        ).pack(anchor="w", pady=10)
        

        def add_readingList():
            print([book_isbn])
            result= self.current_user.make_reading_list(book_isbn)  # Pass the ISBN
            if result:
                messagebox.showinfo("Success", "The book has been successfully added to reading list.")

        tk.Button(
            details_frame,
            text="Add Reading List",
            command= add_readingList,
            font=("Arial", 12),
            bg="green",
            fg="white"
        ).pack(anchor="w", pady=10)

    





    
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

        # Treeview widget'ı oluştur ve `self.tree` olarak kaydet
        columns = ("Title", "Author", "Genre")  # ISBN kaldırıldı
        self.tree = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=10)
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Genre", text="Genre")


        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar ekleme ve Treeview'e bağlama
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
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
                    self.tree.insert("", "end", values=(book[1], book[2], book[4]), tags=(book[0],))  # ISBN saklanıyor

                # Seçim olayını bağlama
                def on_item_select(event):
                    selected_item = self.tree.focus()  # Seçilen öğenin ID'sini al
                    item_values = self.tree.item(selected_item, "values")  # Seçilen öğenin görünen değerlerini al
                    book_isbn = self.tree.item(selected_item, "tags")[0]  # ISBN'i tags'den alıyoruz

                    if item_values:  # Eğer geçerli bir seçim varsa
                        self.show_book_details(item_values, book_isbn)  # Detay penceresini açarken ISBN'i de geçiriyoruz


                self.tree.bind("<<TreeviewSelect>>", on_item_select)

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
