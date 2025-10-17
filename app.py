# --- Imports and app definition moved to top ---
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from datetime import datetime, date, timedelta
from functools import wraps, lru_cache
import time

app = Flask(__name__)
app.secret_key = 'hostel_management_secret_key_2024'

# Simple in-memory cache for performance
cache = {
    'rooms': {'data': None, 'timestamp': 0},
    'stats': {'data': None, 'timestamp': 0}
}
CACHE_DURATION = 30  # seconds

# --- Tenant details JSON endpoint for modal ---
# (define only once, after app is defined)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Tenant details JSON endpoint for modal ---
@app.route('/tenant/<int:tenant_id>/details')
@login_required
def tenant_details_json(tenant_id):
    conn = get_db_connection()
    t = conn.execute('''
        SELECT t.tenant_id, t.tenant_name, t.id_number, t.tenant_phone, t.move_in_date,
               t.relative_name, t.relative_contact, t.relative_id_number,
               r.room_number, r.monthly_rent,
               (
                   SELECT COALESCE(SUM(p.amount), 0)
                   FROM payments p
                   WHERE p.tenant_id = t.tenant_id
               ) as total_paid
        FROM tenants t
        LEFT JOIN rooms r ON t.room_id = r.room_id
        WHERE t.tenant_id = ?
    ''', (tenant_id,)).fetchone()
    # Also fetch all payments for this tenant, sorted by date desc
    payments = conn.execute('''
        SELECT amount, payment_date FROM payments WHERE tenant_id = ? ORDER BY payment_date DESC''', (tenant_id,)).fetchall()
    conn.close()
    if not t:
        return jsonify({'error': 'Tenant not found'}), 404
    monthly_rent = t['monthly_rent'] or 0
    total_paid = t['total_paid'] or 0
    balance = total_paid - monthly_rent
    if balance > 0:
        balance_status = 'credit'
    elif balance == 0:
        balance_status = 'paid'
    else:
        balance_status = 'arrears'
    arrears_excess = abs(balance) if balance != 0 else 0
    return jsonify({
        'tenant_id': t['tenant_id'],
        'tenant_name': t['tenant_name'],
        'id_number': t['id_number'],
        'tenant_phone': t['tenant_phone'],
        'move_in_date': t['move_in_date'],
        'relative_name': t['relative_name'],
        'relative_contact': t['relative_contact'],
        'relative_id': t['relative_id_number'],
        'room_number': t['room_number'],
        'monthly_rent': monthly_rent,
        'total_paid': total_paid,
        'balance': balance,
        'balance_status': balance_status,
        'arrears_excess': arrears_excess,
        'payments': [dict(p) for p in payments]
    })
@app.template_filter('currency')
def currency_filter(value):
    """Format number as KES currency with commas"""
    if value is None:
        return "KES 0.00"
    return f"KES {value:,.2f}"

# Database configuration
DATABASE = 'hostel.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=20.0)
    conn.row_factory = sqlite3.Row
    # Performance optimizations
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=10000')
    conn.execute('PRAGMA temp_store=MEMORY')
    return conn

def get_cached_data(key):
    """Get data from cache if it's still valid"""
    if key in cache:
        data, timestamp = cache[key]['data'], cache[key]['timestamp']
        if time.time() - timestamp < CACHE_DURATION:
            return data
    return None

def set_cached_data(key, data):
    """Set data in cache with current timestamp"""
    cache[key] = {'data': data, 'timestamp': time.time()}

