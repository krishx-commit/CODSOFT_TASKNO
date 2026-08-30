import sqlite3
import customtkinter as ctk
from tkinter import messagebox

# Set up the visual theme and accent color
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ContactBookApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern SQL Contact Book")
        self.geometry("750x500")
        self.resizable(False, False)
        
        # Initialize database and build table if missing
        self.init_db()
        
        self.setup_ui()
        self.refresh_contact_list()

    def init_db(self):
        """Creates the local SQLite database and structured table."""
        self.conn = sqlite3.connect("contacts.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                email TEXT
            )
        """)
        self.conn.commit()

    def setup_ui(self):
        """Creates the grid layout and all UI widgets."""
        # ---------------- Left Frame: Input Form ----------------
        self.form_frame = ctk.CTkFrame(self, width=320, corner_radius=15)
        self.form_frame.pack(side="left", fill="y", padx=20, pady=20)
        self.form_frame.pack_propagate(False)

        title_lbl = ctk.CTkLabel(self.form_frame, text="Contact Details", font=("Helvetica", 20, "bold"))
        title_lbl.pack(pady=(20, 20))

        # Input fields
        self.name_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Full Name", width=260, height=40)
        self.name_entry.pack(pady=10)

        self.phone_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Phone Number", width=260, height=40)
        self.phone_entry.pack(pady=10)

        self.email_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Email Address", width=260, height=40)
        self.email_entry.pack(pady=10)

        # Action Buttons
        self.add_btn = ctk.CTkButton(self.form_frame, text="Save Contact", command=self.save_contact, width=260, height=40, font=("Helvetica", 14, "bold"))
        self.add_btn.pack(pady=(25, 10))

        self.clear_btn = ctk.CTkButton(self.form_frame, text="Clear Form", fg_color="transparent", border_width=1, command=self.clear_form, width=260, height=35)
        self.clear_btn.pack(pady=5)

        # ---------------- Right Frame: View & Search ----------------
        self.view_frame = ctk.CTkFrame(self, corner_radius=15)
        self.view_frame.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        # Search Bar
        self.search_entry = ctk.CTkEntry(self.view_frame, placeholder_text="🔍 Search contacts...", height=35)
        self.search_entry.pack(fill="x", padx=20, pady=(20, 10))
        self.search_entry.bind("<KeyRelease>", self.search_contacts)

        # Scrollable Contact Container
        self.scroll_container = ctk.CTkScrollableFrame(self.view_frame, label_text="Saved Contacts", label_font=("Helvetica", 14, "bold"))
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ---------------- UI Actions & Logic ----------------
    def refresh_contact_list(self, filter_term=""):
        """Clears and rebuilds the scrollable contact view panel using SQL queries."""
        # Wipe existing UI items in the scroll frame
        for widget in self.scroll_container.winfo_children():
            widget.destroy()

        # Fetch contacts filtered by search entry (if any) ordered alphabetically
        if filter_term:
            self.cursor.execute(
                "SELECT name, phone, email FROM contacts WHERE name LIKE ? OR phone LIKE ? ORDER BY name ASC",
                (f"%{filter_term}%", f"%{filter_term}%")
            )
        else:
            self.cursor.execute("SELECT name, phone, email FROM contacts ORDER BY name ASC")
        
        rows = self.cursor.fetchall()

        # Populate visual list rows
        for name, phone, email in rows:
            row = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=5)

            # Label generation
            info_text = f"{name}\n📞 {phone}  |  ✉️ {email if email else 'N/A'}"
            lbl = ctk.CTkLabel(row, text=info_text, justify="left", font=("Helvetica", 12))
            lbl.pack(side="left", padx=5, pady=5)

            # Delete button
            del_btn = ctk.CTkButton(row, text="🗑️", width=35, height=30, fg_color="#C0392B", hover_color="#E74C3C", command=lambda n=name: self.delete_contact(n))
            del_btn.pack(side="right", padx=2)

            # Edit button
            edit_btn = ctk.CTkButton(row, text="✏️", width=35, height=30, fg_color="#2E86C1", hover_color="#3498DB", command=lambda n=name, p=phone, e=email: self.load_to_form(n, p, e))
            edit_btn.pack(side="right", padx=2)

    def save_contact(self):
        """Inserts a new contact or updates an existing record based on the name key."""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name or not phone:
            messagebox.showwarning("Input Error", "Name and Phone Number fields are required.")
            return

        try:
            # UPSERT pattern: Try to insert; if name already exists, update phone and email
            self.cursor.execute("""
                INSERT INTO contacts (name, phone, email) 
                VALUES(?, ?, ?)
                ON CONFLICT(name) 
                DO UPDATE SET phone=excluded.phone, email=excluded.email
            """, (name, phone, email if email else None))
            
            self.conn.commit()
            self.refresh_contact_list()
            self.clear_form()
            messagebox.showinfo("Success", f"Contact '{name}' saved successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save contact: {e}")

    def load_to_form(self, name, phone, email):
        """Populates the text inputs with selected row variables."""
        self.clear_form()
        self.name_entry.insert(0, name)
        self.phone_entry.insert(0, phone)
        if email:
            self.name_entry.configure(state="disabled") # Disable name editing to prevent creating duplicate entries during update
            self.email_entry.insert(0, email)

    def delete_contact(self, name):
        """Deletes selected row permanently from the database table."""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            self.cursor.execute("DELETE FROM contacts WHERE name = ?", (name,))
            self.conn.commit()
            self.refresh_contact_list()
            self.clear_form()

    def search_contacts(self, event):
        """Passes real-time input keywords straight to SQL query filtration blocks."""
        query = self.search_entry.get().lower()
        self.refresh_contact_list(query)

    def clear_form(self):
        """Resets inputs to an empty canvas state."""
        self.name_entry.configure(state="normal")
        self.name_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')

    def __del__(self):
        """Safely shuts down database connections on exit."""
        try:
            self.conn.close()
        except:
            pass

if __name__ == "__main__":
    app = ContactBookApp()
    app.mainloop()
