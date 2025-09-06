import json
import csv
import os
from datetime import datetime, timedelta

# ==============================
# Helper Functions for File I/O
# ==============================

def load_data(filename, default_data):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump(default_data, f)
    with open(filename, "r") as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# ==============================
# Initialize Files
# ==============================

books = load_data("books.json", [])
users = load_data("users.json", [])

if not os.path.exists("transactions.csv"):
    with open("transactions.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["UserID", "BookID", "Action", "Date", "DueDate", "Fine"])

# ==============================
# Book Management
# ==============================

def add_book():
    book_id = input("Enter Book ID (ISBN): ")
    title = input("Enter Book Title: ")
    author = input("Enter Author Name: ")
    books.append({"id": book_id, "title": title, "author": author, "available": True})
    save_data("books.json", books)
    print("✅ Book added successfully!")

def view_books():
    for book in books:
        status = "Available" if book["available"] else "Borrowed"
        print(f"{book['id']} - {book['title']} by {book['author']} [{status}]")

# ==============================
# User Management
# ==============================

def add_user():
    user_id = input("Enter User ID: ")
    name = input("Enter User Name: ")
    user_type = input("Enter Type (student/faculty/regular): ").lower()
    users.append({"id": user_id, "name": name, "type": user_type, "borrowed": []})
    save_data("users.json", users)
    print("✅ User added successfully!")

def view_users():
    for user in users:
        print(f"{user['id']} - {user['name']} ({user['type']}) | Borrowed: {len(user['borrowed'])}")

# ==============================
# Borrowing System
# ==============================

BORROW_LIMITS = {
    "student": (5, 21),
    "faculty": (10, 90),
    "regular": (3, 14)
}

def borrow_book():
    user_id = input("Enter User ID: ")
    book_id = input("Enter Book ID: ")

    user = next((u for u in users if u["id"] == user_id), None)
    book = next((b for b in books if b["id"] == book_id), None)

    if not user or not book:
        print("❌ Invalid User ID or Book ID!")
        return

    limit, days = BORROW_LIMITS[user["type"]]
    if len(user["borrowed"]) >= limit:
        print("❌ Borrow limit reached!")
        return
    if not book["available"]:
        print("❌ Book not available!")
        return

    due_date = datetime.now() + timedelta(days=days)
    user["borrowed"].append({"book_id": book_id, "due_date": str(due_date.date())})
    book["available"] = False

    save_data("users.json", users)
    save_data("books.json", books)

    with open("transactions.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, book_id, "Borrow", datetime.now().date(), due_date.date(), 0])

    print(f"✅ Book borrowed! Due date: {due_date.date()}")

def return_book():
    user_id = input("Enter User ID: ")
    book_id = input("Enter Book ID: ")

    user = next((u for u in users if u["id"] == user_id), None)
    book = next((b for b in books if b["id"] == book_id), None)

    if not user or not book:
        print("❌ Invalid User ID or Book ID!")
        return

    borrowed_book = next((b for b in user["borrowed"] if b["book_id"] == book_id), None)
    if not borrowed_book:
        print("❌ This book was not borrowed by the user!")
        return

    due_date = datetime.strptime(borrowed_book["due_date"], "%Y-%m-%d").date()
    today = datetime.now().date()
    fine = 0
    if today > due_date:
        fine = (today - due_date).days * 0.5

    user["borrowed"].remove(borrowed_book)
    book["available"] = True

    save_data("users.json", users)
    save_data("books.json", books)

    with open("transactions.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, book_id, "Return", today, due_date, fine])

    print(f"✅ Book returned! Fine: ${fine:.2f}")

# ==============================
# Reports
# ==============================

def borrowed_report():
    print("📌 Currently Borrowed Books:")
    for user in users:
        for b in user["borrowed"]:
            print(f"User: {user['name']} | Book: {b['book_id']} | Due: {b['due_date']}")

def overdue_report():
    print("⚠️ Overdue Books:")
    today = datetime.now().date()
    for user in users:
        for b in user["borrowed"]:
            due_date = datetime.strptime(b["due_date"], "%Y-%m-%d").date()
            if today > due_date:
                print(f"User: {user['name']} | Book: {b['book_id']} | Overdue: {(today - due_date).days} days")

# ==============================
# Main Menu
# ==============================

def main():
    while True:
        print("\n===== 📚 Library Management System =====")
        print("1. Add Book")
        print("2. View Books")
        print("3. Add User")
        print("4. View Users")
        print("5. Borrow Book")
        print("6. Return Book")
        print("7. Borrowed Report")
        print("8. Overdue Report")
        print("9. Exit")
        choice = input("Enter choice: ")

        if choice == "1": add_book()
        elif choice == "2": view_books()
        elif choice == "3": add_user()
        elif choice == "4": view_users()
        elif choice == "5": borrow_book()
        elif choice == "6": return_book()
        elif choice == "7": borrowed_report()
        elif choice == "8": overdue_report()
        elif choice == "9": break
        else: print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
