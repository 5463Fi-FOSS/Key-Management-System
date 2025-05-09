import os
import sqlite3
import json
from datetime import datetime
import time
import glob
import hashlib
import keyring
from Crypto.Cipher import AES
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

def backup_database_in_memory(source_db):
    with open(source_db, "rb") as f:
        data = f.read()
    return data

def encrypt_backup_data(data, key):
    """
    |Study
    Encrypts the data using AES-GCM (compression must be added and much more things).
    """
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce, tag, ciphertext

def write_encrypted_backup_file(outfile, nonce, tag, ciphertext):
    """
    Writes the encrypted backup to a file - nonce, tag and ciphertext are saved one after the other.
    """
    with open(f"backup/{outfile}", "wb") as f:
        f.write(nonce)
        f.write(tag)
        f.write(ciphertext)

    backup_path = keyring.get_password("KMS", "backup-path")
    if not backup_path:
        return
    
     # Ensure that the destination folder exists
    os.makedirs(backup_path, exist_ok=True)
    file_path = os.path.join(backup_path, outfile)
    
    with open(file_path, "wb") as f:
        f.write(nonce)
        f.write(tag)
        f.write(ciphertext)
    print(f"Backup dafed under: {file_path}")

def get_encryption_key(root):
    key_str = keyring.get_password("KMS", "backup-key")
    if key_str is None:
        key_str = simpledialog.askstring(
            "Encryption Key",
            "No key found. Please enter your backup key (at least 16 characters):",
            parent=root,
            show="*"
        )
        if not key_str or len(key_str) < 16:
            messagebox.showerror("ERROR”, ”The key entered is invalid or too short.")
            root.destroy()
            exit(1)
        keyring.set_password("KMS", "backup-key", key_str)
    # With SHA-256 the key is set to the required length (32 bytes).
    key = hashlib.sha256(key_str.encode()).digest()
    return key



class KeyManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Key Management System")
        self.root.geometry("900x600")
        db_path = "data/keys_dummy.db"

        self.root.after(100, self.perform_backup, db_path)

        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()
        
        self.create_menu()
        self.create_tabs()
    
    def perform_backup(self, db_path):
        """
        Führt den gesamten Backup-Vorgang aus:
          - Abfrage bzw. Erfassung des Schlüssels (über keyring oder Dialog)
          - Erstellung des SQL-Dumps
          - Verschlüsselung des Dumps
          - Speicherung des verschlüsselten Backups in einer Datei
        """
        today = time.strftime('%Y%m%d')

        if not glob.glob(f'backup/backup_{today}*.db.enc'):
            key = get_encryption_key(self.root)
            backup_data = backup_database_in_memory(db_path)
            nonce, tag, ciphertext = encrypt_backup_data(backup_data, key)
            backup_filename = f"backup_{time.strftime('%Y%m%d_%H%M%S')}.db.enc"
            write_encrypted_backup_file(backup_filename, nonce, tag, ciphertext)
            messagebox.showinfo("Backup", f"Verschlüsseltes Backup erstellt:\n{backup_filename}")
        
    def only_numbers(self, P):        
        if P == "":
            return True
        if P == ".":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Backup_path Settings", command=self.backup_settings_window)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        add_menu = tk.Menu(menubar, tearoff=0)
        add_menu.add_command(label="Add Member", command=self.add_member_window)
        add_menu.add_command(label="Add Key", command=self.add_key_window)
        add_menu.add_command(label="Verify Key", command=self.add_verify_key_window)
        menubar.add_cascade(label="Add", menu=add_menu)
        
        exit_menu = tk.Menu(menubar, tearoff=0)
        exit_menu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="Exit", menu=exit_menu)


    def backup_settings_window(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Backup Einstellungen")
        settings_win.geometry("400x350")

        current_path = keyring.get_password("KMS", "backup-path")
        if not current_path:
            current_path = "Kein Pfad gesetzt"

        label_current = tk.Label(settings_win, text="Please select an Cloud loccation for an extra ofsite Backup", font=("Arial", 12))
        label_current.pack(pady=10)
        label_current = tk.Label(settings_win, text=f"Current Backup-Path:\n{current_path}", font=("Arial", 12))
        label_current.pack(pady=10)

        def set_new_backup_path():
            new_path = filedialog.askdirectory(title="Wähle den neuen Backup-Ordner")
            if new_path:
                keyring.set_password("KMS", "backup-path", new_path)
                label_current.config(text=f"Aktueller Backup-Pfad:\n{new_path}")
                messagebox.showinfo("Backup Settings", f"Backup Pfad gespeichert:\n{new_path}")

       
        btn_set_new = tk.Button(settings_win, text="Neuen Backup-Pfad setzen", command=set_new_backup_path)
        btn_set_new.pack(pady=10)

    def add_member_window(self):
        window = tk.Toplevel(self.root)
        window.title("Add Member")

        tk.Label(window, text="Member ID:").pack()
        member_id_entry = tk.Entry(window)
        member_id_entry.pack()

        tk.Label(window, text="First Name:").pack()
        first_name_entry = tk.Entry(window)
        first_name_entry.pack()
        
        tk.Label(window, text="Last Name:").pack()
        last_name_entry = tk.Entry(window)
        last_name_entry.pack()
        
        tk.Label(window, text="Role:").pack()
        role_entry = tk.Entry(window)
        role_entry.pack()
        
        def add_member():
            member_id = member_id_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            role = role_entry.get()
            if not first_name or not last_name or not role:
                messagebox.showerror("Error", "All fields are required!")
                return
            self.cursor.execute("INSERT INTO members (member_id, first_name, last_name, role) VALUES (?, ?, ?, ?)",
                                (member_id, first_name, last_name, role))
            self.conn.commit()
            member_id_entry.delete(0, tk.END)
            first_name_entry.delete(0, tk.END)
            last_name_entry.delete(0, tk.END)
            role_entry.delete(0, tk.END)
            self.load_keys()
            self.load_free_keys()
            self.load_member_loans()
            messagebox.showinfo("Success", "Member added successfully!")
        
        tk.Button(window, text="Add Member", command=add_member).pack()
    
    def add_key_window(self):
        window = tk.Toplevel(self.root)
        window.title("Add Key")

        tk.Label(window, text="Key Type:").pack()
        key_type_entry = tk.Entry(window)
        key_type_entry.pack()

        tk.Label(window, text="Key Number:").pack()
        key_number_entry = tk.Entry(window)
        key_number_entry.pack()
        
        tk.Label(window, text="UID:").pack()
        uid_entry = tk.Entry(window)
        uid_entry.pack()

        tk.Label(window, text="Transponder Number:").pack()
        transponder_numbe_entry = tk.Entry(window)
        transponder_numbe_entry.pack()
        
        tk.Label(window, text="Access Area:").pack()
        access_area_entry = tk.Entry(window)
        access_area_entry.pack()

        tk.Label(window, text="Programmed By:").pack()
        programmed_by_entry = tk.Entry(window)
        programmed_by_entry.pack()

        tk.Label(window, text="Programmed At:").pack()
        programmed_at_entry = tk.Entry(window)
        programmed_at_entry.insert(0, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        programmed_at_entry.pack()
        
        def add_key():
            key_type = key_type_entry.get()
            key_number = key_number_entry.get()
            uid = uid_entry.get()
            transponder_number = transponder_numbe_entry.get()
            access_area = access_area_entry.get()
            programmed_by = programmed_by_entry.get()
            programmed_at = programmed_at_entry.get()
            if not key_type or not access_area:
                messagebox.showerror("Error", "All fields are required!")
                return
            self.cursor.execute("INSERT INTO keys (key_type, key_number, uid, transponder_number, access_area, programmed_by, programmed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (key_type, key_number, uid, transponder_number, access_area, programmed_by, programmed_at))
            self.conn.commit()
            key_type_entry.delete(0, tk.END)
            key_number_entry.delete(0, tk.END)
            uid_entry.delete(0, tk.END)
            transponder_numbe_entry.delete(0, tk.END)
            access_area_entry.delete(0, tk.END)
            programmed_by_entry.delete(0, tk.END)
            programmed_at_entry.delete(0, tk.END)
            self.load_keys()
            self.load_free_keys()
            self.load_member_loans()
            messagebox.showinfo("Success", "Key added successfully!")
        
        tk.Button(window, text="Add Key", command=add_key).pack()
    
    def add_verify_key_window(self):
        window = tk.Toplevel(self.root)
        window.title("Verify Key")
        window.geometry("300x350")  # Optional: Größe des Fensters festlegen

        tk.Label(window, text="Key ID:").pack(pady=5)
        key_id_verify_entry = tk.Entry(window)
        key_id_verify_entry.pack(pady=5)

        tk.Label(window, text="Verifier ID:").pack(pady=5)
        verifier_id_entry = tk.Entry(window)
        verifier_id_entry.pack(pady=5)

        tk.Label(window, text="Verified At:").pack(pady=5)
        verified_at_entry = tk.Entry(window)
        verified_at_entry.insert(0, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        verified_at_entry.pack(pady=5)

        tk.Label(window, text="Remark").pack(pady=5)
        remark_entry = tk.Entry(window)
        remark_entry.pack(pady=5)

        verify_button = tk.Button(window, text="Verify Key", command=lambda: self.verify_key(key_id_verify_entry.get(), verifier_id_entry.get(), verified_at_entry.get(), remark_entry.get()))
        verify_button.pack(pady=10)

        def verify_key(self):
            key_id = self.key_id_verify_entry.get()
            verifier_id = self.verifier_id_entry.get()
            verified_at = self.verified_at_entry.get()
            remark = self.remark_entry.get()

    
            if not key_id or not verifier_id:
                messagebox.showerror("Input Error", "Key ID and Verifier ID are required.")
                return
    
            try:
                self.cursor.execute("SELECT * FROM keys WHERE key_id = ?", (key_id,))
                key = self.cursor.fetchone()
                if not key:
                    messagebox.showerror("Error", "Key ID not found.")
                    return
    
                self.cursor.execute("INSERT INTO key_verifications (key_id, verified_by, verified_at, remark) "
                                    "VALUES (?, ?, ?, ?)", 
                                    (key_id, verifier_id, verified_at, remark))
                self.conn.commit()
                
                self.load_keys()
                self.load_free_keys()
                self.load_member_loans()
                messagebox.showinfo("Success", f"Key {key_id} verified by Member {verifier_id}.")
    
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
#TABS#    

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.create_key_overview_tab()
        self.create_free_keys_tab()
        self.create_member_tab()

        self.create_key_assignment_tab()
        self.create_key_return_tab()
    
    def create_key_overview_tab(self):
        self.overview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_tab, text="All Keys")

        columns = [
            ("Key ID", 40), ("Member ID", 60), ("First Name", 100), ("Last Name", 100), ("Role", 80),
            ("Assigned At", 85), ("Loaned By", 80), ("Deposit", 70), ("Remark", 150),
            ("Key Type", 80), ("Key Number", 120), ("UID", 120), ("Transponder Number", 120),
            ("Access Area", 100), ("Programmed By", 90), ("Programmed At", 85)
        ]

        column_names = [col[0] for col in columns]
        self.tree = ttk.Treeview(self.overview_tab, columns=column_names, show="headings")

        for col_name, width in columns:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=width, anchor="center")

        tree_scroll_y = ttk.Scrollbar(self.overview_tab, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.overview_tab, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=tree_scroll_y.set)
        self.tree.configure(xscrollcommand=tree_scroll_x.set)


        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")

        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure('odd', background='#f2f2f2')
        self.tree.tag_configure('even', background='#fdfdfd')

        self.add_tooltip_on_hover(self.tree)
        self.load_keys()

    def load_keys(self):
        self.tree.delete(*self.tree.get_children())

        query = """
        SELECT k.key_id, m.member_id, m.first_name, m.last_name, m.role, 
               ka.assigned_at, ka.loaned_by, ka.deposit, ka.remark, 
               k.key_type, k.key_number, k.uid, k.transponder_number, 
               k.access_area, k.programmed_by, k.programmed_at
        FROM keys k
        LEFT JOIN key_assignments ka ON k.key_id = ka.key_id
        LEFT JOIN members m ON ka.member_id = m.member_id
        """

        self.cursor.execute(query)
        

        for i, row in enumerate(self.cursor.fetchall()):
            tag = 'odd' if i % 2 == 0 else 'even' 
            key_number = row[10]
            try:
                key_number_list = json.loads(key_number) if key_number else []
                key_number_string = " ".join(key_number_list)
            except json.JSONDecodeError:
                key_number_string = ""

            row = list(row)
            row[10] = key_number_string
            row = [value if value is not None else "" for value in row]
            self.tree.insert("", "end", values=row, tags=(tag,))
    
    def create_free_keys_tab(self):
        self.loaned_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.loaned_tab, text="Free Keys")

        tree_scroll_y = ttk.Scrollbar(self.loaned_tab, orient="vertical")
        tree_scroll_x = ttk.Scrollbar(self.loaned_tab, orient="horizontal")

        # Treeview erstellen
        columns = [
            ("Key ID", 40), ("Type", 100), ("Key Nr.", 80), ("UID", 100),
            ("Transp. Nr.", 100), ("Access", 90),
            ("Prog. By", 55), ("Prog. At", 85)
        ]
        
        self.loaned_tree = ttk.Treeview(
            self.loaned_tab,
            columns=[col[0] for col in columns],
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )

        # Scrollbars mit Treeview verbinden
        tree_scroll_y.config(command=self.loaned_tree.yview)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.config(command=self.loaned_tree.xview)
        tree_scroll_x.pack(side="bottom", fill="x")

        # Spaltenüberschriften und Spaltenbreiten einstellen
        for col, width in columns:
            self.loaned_tree.heading(col, text=col)
            if col in ["Key ID", "Prog. By", "Prog. At", "Member"]:
                self.loaned_tree.column(col, width=width, anchor="center", stretch=False)
            else:
                self.loaned_tree.column(col, width=width, stretch=True)

        self.loaned_tree.tag_configure('odd', background='#f2f2f2')
        self.loaned_tree.tag_configure('even', background='#fdfdfd')

        self.loaned_tree.pack(fill="both", expand=True)

        self.loaned_tree.bind("<ButtonRelease-3>", self.on_free_key_select)

        self.add_tooltip_on_hover(self.loaned_tree)
        self.load_free_keys()

    def load_free_keys(self):
        for item in self.loaned_tree.get_children():
            self.loaned_tree.delete(item)
        
        self.cursor.execute("""
            SELECT key_id, key_type, key_number, uid, transponder_number, access_area, programmed_by, programmed_at
            FROM keys
            WHERE key_id NOT IN (SELECT key_id FROM key_assignments)
        """)
        keys = self.cursor.fetchall()

        for i, key in enumerate(keys):
            tag = 'odd' if i % 2 == 0 else 'even'
            key_number = key[2]
            try:
                key_number_list = json.loads(key_number) if key_number else []
                key_number_string = " ".join(key_number_list)
            except json.JSONDecodeError:
                key_number_string = ""

            key = list(key)
            key[2] = key_number_string
            key = [value if value is not None else "" for value in key]
            self.loaned_tree.insert("", "end", values=key, tags=(tag,))



    def add_tooltip_on_hover(self, treeview):
        """Fügt Tooltips hinzu, um abgeschnittenen Text anzuzeigen, wenn man mit der Maus darüber fährt."""
        def on_hover(event):
            # Identifiziere das Element (Zeile und Spalte)
            item_id = treeview.identify('item', event.x, event.y)
            column = treeview.identify('column', event.x, event.y)

            # Falls ein Item gefunden wurde, den Text aus der Zelle holen und den Tooltip anzeigen
            if item_id:
                # Spalte als Index für die entsprechenden Werte verwenden
                column_index = int(column.replace('#', '')) - 1  # weil Spalten 1-basiert sind
                text = treeview.item(item_id)["values"][column_index]
                self.show_tooltip(event, text)

        def on_leave(event):
            # Tooltip ausblenden
            self.hide_tooltip()

        # Tooltip Label erstellen
        self.tooltip = tk.Label(self.root, text="", background="lightgrey", relief="solid", bd=1, padx=5, pady=2)
        self.tooltip.place_forget()

        # Hover-Ereignisse hinzufügen
        treeview.bind("<Motion>", on_hover)
        treeview.bind("<Leave>", on_leave)

    def show_tooltip(self, event, text):
        """Zeigt den Tooltip an, wenn der Benutzer mit der Maus über eine Zelle fährt."""
        self.tooltip.config(text=text)

        # Position des Tooltips berechnen
        x = event.x_root + 10
        y = event.y_root + 10

        # Überprüfen, ob genug Platz auf der rechten Seite des Mauszeigers ist
        if x + self.tooltip.winfo_width() > self.root.winfo_width():
            # Wenn kein Platz rechts, Tooltip nach links verschieben
            x = event.x_root - self.tooltip.winfo_width() - 10

        self.tooltip.place(x=x, y=y)

    def hide_tooltip(self):
        """Versteckt den Tooltip, wenn der Benutzer den Bereich verlässt."""
        self.tooltip.place_forget()

    
    def create_member_tab(self):
        self.member_loans_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.member_loans_tab, text="Members")

        tree_frame = ttk.Frame(self.member_loans_tab)
        tree_frame.pack(fill="both", expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")

        self.member_loans_tree = ttk.Treeview(
            tree_frame, 
            columns=("Member ID", "First Name", "Last Name", "Role", "Key ID", "Key Type"), 
            show="headings", 
            yscrollcommand=tree_scroll.set  
        )

       
        tree_scroll.config(command=self.member_loans_tree.yview)
        tree_scroll.pack(side="right", fill="y")  

        self.member_loans_tree.heading("Member ID", text="Member ID")
        self.member_loans_tree.heading("First Name", text="First Name")
        self.member_loans_tree.heading("Last Name", text="Last Name")
        self.member_loans_tree.heading("Role", text="Role")
        self.member_loans_tree.heading("Key ID", text="Key ID")
        self.member_loans_tree.heading("Key Type", text="Key Type")


        column_settings = {
            "Member ID": 80,
            "First Name": 100,
            "Last Name": 150,
            "Role": 100,
            "Key ID": 80,
            "Key Type": 150
        }

        for col, width in column_settings.items():
            self.member_loans_tree.heading(col, text=col)
            self.member_loans_tree.column(col, width=width, anchor="center", stretch=True)

        self.member_loans_tree.pack(fill="both", expand=True)

        self.member_loans_tree.bind("<Double-Button-1>", self.show_keys_window)
        self.member_loans_tree.bind("<ButtonRelease-3>", self.on_row_click)
        
        self.load_member_loans()

    def load_member_loans(self):
        self.member_loans_tree.delete(*self.member_loans_tree.get_children())

        self.cursor.execute("SELECT member_id, first_name, last_name, role FROM members")
        members = self.cursor.fetchall()

        row_color = False  

        for member in members:
            member_id, first_name, last_name, role = member

            row_tag = 'even_row' if row_color else 'odd_row'
            member_tag = member_id
            self.member_loans_tree.insert("", "end", values=(member_id, first_name, last_name, role), tags=(row_tag,member_tag))

            self.cursor.execute("""
                SELECT ka.key_id, k.key_type
                FROM key_assignments ka
                JOIN keys k ON ka.key_id = k.key_id
                WHERE ka.member_id = ?
            """, (member_id,))
            keys = self.cursor.fetchall()

            for key in keys:
                key_id, key_type = key
                self.member_loans_tree.insert("", "end", values=("", "", "", "", key_id, key_type), tags=(row_tag,member_tag))

            row_color = not row_color

        self.member_loans_tree.tag_configure('even_row', background='#f2f2f2') 
        self.member_loans_tree.tag_configure('odd_row', background='#fdfdfd')   

    def on_row_click(self, event):
        item = self.member_loans_tree.selection()
        if item:

            values = self.member_loans_tree.item(item, "values")
            tags = self.member_loans_tree.item(item, "tags")
            if len(values) > 5 and values[4] and values[5]:
                key_id = values[4]  
                key_type = values[5]  
                member_tag = tags[1] 
                member_id = int(member_tag)

                self.fill_return_fields(member_id, key_id)  
                self.notebook.select(self.return_tab)  

    def fill_return_fields(self, member_id, key_id):
        self.member_id_return_entry.delete(0, "end")  
        self.member_id_return_entry.insert(0, member_id)  

        self.key_id_return_entry.delete(0, "end")  
        self.key_id_return_entry.insert(0, key_id) 

    def on_free_key_select(self, event):
        item = self.loaned_tree.selection()
        if not item:
            return

        values = self.loaned_tree.item(item, "values")
        if len(values) > 0 and values[0]: 
            key_id = values[0]

            self.key_id_entry.delete(0, "end")
            self.key_id_entry.insert(0, key_id)

            self.notebook.select(self.assignment_tab)

    def show_keys_window(self, event):
        selected_item = self.member_loans_tree.selection()
        if not selected_item:
            return  
        values = self.member_loans_tree.item(selected_item, "values")

        if len(values) < 5 or not values[4]: 
            return
        key_id = values[4]  

        window = tk.Toplevel(self.root)
        window.title(f"Key Details - ID {key_id}")
        window.geometry("950x300")

        table_frame = ttk.Frame(window)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree_scroll = ttk.Scrollbar(table_frame, orient="vertical")

        columns = [
            ("Key ID", 40), ("Member", 55), ("Type", 80), ("Int. Nr.", 70), ("UID", 90),
            ("Transp. Nr.", 90), ("Key Nr.", 50), ("Access", 90),
            ("Prog. By", 55), ("Prog. At", 85)
        ]

        self.keys_tree = ttk.Treeview(table_frame, columns=[col[0] for col in columns], show="headings", yscrollcommand=tree_scroll.set)

        tree_scroll.config(command=self.keys_tree.yview)
        tree_scroll.pack(side="right", fill="y")

        for col, width in columns:
            self.keys_tree.heading(col, text=col)
            
            if col in ["Key ID", "Prog. By", "Prog. At", "Member"]:
                self.keys_tree.column(col, width=width, anchor="center", stretch=False) 
            else:
                self.keys_tree.column(col, width=width, stretch=True)

        self.keys_tree.pack(fill="both", expand=True)

        self.cursor.execute("""
            SELECT k.key_id, ka.member_id, k.key_type, k.internal_number, k.uid, k.transponder_number, 
                   k.key_number, k.access_area, k.programmed_by, k.programmed_at
            FROM keys k
            LEFT JOIN key_assignments ka ON k.key_id = ka.key_id
            WHERE k.key_id = ?
        """, (key_id,))

        row = self.cursor.fetchone() 

        if row:
            key_id, member_id, key_type, internal_number, uid, transponder_number, key_number, access_area, programmed_by, programmed_at = row

            try:
                access_area_list = json.loads(access_area) if access_area else []
            except json.JSONDecodeError:
                access_area_list = []  

            try:
                internal_number_list = json.loads(internal_number) if internal_number else []
                internal_number_string = " ".join(internal_number_list)
            except json.JSONDecodeError:
                internal_number_string = ""



            # Füge nur einmal die vollständigen Informationen in die erste Zeile ein
            first_row = (key_id, member_id, key_type, internal_number_string, uid, transponder_number, key_number, access_area_list[0] if access_area_list else '', programmed_by, programmed_at)
            first_row = [value if value is not None else "" for value in first_row]
            self.keys_tree.insert("", "end", values=first_row)

          
            for area in access_area_list[1:]: 
                self.keys_tree.insert("", "end", values=("","", "", "", "", "", "", area, "", "")) 

    def create_key_assignment_tab(self):
        vcmd = (self.root.register(self.only_numbers), "%P")
        self.assignment_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.assignment_tab, text="Assign Key")

        # UI Elements for Key Assignment
        self.key_id_label = ttk.Label(self.assignment_tab, text="Key ID:")
        self.key_id_label.grid(row=0, column=0, padx=5, pady=5)
        self.key_id_entry = ttk.Entry(self.assignment_tab)
        self.key_id_entry.grid(row=0, column=1, padx=5, pady=5)

        self.member_id_label = ttk.Label(self.assignment_tab, text="Member ID:")
        self.member_id_label.grid(row=1, column=0, padx=5, pady=5)
        self.member_id_entry = ttk.Entry(self.assignment_tab)
        self.member_id_entry.grid(row=1, column=1, padx=5, pady=5)

        self.assigned_at_label = ttk.Label(self.assignment_tab, text="Assigned At (now)")
        self.assigned_at_label.grid(row=2, column=0, padx=5, pady=5)
        self.assigned_at_entry = ttk.Entry(self.assignment_tab)
        self.assigned_at_entry.insert(0, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.assigned_at_entry.grid(row=2, column=1, padx=5, pady=5)

        self.loaned_by_label = ttk.Label(self.assignment_tab, text="Loaned By (Member ID):")
        self.loaned_by_label.grid(row=3, column=0, padx=5, pady=5)
        self.loaned_by_create_entry = ttk.Entry(self.assignment_tab)
        self.loaned_by_create_entry.grid(row=3, column=1, padx=5, pady=5)

        self.deposit_in_label = ttk.Label(self.assignment_tab, text="Deposit Amount:")
        self.deposit_in_label.grid(row=4, column=0, padx=5, pady=5)
        self.deposit_in_entry = ttk.Entry(self.assignment_tab, validate="key", validatecommand=vcmd)
        self.deposit_in_entry.insert(0, "0")
        self.deposit_in_entry.grid(row=4, column=1, padx=5, pady=5)

        self.remark_label = ttk.Label(self.assignment_tab, text="Remark:")
        self.remark_label.grid(row=5, column=0, padx=5, pady=5)
        self.remark_entry = ttk.Entry(self.assignment_tab)
        self.remark_entry.insert(0, "Ausgeliehen an ein Mitglied")
        self.remark_entry.grid(row=5, column=1, padx=5, pady=5)

        self.assign_button = ttk.Button(self.assignment_tab, text="Assign Key", command=self.assign_key)
        self.assign_button.grid(row=6, columnspan=2, pady=10)

    def create_key_return_tab(self):
        vcmd = (self.root.register(self.only_numbers), "%P")
        self.return_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.return_tab, text="Return Key")

        # UI Elements for Key Return
        self.key_id_return_label = ttk.Label(self.return_tab, text="Key ID:")
        self.key_id_return_label.grid(row=0, column=0, padx=5, pady=5)
        self.key_id_return_entry = ttk.Entry(self.return_tab)
        self.key_id_return_entry.grid(row=0, column=1, padx=5, pady=5)

        self.member_id_return_label = ttk.Label(self.return_tab, text="Member ID:")
        self.member_id_return_label.grid(row=1, column=0, padx=5, pady=5)
        self.member_id_return_entry = ttk.Entry(self.return_tab)
        self.member_id_return_entry.grid(row=1, column=1, padx=5, pady=5)

        self.assigned_at_label = ttk.Label(self.return_tab, text="Returned At (now)")
        self.assigned_at_label.grid(row=2, column=0, padx=5, pady=5)
        self.assigned_at_entry = ttk.Entry(self.return_tab)
        self.assigned_at_entry.insert(0, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.assigned_at_entry.grid(row=2, column=1, padx=5, pady=5)

        self.loaned_by_label = ttk.Label(self.return_tab, text="Returned By (Member ID):")
        self.loaned_by_label.grid(row=3, column=0, padx=5, pady=5)
        self.loaned_by_entry = ttk.Entry(self.return_tab)
        self.loaned_by_entry.grid(row=3, column=1, padx=5, pady=5)

        self.deposit_out_label = ttk.Label(self.return_tab, text="Deposit Amount:")
        self.deposit_out_label.grid(row=4, column=0, padx=5, pady=5)
        self.deposit_out_entry = ttk.Entry(self.return_tab, validate="key", validatecommand=vcmd)
        self.deposit_out_entry.insert(0, "0")
        self.deposit_out_entry.grid(row=4, column=1, padx=5, pady=5)

        self.return_reason_label = ttk.Label(self.return_tab, text="Return Reason:")
        self.return_reason_label.grid(row=5, column=0, padx=5, pady=5)
        self.return_reason_entry = ttk.Entry(self.return_tab)
        self.return_reason_entry.insert(0, "Ausgetretten")
        self.return_reason_entry.grid(row=5, column=1, padx=5, pady=5)

        self.return_button = ttk.Button(self.return_tab, text="Return Key", command=self.return_key)
        self.return_button.grid(row=6, columnspan=2, pady=10)



    def assign_key(self):
        key_id = self.key_id_entry.get()
        member_id = self.member_id_entry.get()
        assigned_at = self.assigned_at_entry.get()
        loaned_by = self.loaned_by_create_entry.get()
        deposit = self.deposit_in_entry.get()
        remark = self.remark_entry.get()

        if not key_id or not member_id or not loaned_by:
            messagebox.showerror("Input Error", "Key ID, Member ID, and Loaned By are required.")
            return

        try:
            # Check if key exists
            self.cursor.execute("SELECT * FROM keys WHERE key_id = ?", (key_id,))
            key = self.cursor.fetchone()
            if not key:
                messagebox.showerror("Error", "Key ID not found.")
                return

            self.cursor.execute("SELECT first_name, last_name FROM members WHERE member_id = ?", (member_id,))
            member = self.cursor.fetchone()
            if not member:
                messagebox.showerror("Error", "Member ID not found.")
                return
            
            member_first_name, member_last_name = member

            self.cursor.execute("INSERT INTO key_assignments (key_id, member_id, assigned_at, loaned_by, deposit, remark) "
                                "VALUES (?, ?, ?, ?, ?, ?)", 
                                (key_id, member_id, assigned_at, loaned_by, deposit, remark))
            self.conn.commit()
            
            self.cursor.execute("INSERT INTO accounting (member_first_name, member_last_name, key_id, amount, entry_type, remark) "
                            "VALUES (?, ?, ?, ?, ?, ?)", 
                            (member_first_name, member_last_name, key_id, deposit, 'deposit', remark))
            self.conn.commit()

            self.load_keys()
            self.load_free_keys()
            self.load_member_loans()

            messagebox.showinfo("Success", f"Key {key_id} assigned to Member {member_id}.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def return_key(self):
        key_id = self.key_id_return_entry.get().strip()
        member_id = self.member_id_return_entry.get() 
        returned_at = self.assigned_at_entry.get() 
        returned_by = self.loaned_by_entry.get() 
        deposit = self.deposit_out_entry.get() 
        return_reason = self.return_reason_entry.get()

        if not key_id:
            messagebox.showerror("Input Error", "Key ID is required.")
            return
            
        if not returned_by:
            messagebox.showerror("Input Error", "Returned by is required.")
            return

        try:
            # Prüfe, ob der Schlüssel überhaupt existiert
            self.cursor.execute("SELECT * FROM keys WHERE key_id = ?", (key_id,))
            key = self.cursor.fetchone()
            if not key:
                messagebox.showerror("Error", "Key ID not found.")
                return

            # Hole den zugehörigen Verleih-Datensatz aus key_assignments (der aktive Verleih)
            self.cursor.execute("SELECT * FROM key_assignments WHERE key_id = ?", (key_id,))
            assignment = self.cursor.fetchone()
            if assignment is None:
                messagebox.showerror("Error", "No active assignment found for this key.")
                return

            # Annahme: key_assignments hat folgende Struktur:
            # (key_id, member_id, assigned_at, loaned_by, deposit, remark)
            (key_id, member_id, assigned_at, loaned_by, deposit, remark) = assignment

            # Starte eine Transaktion, damit beide Operationen atomar erfolgen
            self.conn.execute("BEGIN")

            # Füge in key_returns den übernommenen Datensatz ein.
            # Wir übernehmen hier die Felder aus key_assignments und ergänzen die Rückgabezeit (returned_at) 
            # mit dem aktuellen Zeitpunkt (datetime('now')) und übernehmen returned_by sowie den return_reason.
            self.cursor.execute("""
                INSERT INTO key_returns 
                (key_id, member_id, assigned_at, loaned_by, returned_at, returned_by, return_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (key_id, member_id, assigned_at, loaned_by, returned_at, returned_by, return_reason))

            # Füge zusätzlich einen Eintrag in der Accounting-Tabelle ein, falls der Deposit-Wert erfasst werden soll
            self.cursor.execute("SELECT first_name, last_name FROM members WHERE member_id = ?", (member_id,))
            member = self.cursor.fetchone()
            if not member:
                messagebox.showerror("Error", "Member not found.")
                return
            member_first_name, member_last_name = member

            self.cursor.execute("""
                INSERT INTO accounting 
                (member_first_name, member_last_name, key_id, amount, entry_type, remark)
                VALUES (?, ?, ?, ?, 'refund', ?)
            """, (member_first_name, member_last_name, key_id, deposit,return_reason))

            # Lösche anschließend den Verleih-Datensatz aus key_assignments,
            # weil der Schlüssel jetzt zurückgegeben ist.
            self.cursor.execute("DELETE FROM key_assignments WHERE key_id = ?", (key_id,))

            # Setze die Transaktion fort
            self.conn.commit()

            # Aktualisiere die Ansicht (Schlüssel, freie Schlüssel, Mitgliedsleihen)
            self.load_keys()
            self.load_free_keys()
            self.load_member_loans()

            messagebox.showinfo("Success", f"Key {key_id} returned by Member {member_id}.")

        except Exception as e:
            # Bei einem Fehler rollt die Transaktion zurück, sodass keine Teilschritte übernommen werden
            self.conn.rollback()
            messagebox.showerror("Error", str(e))


    def close(self):
        self.conn.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyManagementApp(root)
    root.mainloop()
