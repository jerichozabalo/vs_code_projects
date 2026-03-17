import sqlite3
from config import DATABASE

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()
cur.execute("INSERT INTO knowledge_items (title, content, source, category, date_added) VALUES (?, ?, ?, ?, ?)",
            ("Sample", "This is a test knowledge item about productivity tips.", "chatbot", "test", "2026-03-10"))
conn.commit()
conn.close()
print('Inserted sample item')
