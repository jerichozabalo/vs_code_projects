# Expense Tracker

A simple expense tracker with CLI and web interface.

## Project Structure

```
expense-tracker/
├── app.py                 # Flask web application
├── expense_tracker.py     # CLI script
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── index.html
│   ├── add.html
│   ├── edit.html
│   └── summary.html
├── static/                # CSS and static files
│   └── style.css
├── data/                  # Data storage
│   └── expenses.db        # SQLite database (auto-created)
└── README.md
```

## Setup

1. Ensure Python 3.12+ is installed.
2. Clone or download the project.
3. Create virtual environment: `python -m venv venv`
4. Activate (Windows): `venv\Scripts\activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Run CLI: `python expense_tracker.py --help`
7. Run web app: `python app.py`

## Usage

### CLI
- Add: `python expense_tracker.py add --amount 10.00 --category food --description "Lunch"`
- List: `python expense_tracker.py list`
- Summary: `python expense_tracker.py summary` or `python expense_tracker.py summary --by-category`

### Web
- Open http://127.0.0.1:5000
- Add, edit, delete expenses via forms
- View summaries with optional date filtering
- Export expenses as CSV

## Features

- ✅ Add, edit, delete expenses
- ✅ View expense lists and summaries
- ✅ Filter by date range
- ✅ Category-based summaries
- ✅ CSV export
- ✅ Both CLI and web interfaces
- ✅ Input validation and error handling

## Configuration

Edit `config.py` to customize settings:
- `DATABASE`: Path to SQLite database
- `SECRET_KEY`: Flask session secret (change for production)
- `DEBUG`: Enable/disable debug mode

## Deployment

For production, use Gunicorn: `pip install gunicorn`, then `gunicorn app:app`.