import tkinter 
from tkinter import messagebox
import re
import sqlite3
from home import main_exe

file_1 = "amazon_vfl_reviews.csv"

def login_screen():
    win = tk.Tk()
    win.title("Login - Amazon Review Sentiment App")
    win.state('zoomed')
    win.configure(bg="#ffe6f0")

    form_frame = tk.Frame(win, bg="white", bd=3, relief="solid", padx=20, pady=20)
    form_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(form_frame, text="Login", font=("Arial", 30, "bold"), bg="white", fg="black").pack(pady=20)

    tk.Label(form_frame, text="Username", font=("Arial", 14), bg="white").pack()
    username_entry = tk.Entry(form_frame, font=("Arial", 12), width=40)
    username_entry.pack(pady=10)

    tk.Label(form_frame, text="Password", font=("Arial", 14), bg="white").pack()
    password_entry = tk.Entry(form_frame, show="*", font=("Arial", 12), width=40)
    password_entry.pack(pady=10)


    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Error", "Please fill in all fields.")
            return

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()

            if result and result[0] == password:
                messagebox.showinfo("Login Success", f"Welcome back, {username}!")
                win.destroy()
                main_exe(file_1)

            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

        except Exception as e:
            messagebox.showerror("Database Error", str(e))


    tk.Button(form_frame, text="Login", command=login, bg="blue", fg="white",
              font=("Arial", 14), width=20).pack(pady=20)


    tk.Button(form_frame, text="New user? Register here", command=lambda: [win.destroy(), register_screen()],
              bg="white", fg="blue", bd=0, font=("Arial", 10, "underline")).pack()

    win.mainloop()


def register_screen():
    win = tk.Tk()
    win.title("Register - Amazon Review Sentiment App")
    win.state('zoomed')
    win.configure(bg="#ffe6f0")


    form_frame = tk.Frame(win, bg="white", bd=3, relief="solid", padx=20, pady=20)
    form_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(form_frame, text="Register", font=("Arial", 30, "bold"), bg="white", fg="black").pack(pady=20)


    tk.Label(form_frame, text="Username", font=("Arial", 14), bg="white").pack()
    username_entry = tk.Entry(form_frame, font=("Arial", 12), width=40)
    username_entry.pack(pady=10)


    tk.Label(form_frame, text="Email", font=("Arial", 14), bg="white").pack()
    email_entry = tk.Entry(form_frame, font=("Arial", 12), width=40)
    email_entry.pack(pady=10)


    tk.Label(form_frame, text="Password", font=("Arial", 14), bg="white").pack()
    password_entry = tk.Entry(form_frame, show="*", font=("Arial", 12), width=40)
    password_entry.pack(pady=10)

    # Confirm Password Entry
    tk.Label(form_frame, text="Confirm Password", font=("Arial", 14), bg="white").pack()
    confirm_password_entry = tk.Entry(form_frame, show="*", font=("Arial", 12), width=40)
    confirm_password_entry.pack(pady=10)


    def register():
        username = username_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        confirm_password = confirm_password_entry.get().strip()


        if not username or not email or not password or not confirm_password:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Email Error", "Invalid email format.")
            return

        if password != confirm_password:
            messagebox.showerror("Password Error", "Passwords do not match.")
            return

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()


            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
            """)


            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                messagebox.showerror("Registration Error", "Username already exists!")
                conn.close()
                return


            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, password))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Account created for {username}!")
            win.destroy()
            login_screen()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))


    tk.Button(form_frame, text="Register", command=register, bg="blue", fg="white",
              font=("Arial", 14), width=20).pack(pady=20)


    tk.Button(form_frame, text="Already have an account? Login", command=lambda: [win.destroy(), login_screen()],
              bg="white", fg="blue", bd=0, font=("Arial", 10, "underline")).pack()

    win.mainloop()
register_screen()