def init_db():
    conn = get_db_connection()
    
    # Create rooms table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            monthly_rent REAL NOT NULL,
            status TEXT DEFAULT 'vacant'
        )
    ''')
    
    # Create tenants table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_name TEXT NOT NULL,
            tenant_phone TEXT NOT NULL,
            room_id INTEGER,
            move_in_date DATE NOT NULL,
            balance REAL DEFAULT 0,
            FOREIGN KEY (room_id) REFERENCES rooms (room_id)
        )
    ''')
    
    # Create payments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date DATE NOT NULL,
            notes TEXT,
            FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id)
        )
    ''')
    
    # Create admin table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Insert default admin if not exists
    existing_admin = conn.execute('SELECT * FROM admin WHERE username = ?', ('admin',)).fetchone()
    if not existing_admin:
        conn.execute('INSERT INTO admin (username, password) VALUES (?, ?)', ('admin', 'admin123'))
    
    # --- Safe migrations: extend tenants with new fields if missing ---
    def column_missing(table, column):
        cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return all(col['name'] != column for col in cols)

    # credit balance for rollover
    if column_missing('tenants', 'credit_balance'):
        conn.execute('ALTER TABLE tenants ADD COLUMN credit_balance REAL DEFAULT 0')

    # last payment date for countdown
    if column_missing('tenants', 'last_payment_date'):
        conn.execute('ALTER TABLE tenants ADD COLUMN last_payment_date DATE')

    # Enhanced registration fields (stored but not shown on main dashboards)
    # First/second name no longer used (keep existing columns if already present, but don't add new ones)
    if column_missing('tenants', 'id_number'):
        conn.execute('ALTER TABLE tenants ADD COLUMN id_number TEXT')
    # Ensure target fields exist: relative_name and relative_contact
    if column_missing('tenants', 'relative_name'):
        conn.execute('ALTER TABLE tenants ADD COLUMN relative_name TEXT')
    if column_missing('tenants', 'relative_contact'):
        conn.execute('ALTER TABLE tenants ADD COLUMN relative_contact TEXT')
    if column_missing('tenants', 'relative_id_number'):
        conn.execute('ALTER TABLE tenants ADD COLUMN relative_id_number TEXT')

    # Backfill: move next_of_kin_* data into relative_* if present
    cols = {c['name'] for c in conn.execute("PRAGMA table_info(tenants)").fetchall()}
    if 'next_of_kin_name' in cols:
        conn.execute('UPDATE tenants SET relative_name = COALESCE(relative_name, next_of_kin_name) WHERE next_of_kin_name IS NOT NULL AND (relative_name IS NULL OR relative_name = "")')
    if 'next_of_kin_contact' in cols and 'relative_contact' in cols:
        conn.execute('UPDATE tenants SET relative_contact = COALESCE(relative_contact, next_of_kin_contact) WHERE next_of_kin_contact IS NOT NULL AND (relative_contact IS NULL OR relative_contact = "")')

    # Tenant stays history table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tenant_stays (
            stay_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            room_id INTEGER,
            start_date DATE NOT NULL,
            end_date DATE,
            rent_amount REAL,
            note TEXT,
            FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
            FOREIGN KEY (room_id) REFERENCES rooms (room_id)
        )
    ''')

    # Create indexes for better performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_rooms_room_number ON rooms(room_number)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_tenants_room_id ON tenants(room_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_tenants_name ON tenants(tenant_name)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_payments_tenant_id ON payments(tenant_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_payments_month ON payments(strftime("%Y-%m", payment_date))')
    
    # Seed rooms if not exists
    existing_rooms = conn.execute('SELECT COUNT(*) as count FROM rooms').fetchone()['count']
    if existing_rooms == 0:
        seed_rooms(conn)
    
    conn.commit()
    conn.close()

