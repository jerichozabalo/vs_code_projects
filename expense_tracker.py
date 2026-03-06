import argparse
import sqlite3
from datetime import datetime

# Database setup
DB_NAME = 'expenses.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_expense(amount, category, description):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)',
                   (amount, category, description, date))
    conn.commit()
    conn.close()
    print(f"Expense added: ${amount} for {category} - {description}")

def list_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, amount, category, description, date FROM expenses ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("No expenses recorded yet.")
        return
    print("ID | Amount | Category | Description | Date")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]} | ${row[1]:.2f} | {row[2]} | {row[3]} | {row[4]}")

def summary_expenses(by_category=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if by_category:
        cursor.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
        rows = cursor.fetchall()
        print("Category | Total")
        print("-" * 20)
        for row in rows:
            print(f"{row[0]} | ${row[1]:.2f}")
    else:
        cursor.execute('SELECT SUM(amount) FROM expenses')
        total = cursor.fetchone()[0] or 0
        print(f"Total expenses: ${total:.2f}")
    conn.close()

def main():
    init_db()
    parser = argparse.ArgumentParser(description="Simple Expense Tracker CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add expense
    add_parser = subparsers.add_parser('add', help='Add a new expense')
    add_parser.add_argument('--amount', type=float, required=True, help='Expense amount')
    add_parser.add_argument('--category', type=str, required=True, help='Expense category')
    add_parser.add_argument('--description', type=str, required=True, help='Expense description')

    # List expenses
    subparsers.add_parser('list', help='List all expenses')

    # Summary
    summary_parser = subparsers.add_parser('summary', help='View expense summary')
    summary_parser.add_argument('--by-category', action='store_true', help='Summarize by category')

    args = parser.parse_args()

    if args.command == 'add':
        add_expense(args.amount, args.category, args.description)
    elif args.command == 'list':
        list_expenses()
    elif args.command == 'summary':
        summary_expenses(args.by_category)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()