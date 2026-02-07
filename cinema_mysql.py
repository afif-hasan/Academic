import mysql.connector
from tkinter import *
from tkinter import messagebox, ttk


def get_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",      
            password="root",
            database="cineplex_db"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None


def show_bookings_window():
    # Create a new popup window
    view_win = Toplevel()
    view_win.title("Sales History - All Bookings")
    view_win.geometry("700x400")

    Label(view_win, text="ALL BOOKING RECORDS", font=("Arial", 14, "bold"), pady=10).pack()

    # Create Table
    cols = ("ID", "Customer Name", "Movie Title", "Seats", "Total Paid")
    tree_view = ttk.Treeview(view_win, columns=cols, show="headings")
    
    for col in cols:
        tree_view.heading(col, text=col)
        tree_view.column(col, width=120)
    
    tree_view.pack(pady=10, padx=10, fill=BOTH, expand=True)

    # Fetch data from Database using JOIN
    db = get_db()
    if db:
        cursor = db.cursor()
        # SQL JOIN to get Movie Title instead of just Movie ID
        query = """
            SELECT b.id, b.customer_name, m.title, b.seats_booked, b.total_price 
            FROM bookings b 
            JOIN movies m ON b.movie_id = m.id
            ORDER BY b.id DESC
        """
        cursor.execute(query)
        for row in cursor.fetchall():
            tree_view.insert("", END, values=row)
        db.close()

    Button(view_win, text="Close", command=view_win.destroy, bg="grey", fg="white").pack(pady=10)

# --- FUNCTION: LOGOUT ---
def logout(current_window):
    current_window.destroy()
    show_login_screen()

# --- MAIN DASHBOARD WINDOW ---
def open_booking_window(user_full_name):
    root = Tk()
    root.title("Cineplex Staff Dashboard")
    root.geometry("800x650")

    # Header
    header = Frame(root, bg="#333", pady=10)
    header.pack(fill=X)
    Label(header, text=f"Staff: {user_full_name}", fg="white", bg="#333").pack(side=LEFT, padx=20)
    Button(header, text="Logout", command=lambda: logout(root), bg="red", fg="white").pack(side=RIGHT, padx=20)

    # Internal Logic
    def refresh_data():
        for item in tree.get_children(): tree.delete(item)
        db = get_db()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT id, title, price, available_seats FROM movies")
            for row in cursor.fetchall(): tree.insert("", END, values=row)
            db.close()

    def handle_booking():
        name, m_id, seats = ent_name.get(), ent_mid.get(), ent_seats.get()
        if not (name and m_id and seats):
            messagebox.showwarning("Input Error", "All fields required!")
            return

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT title, price, available_seats FROM movies WHERE id=%s", (m_id,))
        movie = cursor.fetchone()

        if movie and movie[2] >= int(seats):
            total = movie[1] * int(seats)
            cursor.execute("UPDATE movies SET available_seats = available_seats - %s WHERE id = %s", (seats, m_id))
            cursor.execute("INSERT INTO bookings (customer_name, movie_id, seats_booked, total_price) VALUES (%s, %s, %s, %s)",
                           (name, m_id, seats, total))
            db.commit()
            messagebox.showinfo("Success", f"Booked for {name}!\nTotal: ${total}")
            refresh_data()
            ent_name.delete(0, END); ent_mid.delete(0, END); ent_seats.delete(0, END)
        else:
            messagebox.showerror("Error", "Check Movie ID or Seat availability")
        db.close()

    # UI Layout
    Label(root, text="AVAILABLE MOVIES", font=("Arial", 14, "bold")).pack(pady=10)
    columns = ("ID", "Movie Title", "Price", "Available Seats")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=6)
    for col in columns: tree.heading(col, text=col)
    tree.pack(pady=5, padx=20, fill=X)

    # customer form
    form = Frame(root)
    form.pack(pady=15)
    Label(form, text="Customer:").grid(row=0, column=0)
    ent_name = Entry(form); ent_name.grid(row=0, column=1, padx=10, pady=5)
    Label(form, text="Movie ID:").grid(row=1, column=0)
    ent_mid = Entry(form); ent_mid.grid(row=1, column=1, padx=10, pady=5)
    Label(form, text="Seats:").grid(row=2, column=0)
    ent_seats = Entry(form); ent_seats.grid(row=2, column=1, padx=10, pady=5)

    # issue ticket Button
    btn_frame = Frame(root)
    btn_frame.pack(pady=10)

    Button(btn_frame, text="Issue Ticket", command=handle_booking, bg="green", fg="white", width=15, font=("Arial", 11, "bold")).grid(row=0, column=0, padx=10)
    
    # view booking button
    Button(btn_frame, text="View All Bookings", command=show_bookings_window, bg="blue", fg="white", width=15, font=("Arial", 11, "bold")).grid(row=0, column=1, padx=10)

    refresh_data()
    root.mainloop()

# --- LOGIN SCREEN ---
def show_login_screen():
    login_win = Tk()
    login_win.title("Cineplex Login")
    login_win.geometry("350x300")

    def attempt_login():
        u, p = entry_user.get(), entry_pw.get()
        db = get_db()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM employees WHERE username=%s AND password=%s", (u, p))
            result = cursor.fetchone()
            db.close()
            if result:
                login_win.destroy()
                open_booking_window(result[3])
            else:
                messagebox.showerror("Error", "Invalid login")

    Label(login_win, text="STAFF LOGIN", font=("Arial", 16, "bold")).pack(pady=20)
    Label(login_win, text="Username").pack()
    entry_user = Entry(login_win); entry_user.pack(pady=5)
    Label(login_win, text="Password").pack()
    entry_pw = Entry(login_win, show="*"); entry_pw.pack(pady=5)
    Button(login_win, text="Login", command=attempt_login, bg="#444", fg="white", width=15).pack(pady=20)
    login_win.mainloop()

if __name__ == "__main__":
    show_login_screen()