def seed_rooms(conn):
    """Seed the database with 24 rooms with proper types and rents"""
    import random
    
    # Define room types and their rents
    room_types = {
        'one bedroom': 15000,
        'studio': 12000,
        'bedsitter (big)': 10000,
        'bedsitter (small)': 8000
    }
    
    # Create list of room assignments (6 of each type)
    room_assignments = []
    for room_type, rent in room_types.items():
        for _ in range(6):  # 6 rooms of each type
            room_assignments.append((room_type, rent))
    
    # Randomize the order
    random.shuffle(room_assignments)
    
    # Insert rooms 1-24
    for room_num in range(1, 25):
        room_type, rent = room_assignments[room_num - 1]
        conn.execute('INSERT INTO rooms (room_number, room_type, monthly_rent) VALUES (?, ?, ?)',
                    (str(room_num), room_type, rent))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def update_room_status():
    """Update room status based on tenant occupancy"""
    conn = get_db_connection()
    
    # Get all rooms
    rooms = conn.execute('SELECT room_id FROM rooms').fetchall()
    
    for room in rooms:
        room_id = room['room_id']
        # Check if room has active tenant
        tenant = conn.execute('SELECT * FROM tenants WHERE room_id = ?', (room_id,)).fetchone()
        
        if tenant:
            conn.execute('UPDATE rooms SET status = ? WHERE room_id = ?', ('occupied', room_id))
        else:
            conn.execute('UPDATE rooms SET status = ? WHERE room_id = ?', ('vacant', room_id))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin WHERE username = ? AND password = ?', 
                           (username, password)).fetchone()
        conn.close()
        
        if admin:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    
    # Get statistics
    total_rooms = conn.execute('SELECT COUNT(*) as count FROM rooms').fetchone()['count']
    occupied_rooms = conn.execute('SELECT COUNT(*) as count FROM rooms WHERE status = ?', ('occupied',)).fetchone()['count']
    vacant_rooms = total_rooms - occupied_rooms
    total_tenants = conn.execute('SELECT COUNT(*) as count FROM tenants').fetchone()['count']
    
    # Calculate total arrears considering credits and current month payments
    current_month = datetime.now().strftime('%Y-%m')
    arrears_data = conn.execute('''
        SELECT 
            t.tenant_id,
            t.credit_balance,
            t.last_payment_date,
            r.monthly_rent,
            (
                SELECT COALESCE(SUM(p2.amount), 0)
                FROM payments p2
                WHERE p2.tenant_id = t.tenant_id
                  AND strftime('%Y-%m', p2.payment_date) = ?
            ) AS paid_this_month
        FROM tenants t 
        LEFT JOIN rooms r ON t.room_id = r.room_id 
    ''', (current_month,)).fetchall()
    
    total_arrears = 0
    for tenant in arrears_data:
        monthly_rent = tenant['monthly_rent'] if tenant['monthly_rent'] else 0
        effective_paid = (tenant['paid_this_month'] or 0) + (tenant['credit_balance'] or 0)
        arrears = max(0, monthly_rent - effective_paid)
        total_arrears += arrears
    
    # Get recent tenants with optimized query
    current_month = datetime.now().strftime('%Y-%m')
    recent_tenants = conn.execute('''
        SELECT 
            t.tenant_id,
            t.tenant_name,
            t.tenant_phone,
            t.move_in_date,
            t.credit_balance,
            t.last_payment_date,
            r.room_number,
            r.monthly_rent,
            COALESCE(p.total_payments, 0) as total_payments
        FROM tenants t 
        LEFT JOIN rooms r ON t.room_id = r.room_id 
        LEFT JOIN (
            SELECT tenant_id, SUM(amount) as total_payments
            FROM payments 
            WHERE strftime('%Y-%m', payment_date) = ?
            GROUP BY tenant_id
        ) p ON t.tenant_id = p.tenant_id
        ORDER BY t.move_in_date DESC 
        LIMIT 5
    ''', (current_month,)).fetchall()
    
    def compute_days_since(d):
        if not d:
            return None
        try:
            d0 = datetime.strptime(d, '%Y-%m-%d').date()
        except Exception:
            try:
                d0 = datetime.fromisoformat(d).date()
            except Exception:
                return None
        return (date.today() - d0).days

    # enrich recent tenants with days_since, net_balance, balance_status for template simplicity
    enriched_recent = []
    for t in recent_tenants:
        item = dict(t)
        # net_balance = total_payments_for_current_cycle - monthly_rent
        monthly_rent = t['monthly_rent'] or 0
        total_paid = t['total_payments'] or 0
        net_balance = total_paid - monthly_rent
        item['net_balance'] = net_balance
        # status: credit, paid, arrears
        if net_balance > 0:
            item['balance_status'] = 'credit'
        elif net_balance == 0:
            item['balance_status'] = 'paid'
        else:
            item['balance_status'] = 'arrears'
        item['days_since'] = compute_days_since(t['last_payment_date'])
        enriched_recent.append(item)

    stats = {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'vacant_rooms': vacant_rooms,
        'total_tenants': total_tenants,
        'total_arrears': total_arrears
    }
    
    # Reminder system: tenants with partial/no payment
    reminders = conn.execute('''
        SELECT 
            t.tenant_id,
            t.tenant_name,
            t.last_payment_date,
            t.credit_balance,
            r.room_number,
            r.monthly_rent,
            (
                SELECT COALESCE(SUM(p2.amount), 0)
                FROM payments p2
                WHERE p2.tenant_id = t.tenant_id
                  AND strftime('%Y-%m', p2.payment_date) = strftime('%Y-%m', 'now')
            ) as paid_this_month
        FROM tenants t
        LEFT JOIN rooms r ON t.room_id = r.room_id
        ORDER BY t.tenant_name
    ''').fetchall()
    conn.close()

    def compute_days_since(d):
        if not d:
            return None
        try:
            d0 = datetime.strptime(d, '%Y-%m-%d').date()
        except Exception:
            try:
                d0 = datetime.fromisoformat(d).date()
            except Exception:
                return None
        return (date.today() - d0).days

    reminder_cards = []
    for r in reminders:
        rent = r['monthly_rent'] or 0
        effective_paid = (r['paid_this_month'] or 0) + (r['credit_balance'] or 0)
        amount_remaining = max(0, rent - effective_paid)
        if amount_remaining <= 0:
            continue  # fully paid, skip
        days_since = compute_days_since(r['last_payment_date'])
        if days_since is None:
            days_since = (date.today() - date.fromisoformat('1970-01-01')).days  # treat as very old/no payment
        if days_since <= 4:
            level = 'pending'
        elif days_since <= 13:
            level = 'warning'
        else:
            level = 'critical'
        reminder_cards.append({
            'tenant_name': r['tenant_name'],
            'room_number': r['room_number'],
            'amount_remaining': amount_remaining,
            'days_overdue': days_since,
            'level': level
        })

    # --- Sanity check for Eric Onyango ---
    for t in enriched_recent:
        if t['tenant_name'].lower() == 'eric onyango':
            assert t['monthly_rent'] == 15000, f"Eric Onyango rent should be 15000, got {t['monthly_rent']}"
            assert t['total_payments'] == 19000, f"Eric Onyango total_payments should be 19000, got {t['total_payments']}"
            assert t['net_balance'] == 4000, f"Eric Onyango net_balance should be 4000, got {t['net_balance']}"
            assert t['balance_status'] == 'credit', f"Eric Onyango balance_status should be credit, got {t['balance_status']}"
    # --- End sanity check ---
    return render_template('dashboard.html', stats=stats, recent_tenants=enriched_recent, reminders=reminder_cards)

