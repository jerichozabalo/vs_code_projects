from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3
from datetime import datetime
import csv
import io
from config import DATABASE, SECRET_KEY, DEBUG

app = Flask(__name__)
app.secret_key = SECRET_KEY

DB_NAME = DATABASE

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

def get_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, amount, category, description, date FROM expenses ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_expense(amount, category, description, date=None):
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)',
                   (amount, category, description, date))
    conn.commit()
    conn.close()

def update_expense(id, amount, category, description, date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE expenses SET amount=?, category=?, description=?, date=? WHERE id=?',
                   (amount, category, description, date, id))
    conn.commit()
    conn.close()

def delete_expense(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id=?', (id,))
    conn.commit()
    conn.close()

def get_summary(start_date=None, end_date=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = 'SELECT SUM(amount) FROM expenses'
    params = []
    if start_date and end_date:
        query += ' WHERE date BETWEEN ? AND ?'
        params = [start_date, end_date]
    cursor.execute(query, params)
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

def get_summary_by_category(start_date=None, end_date=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = 'SELECT category, SUM(amount) FROM expenses'
    params = []
    if start_date and end_date:
        query += ' WHERE date BETWEEN ? AND ?'
        params = [start_date, end_date]
    query += ' GROUP BY category'
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route('/')
def index():
    expenses = get_expenses()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                raise ValueError("Amount must be positive")
            category = request.form['category'].strip()
            if not category:
                raise ValueError("Category is required")
            description = request.form['description'].strip()
            if not description:
                raise ValueError("Description is required")
            date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
            add_expense(amount, category, description, date)
            flash("Expense added successfully!")
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                raise ValueError("Amount must be positive")
            category = request.form['category'].strip()
            if not category:
                raise ValueError("Category is required")
            description = request.form['description'].strip()
            if not description:
                raise ValueError("Description is required")
            date = request.form['date']
            update_expense(id, amount, category, description, date)
            flash("Expense updated successfully!")
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE id=?', (id,))
    expense = cursor.fetchone()
    conn.close()
    return render_template('edit.html', expense=expense)

@app.route('/delete/<int:id>')
def delete(id):
    delete_expense(id)
    return redirect(url_for('index'))

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    total = get_summary(start_date, end_date)
    by_category = get_summary_by_category(start_date, end_date)
    return render_template('summary.html', total=total, by_category=by_category, start_date=start_date, end_date=end_date)

@app.route('/export')
def export():
    expenses = get_expenses()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Amount', 'Category', 'Description', 'Date'])
    for expense in expenses:
        writer.writerow(expense)
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=expenses.csv'})

if __name__ == '__main__':
    init_db()
    app.run(debug=DEBUG)