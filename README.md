# Savannah Apartments – Tenant Management System

This is a small property/hostel management app built with Flask and SQLite. It helps you keep track of rooms, tenants, and payments without needing spreadsheets or heavy software. There’s a clean dashboard, simple analytics, and a dark/light mode toggle that remembers your preference.

## What you can do
- Manage rooms: add, edit, and see who’s occupying what
- Manage tenants: assign rooms, update details, track balances
- Record payments: log rent, view history, and see who’s in arrears
- Check the dashboard: quick stats for occupancy and collections
- Switch themes: dark or light, saved per browser

## Getting started
1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python app.py` (or `start.bat` on Windows)
3. Open `http://localhost:5000` in your browser

## Notes
- Uses a local SQLite database (`hostel.db`)
- Best for a single admin/caretaker scenario
- You can customize to ur liking in `static/css/style.css` (CSS variables included)
- Doesnt actually handle payments, just keeps track of them; yet to work on the backend and facilitate for a more dynamic financial management system in future!