# Rooms routes
@app.route('/rooms')
@login_required
def rooms():
    # Check cache first
    cached_rooms = get_cached_data('rooms')
    if cached_rooms:
        return render_template('rooms.html', rooms=cached_rooms)
    
    conn = get_db_connection()
    rooms = conn.execute('''
        SELECT r.*, t.tenant_name 
        FROM rooms r 
        LEFT JOIN tenants t ON r.room_id = t.room_id 
        ORDER BY CAST(r.room_number AS INTEGER)
    ''').fetchall()
    conn.close()
    
    # Cache the results
    set_cached_data('rooms', rooms)
    return render_template('rooms.html', rooms=rooms)

@app.route('/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room():
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        monthly_rent = float(request.form['monthly_rent'])
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO rooms (room_number, room_type, monthly_rent) VALUES (?, ?, ?)',
                        (room_number, room_type, monthly_rent))
            conn.commit()
            # Invalidate cache
            cache['rooms'] = {'data': None, 'timestamp': 0}
            flash('Room added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Room number already exists!', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('rooms'))
    
    return render_template('room_form.html')

@app.route('/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        monthly_rent = float(request.form['monthly_rent'])
        
        try:
            conn.execute('UPDATE rooms SET room_number = ?, room_type = ?, monthly_rent = ? WHERE room_id = ?',
                        (room_number, room_type, monthly_rent, room_id))
            conn.commit()
            flash('Room updated successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Room number already exists!', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('rooms'))
    
    room = conn.execute('SELECT * FROM rooms WHERE room_id = ?', (room_id,)).fetchone()
    conn.close()
    
    if not room:
        flash('Room not found!', 'error')
        return redirect(url_for('rooms'))
    
    return render_template('room_form.html', room=room)

@app.route('/rooms/delete/<int:room_id>')
@login_required
def delete_room(room_id):
    conn = get_db_connection()
    
    # Check if room has tenants
    tenant = conn.execute('SELECT * FROM tenants WHERE room_id = ?', (room_id,)).fetchone()
    if tenant:
        flash('Cannot delete room with active tenants!', 'error')
        conn.close()
        return redirect(url_for('rooms'))
    
    conn.execute('DELETE FROM rooms WHERE room_id = ?', (room_id,))
    conn.commit()
    conn.close()
    
    flash('Room deleted successfully!', 'success')
    return redirect(url_for('rooms'))

# Tenants routes
@app.route('/tenants')
@login_required
def tenants():
    conn = get_db_connection()
    tenants_rows = conn.execute('''
        SELECT 
            t.tenant_id,
            t.tenant_name,
            t.tenant_phone,
            t.move_in_date,
            t.last_payment_date,
            r.room_number,
            r.monthly_rent,
            (
                SELECT COALESCE(SUM(p2.amount), 0)
                FROM payments p2
                WHERE p2.tenant_id = t.tenant_id
                  AND strftime('%Y-%m', p2.payment_date) = strftime('%Y-%m', 'now')
            ) as total_payments,
            (r.monthly_rent - ((
                SELECT COALESCE(SUM(p3.amount), 0)
                FROM payments p3
                WHERE p3.tenant_id = t.tenant_id
                  AND strftime('%Y-%m', p3.payment_date) = strftime('%Y-%m', 'now')
            ) + COALESCE(t.credit_balance, 0))) as balance
        FROM tenants t 
        LEFT JOIN rooms r ON t.room_id = r.room_id 
        GROUP BY t.tenant_id, t.tenant_name, t.tenant_phone, t.move_in_date, t.last_payment_date, r.room_number, r.monthly_rent
        ORDER BY t.tenant_name
    ''').fetchall()
    tenants = [dict(row) for row in tenants_rows]
    conn.close()
    return render_template('tenants.html', tenants=tenants)

@app.route('/tenants/add', methods=['GET', 'POST'])
@login_required
def add_tenant():
    conn = get_db_connection()
    
    if request.method == 'POST':
        tenant_name = request.form['tenant_name']
        tenant_phone = request.form['tenant_phone']
        room_id = int(request.form['room_id']) if request.form['room_id'] else None
        move_in_date = request.form['move_in_date']
        # Enhanced fields (optional)
        id_number = request.form.get('id_number')
        relative_name = request.form.get('relative_name')
        relative_contact = request.form.get('relative_contact')
        relative_id_number = request.form.get('relative_id_number')
        
        # Check if room is available
        if room_id:
            room = conn.execute('SELECT * FROM rooms WHERE room_id = ? AND status = ?', 
                              (room_id, 'vacant')).fetchone()
            if not room:
                flash('Selected room is not available!', 'error')
                conn.close()
                return render_template('tenant_form.html', rooms=get_available_rooms())
        
        conn.execute('''
            INSERT INTO tenants (
                tenant_name, tenant_phone, room_id, move_in_date,
                id_number,
                relative_name, relative_contact, relative_id_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                tenant_name, tenant_phone, room_id, move_in_date,
                id_number,
                relative_name, relative_contact, relative_id_number
            )
        )
        conn.commit()
        
        # Update room status
        update_room_status()
        
        flash('Tenant added successfully!', 'success')
        conn.close()
        return redirect(url_for('tenants'))
    
    rooms = get_available_rooms()
    conn.close()
    return render_template('tenant_form.html', rooms=rooms)

@app.route('/tenants/edit/<int:tenant_id>', methods=['GET', 'POST'])
@login_required
def edit_tenant(tenant_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        tenant_name = request.form['tenant_name']
        tenant_phone = request.form['tenant_phone']
        room_id = int(request.form['room_id']) if request.form['room_id'] else None
        move_in_date = request.form['move_in_date']
        id_number = request.form.get('id_number')
        relative_name = request.form.get('relative_name')
        relative_contact = request.form.get('relative_contact')
        relative_id_number = request.form.get('relative_id_number')

        conn.execute('''
            UPDATE tenants 
            SET tenant_name = ?, tenant_phone = ?, room_id = ?, move_in_date = ?,
                id_number = ?,
                relative_name = ?, relative_contact = ?, relative_id_number = ?
            WHERE tenant_id = ?
        ''', (
            tenant_name, tenant_phone, room_id, move_in_date,
            id_number,
            relative_name, relative_contact, relative_id_number,
            tenant_id
        ))
        conn.commit()
        
        # Update room status
        update_room_status()
        
        flash('Tenant updated successfully!', 'success')
        conn.close()
        return redirect(url_for('tenants'))
    
    tenant = conn.execute('SELECT * FROM tenants WHERE tenant_id = ?', (tenant_id,)).fetchone()
    rooms = conn.execute('SELECT * FROM rooms ORDER BY room_number').fetchall()
    conn.close()
    
    if not tenant:
        flash('Tenant not found!', 'error')
        return redirect(url_for('tenants'))
    
    return render_template('tenant_form.html', tenant=tenant, rooms=rooms)

@app.route('/tenants/delete/<int:tenant_id>')
@login_required
def delete_tenant(tenant_id):
    conn = get_db_connection()
    
    # Delete tenant's payments first
    conn.execute('DELETE FROM payments WHERE tenant_id = ?', (tenant_id,))
    
    # Delete tenant
    conn.execute('DELETE FROM tenants WHERE tenant_id = ?', (tenant_id,))
    conn.commit()
    
    # Update room status
    update_room_status()
    
    conn.close()
    
    flash('Tenant deleted successfully!', 'success')
    return redirect(url_for('tenants'))

def get_available_rooms():
    conn = get_db_connection()
    rooms = conn.execute('SELECT * FROM rooms WHERE status = ? ORDER BY room_number', ('vacant',)).fetchall()
    conn.close()
    return rooms

# Payments routes
@app.route('/payments')
@login_required
def payments():
    conn = get_db_connection()
    payments = conn.execute('''
        SELECT p.*, t.tenant_name, r.room_number 
        FROM payments p 
        JOIN tenants t ON p.tenant_id = t.tenant_id 
        LEFT JOIN rooms r ON t.room_id = r.room_id 
        ORDER BY p.payment_date DESC
    ''').fetchall()
    conn.close()
    return render_template('payments.html', payments=payments)

@app.route('/payments/add', methods=['GET', 'POST'])
@login_required
def add_payment():
    conn = get_db_connection()
    
    if request.method == 'POST':
        tenant_id = int(request.form['tenant_id'])
        amount = float(request.form['amount'])
        payment_date = request.form['payment_date']
        notes = request.form['notes']
        
        # Add payment
        conn.execute('INSERT INTO payments (tenant_id, amount, payment_date, notes) VALUES (?, ?, ?, ?)',
                    (tenant_id, amount, payment_date, notes))
        
        # Update tenant last payment date
        conn.execute('UPDATE tenants SET last_payment_date = ? WHERE tenant_id = ?', (payment_date, tenant_id))

        # Recompute credit rollover for current month
        tenant_row = conn.execute('''
            SELECT t.credit_balance, r.monthly_rent
            FROM tenants t
            LEFT JOIN rooms r ON t.room_id = r.room_id
            WHERE t.tenant_id = ?
        ''', (tenant_id,)).fetchone()
        monthly_rent = tenant_row['monthly_rent'] or 0
        current_month = datetime.strptime(payment_date, '%Y-%m-%d').strftime('%Y-%m')
        paid_this_month = conn.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM payments
            WHERE tenant_id = ? AND strftime('%Y-%m', payment_date) = ?
        ''', (tenant_id, current_month)).fetchone()['total']
        effective_paid = paid_this_month + (tenant_row['credit_balance'] or 0)
        new_credit = max(0, effective_paid - monthly_rent)
        conn.execute('UPDATE tenants SET credit_balance = ? WHERE tenant_id = ?', (new_credit, tenant_id))

        conn.commit()
        conn.close()
        
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('payments'))
    
    tenants = conn.execute('''
        SELECT t.*, r.room_number,
            (
                SELECT COALESCE(SUM(p2.amount), 0)
                FROM payments p2
                WHERE p2.tenant_id = t.tenant_id AND strftime('%Y-%m', p2.payment_date) = strftime('%Y-%m', 'now')
            ) AS paid_this_month,
            (COALESCE(r.monthly_rent,0) - ((
                SELECT COALESCE(SUM(p3.amount), 0)
                FROM payments p3
                WHERE p3.tenant_id = t.tenant_id AND strftime('%Y-%m', p3.payment_date) = strftime('%Y-%m', 'now')
            ) + COALESCE(t.credit_balance,0))) AS current_balance
        FROM tenants t
        LEFT JOIN rooms r ON t.room_id = r.room_id
        ORDER BY t.tenant_name
    ''').fetchall()
    conn.close()
    return render_template('payment_form.html', tenants=tenants)

