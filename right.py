import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import hashlib

# Database Setup
def connect_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            quantity INTEGER,
            price REAL
        )
    """)

    conn.commit()
    conn.close()

connect_db()

# Authentication
class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.frame = tk.Frame(self.root, padx=20, pady=20, bg="#D3E3FC")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.frame, text="Username", bg="#D3E3FC").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.frame, text="Password", bg="#D3E3FC").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2)
        tk.Button(self.frame, text="Register", command=self.register).grid(row=3, column=0, columnspan=2)

    def login(self):
        username = self.username_entry.get()
        password = hashlib.sha256(self.password_entry.get().encode()).hexdigest()

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.on_success()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    def register(self):
        username = self.username_entry.get()
        password = hashlib.sha256(self.password_entry.get().encode()).hexdigest()

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "User Registered")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()

# Inventory Management
class InventoryWindow:
    def __init__(self, root, logout_callback):
        self.root = root
        self.logout_callback = logout_callback
        self.root.title("Inventory Management")
        self.root.configure(bg="#D3E3FC")

        # Header Frame
        header_frame = tk.Frame(self.root, bg="#D3E3FC")
        header_frame.pack(fill=tk.X, pady=10)
        tk.Label(header_frame, text="Inventory Management", font=("Arial", 16, "bold"), bg="#D3E3FC").pack(side=tk.LEFT, padx=20)
        tk.Button(header_frame, text="Logout", command=self.logout_callback).pack(side=tk.RIGHT, padx=20)

        # Form Frame
        self.frame = tk.Frame(self.root, bg="#D3E3FC")
        self.frame.pack(pady=10)

        tk.Label(self.frame, text="Product Name", bg="#D3E3FC").grid(row=0, column=0)
        self.name_entry = tk.Entry(self.frame)
        self.name_entry.grid(row=0, column=1)

        tk.Label(self.frame, text="Quantity", bg="#D3E3FC").grid(row=1, column=0)
        self.quantity_entry = tk.Entry(self.frame)
        self.quantity_entry.grid(row=1, column=1)

        tk.Label(self.frame, text="Price", bg="#D3E3FC").grid(row=2, column=0)
        self.price_entry = tk.Entry(self.frame)
        self.price_entry.grid(row=2, column=1)

        tk.Button(self.frame, text="Add Product", command=self.add_product).grid(row=3, column=0, columnspan=2)
        tk.Button(self.frame, text="Delete Product", command=self.delete_product).grid(row=4, column=0, columnspan=2)
        tk.Button(self.frame, text="Update Product", command=self.update_product).grid(row=5, column=0, columnspan=2)

        # Table Frame
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.product_list = ttk.Treeview(table_frame, columns=("ID", "Name", "Quantity", "Price"), show="headings")
        self.product_list.heading("ID", text="ID")
        self.product_list.heading("Name", text="Name")
        self.product_list.heading("Quantity", text="Quantity")
        self.product_list.heading("Price", text="Price")

        self.product_list.column("ID", width=50, anchor="center")
        self.product_list.column("Name", width=200, anchor="center")
        self.product_list.column("Quantity", width=100, anchor="center")
        self.product_list.column("Price", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.product_list.yview)
        self.product_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.product_list.pack(fill=tk.BOTH, expand=True)

        self.load_products()

    def load_products(self):
        self.product_list.delete(*self.product_list.get_children())
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()
        for product in products:
            self.product_list.insert("", "end", values=product)

    def add_product(self):
        name = self.name_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()

        if not name or not quantity or not price:
            messagebox.showerror("Error", "All fields are required")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
        conn.commit()
        conn.close()
        self.load_products()

    def delete_product(self):
        selected_item = self.product_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "No product selected")
            return

        item_id = self.product_list.item(selected_item, "values")[0]

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        self.load_products()

    def update_product(self):
        messagebox.showinfo("Feature", "Update feature not implemented yet")

# Main Application
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("900x700")
        self.root.configure(bg="#D3E3FC")
        self.login_window = LoginWindow(self.root, self.show_inventory)

    def show_inventory(self):
        self.clear_window()
        InventoryWindow(self.root, self.logout)

    def logout(self):
        self.clear_window()
        self.login_window = LoginWindow(self.root, self.show_inventory)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
