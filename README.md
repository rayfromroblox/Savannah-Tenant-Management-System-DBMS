<<<<<<< HEAD
# Savannah-Tenant-Management-System-DBMS
Savannah Apartments is a lightweight Flask-based property management system for rooms, tenants, and payments with an intuitive dashboard and simple analytics.
=======
# Hostel Management System

A complete hostel management system built with Flask, SQLite, and pure HTML/CSS. This system is designed for local use by hostel caretakers/admins to manage rooms, tenants, and rent payments.

## Features

- **Authentication System**: Simple login/logout for admin users
- **Room Management**: Add, edit, delete rooms with occupancy tracking
- **Tenant Management**: Add, edit, delete tenants with room assignment
- **Payment Management**: Record payments and track tenant balances
- **Analytics Dashboard**: View occupancy statistics, arrears, and collection reports
- **Clean UI**: Blue and white theme with responsive design

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the system**:
   - Open your browser and go to `http://localhost:5000`
   - Default login credentials:
     - Username: `admin`
     - Password: `admin123`

## Database Structure

The system uses SQLite database (`hostel.db`) with the following tables:

- **rooms**: Room information (number, type, rent, status)
- **tenants**: Tenant details (name, phone, room assignment, balance)
- **payments**: Payment records (amount, date, notes)
- **admin**: Admin user credentials

## Usage

### Dashboard
- View key statistics (total rooms, occupancy, tenants, arrears)
- Quick access to all management functions
- Recent tenant overview

### Room Management
- Add new rooms with type and monthly rent
- Edit existing room details
- Delete vacant rooms
- Automatic occupancy status updates

### Tenant Management
- Add new tenants with room assignment
- Edit tenant information
- Delete tenants (removes all payment history)
- Track individual tenant balances

### Payment Management
- Record rent payments
- Automatic balance updates
- Payment history tracking
- Delete payments (reverses balance changes)

### Analytics
- View tenants in arrears
- Room occupancy charts
- Monthly collection reports
- Total arrears calculation

## Security Notes

- This system is designed for local use only
- Default admin credentials should be changed after first login
- No external database connections or cloud services
- Session-based authentication

## Customization

- Modify `static/css/style.css` to change the appearance
- Update room types in the room form template
- Adjust the theme colors by changing CSS variables
- Add new features by extending the Flask routes

## File Structure

```
hostel-management/
├── app.py                 # Main Flask application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/           # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── rooms.html
│   ├── room_form.html
│   ├── tenants.html
│   ├── tenant_form.html
│   ├── payments.html
│   ├── payment_form.html
│   └── analytics.html
└── static/
    └── css/
        └── style.css    # Main stylesheet
```

## Troubleshooting

- **Database errors**: Delete `hostel.db` file and restart the application
- **Port conflicts**: Change the port in `app.py` (line: `app.run(debug=True, host='0.0.0.0', port=5000)`)
- **Permission errors**: Ensure the application has write permissions in the project directory

## License

This project is for educational and personal use. Feel free to modify and distribute as needed.
>>>>>>> 4222f94 (Add dark/light mode toggle and theme support)