@app.route('/payments/delete/<int:payment_id>')
@login_required
def delete_payment(payment_id):
    conn = get_db_connection()
    
    # Get payment details
    payment = conn.execute('SELECT * FROM payments WHERE payment_id = ?', (payment_id,)).fetchone()
    
    if payment:
        # Reverse the balance update
        conn.execute('UPDATE tenants SET balance = balance - ? WHERE tenant_id = ?',
                    (payment['amount'], payment['tenant_id']))
        
        # Delete payment
        conn.execute('DELETE FROM payments WHERE payment_id = ?', (payment_id,))
        conn.commit()
        flash('Payment deleted successfully!', 'success')
    else:
        flash('Payment not found!', 'error')
    
    conn.close()
    return redirect(url_for('payments'))

# Analytics routes
@app.route('/api/room/<room_number>')
@login_required
def get_room_info(room_number):
    """API endpoint to get room information by room number"""
    conn = get_db_connection()
    room = conn.execute('SELECT * FROM rooms WHERE room_number = ?', (room_number,)).fetchone()
    conn.close()
    
    if room:
        return jsonify({
            'room_type': room['room_type'],
            'monthly_rent': room['monthly_rent'],
            'status': room['status']
        })
    else:
        return jsonify({'error': 'Room not found'}), 404

@app.route('/analytics')
@login_required
def analytics():
    conn = get_db_connection()
    
    # Get all tenants with their room info and payment totals
    tenants_data = conn.execute('''
        SELECT 
            t.tenant_id,
            t.tenant_name,
            t.credit_balance,
            t.last_payment_date,
            t.tenant_phone,
            t.move_in_date,
            r.room_number,
            r.monthly_rent,
            (
                SELECT COALESCE(SUM(p2.amount), 0)
                FROM payments p2
                WHERE p2.tenant_id = t.tenant_id
                  AND strftime('%Y-%m', p2.payment_date) = strftime('%Y-%m', 'now')
            ) as total_payments
        FROM tenants t 
        LEFT JOIN rooms r ON t.room_id = r.room_id 
        GROUP BY t.tenant_id, t.tenant_name, t.credit_balance, t.last_payment_date, t.tenant_phone, t.move_in_date, r.room_number, r.monthly_rent
        ORDER BY t.tenant_name
    ''').fetchall()
    
    # Calculate arrears and excess payments for each tenant based on this month's payments only
    arrears_tenants = []
    overpaid_tenants = []
    total_arrears_amount = 0
    total_credits_amount = 0
    
    for tenant in tenants_data:
        monthly_rent = tenant['monthly_rent'] if tenant['monthly_rent'] else 0
        total_paid = tenant['total_payments'] or 0
        credit_balance = tenant['credit_balance'] or 0
        total_credits_amount += credit_balance

        # Arrears: paid < monthly_rent
        arrears = monthly_rent - total_paid
        if arrears > 0:
            arrears_tenants.append({
                'tenant_id': tenant['tenant_id'],
                'tenant_name': tenant['tenant_name'],
                'tenant_phone': tenant['tenant_phone'],
                'room_number': tenant['room_number'],
                'monthly_rent': tenant['monthly_rent'],
                'total_payments': total_paid,
                'arrears': arrears,
                'balance': -arrears
            })
            total_arrears_amount += arrears

        # Excess payments: paid > monthly_rent
        excess = total_paid - monthly_rent
        if excess > 0:
            overpaid_tenants.append({
                'tenant_id': tenant['tenant_id'],
                'tenant_name': tenant['tenant_name'],
                'tenant_phone': tenant['tenant_phone'],
                'room_number': tenant['room_number'],
                'monthly_rent': tenant['monthly_rent'],
                'total_payments': total_paid,
                'excess': excess
            })
    
    # Get room occupancy stats
    room_stats = conn.execute('''
        SELECT status, COUNT(*) as count 
        FROM rooms 
        GROUP BY status
    ''').fetchall()
    # Convert Row objects to dicts for JSON serialization
    room_stats = [dict(row) for row in room_stats]
    
    # Get monthly rent collection
    current_month = datetime.now().strftime('%Y-%m')
    monthly_collection = conn.execute('''
        SELECT SUM(amount) as total 
        FROM payments 
        WHERE strftime('%Y-%m', payment_date) = ?
    ''', (current_month,)).fetchone()
    
    monthly_collection_amount = monthly_collection['total'] if monthly_collection['total'] else 0
    
    conn.close()
    
    return render_template('analytics.html', 
                         arrears_tenants=arrears_tenants,
                         overpaid_tenants=overpaid_tenants,
                         total_arrears_amount=total_arrears_amount,
                         total_credits_amount=total_credits_amount,
                         room_stats=room_stats,
                         monthly_collection_amount=monthly_collection_amount)

# Tenant Details - List and Detail Views
@app.route('/tenant-details')
@login_required
def tenant_details_list():
    q = request.args.get('q', '').strip()
    conn = get_db_connection()
    base_sql = '''
        SELECT t.tenant_id, t.tenant_name, t.tenant_phone, t.move_in_date, t.last_payment_date,
               r.room_number, r.monthly_rent,
               (
                    SELECT COALESCE(SUM(p2.amount), 0)
                    FROM payments p2
                    WHERE p2.tenant_id = t.tenant_id
                      AND strftime('%Y-%m', p2.payment_date) = strftime('%Y-%m', 'now')
               ) AS paid_this_month,
               (COALESCE(r.monthly_rent,0) - ((
                    SELECT COALESCE(SUM(p3.amount), 0)
                    FROM payments p3
                    WHERE p3.tenant_id = t.tenant_id AND strftime('%Y-%m', p3.payment_date) = strftime('%Y-%m', 'now')
               ) + COALESCE(t.credit_balance,0))) AS current_balance
        FROM tenants t
        LEFT JOIN rooms r ON t.room_id = r.room_id
    '''
    params = []
    if q:
        base_sql += ' WHERE t.tenant_name LIKE ? OR t.tenant_phone LIKE ? OR COALESCE(r.room_number, "") LIKE ?'
        like = f"%{q}%"
        params = [like, like, like]
    base_sql += ' ORDER BY t.tenant_name'
    tenants_list = conn.execute(base_sql, params).fetchall()
    conn.close()
    return render_template('tenant_details_list.html', tenants=tenants_list, q=q)

@app.route('/tenant-details/<int:tenant_id>')
@login_required
def tenant_details_view(tenant_id):
    conn = get_db_connection()
    tenant = conn.execute('''
        SELECT t.*, r.room_number, r.monthly_rent
        FROM tenants t
        LEFT JOIN rooms r ON t.room_id = r.room_id
        WHERE t.tenant_id = ?
    ''', (tenant_id,)).fetchone()
    if not tenant:
        conn.close()
        flash('Tenant not found!', 'error')
        return redirect(url_for('tenant_details_list'))

    # Current month due/balance factoring credit
    current_month = datetime.now().strftime('%Y-%m')
    paid_this_month = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM payments
        WHERE tenant_id = ? AND strftime('%Y-%m', payment_date) = ?
    ''', (tenant_id, current_month)).fetchone()['total']
    monthly_rent = tenant['monthly_rent'] or 0
    credit_balance = tenant['credit_balance'] or 0
    amount_remaining = max(0, monthly_rent - (paid_this_month + credit_balance))

    payments_history = conn.execute('''
        SELECT payment_id, amount, payment_date, notes
        FROM payments
        WHERE tenant_id = ?
        ORDER BY payment_date DESC
    ''', (tenant_id,)).fetchall()
    conn.close()

    details = {
        'tenant': tenant,
        'amount_remaining': amount_remaining,
        'paid_this_month': paid_this_month,
        'payments_history': payments_history
    }
    return render_template('tenant_details.html', **details)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
