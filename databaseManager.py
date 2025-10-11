import sqlite3
import json
class DatabaseManager:
    def __init__(self, db_name='database.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at DATE NOT NULL,
                birth_year INTEGER NOT NULL,
                active BOOLEAN NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                license_plate TEXT NOT NULL,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                color TEXT NOT NULL,
                year TEXT NOT NULL,
                created_at DATE NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_lots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                address TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                reserved INTEGER NOT NULL,
                tariff REAL NOT NULL,
                daytariff INTEGER NOT NULL,
                created_at DATE NOT NULL,
                coordinates_lat REAL NOT NULL,
                coordinates_lng REAL NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parking_lot_id INTEGER NOT NULL,
                license_plate TEXT NOT NULL,
                started DATE NOT NULL,
                stopped DATE,
                username TEXT NOT NULL,
                duration_minutes INTEGER,
                cost REAL,
                payment_status TEXT NOT NULL,
                FOREIGN KEY(parking_lot_id) REFERENCES parking_lots(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                parking_lot_id INTEGER NOT NULL,
                license_plate TEXT NOT NULL,
                start_time DATE NOT NULL,
                end_time DATE NOT NULL,
                status TEXT NOT NULL,
                created_at DATE NOT NULL,
                cost REAL NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(parking_lot_id) REFERENCES parking_lots(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                method TEXT NOT NULL,
                issuer TEXT NOT NULL,
                bank TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                "transaction" TEXT PRIMARY KEY,
                amount REAL NOT NULL,
                initiator_id INTEGER NOT NULL,
                created_at DATE NOT NULL,
                completed TEXT NOT NULL,
                hash TEXT NOT NULL,
                t_data_id INTEGER NOT NULL,
                parking_session_id INTEGER NOT NULL,
                parking_lot_id INTEGER NOT NULL,
                FOREIGN KEY(initiator_id) REFERENCES users(id),
                FOREIGN KEY(parking_session_id) REFERENCES parking_sessions(id),
                FOREIGN KEY(parking_lot_id) REFERENCES parking_lots(id),
                FOREIGN KEY(t_data_id) REFERENCES transactions(id)
            )
        ''')
        
        self.connection.commit()
    
    def insert_user(self, username, password, name, email, phone, role, created_at, birth_year, active):
        self.cursor.execute('''
            INSERT INTO users (username, password, name, email, phone, role, created_at, birth_year, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, name, email, phone, role, created_at, birth_year, active))
        self.connection.commit()
    
    def insert_vehicle(self, user_id, license_plate, make, model, color, year, created_at):
        self.cursor.execute('''
            INSERT INTO vehicles (user_id, license_plate, make, model, color, year, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, license_plate, make, model, color, year, created_at))
        self.connection.commit()
    
    def insert_parking_lot(self, name, location, address, capacity, reserved, tariff, daytariff, created_at, coordinateds_lat, coordinateds_lng):
        self.cursor.execute('''
            INSERT INTO parking_lots (name, location, address, capacity, reserved, tariff, daytariff, created_at, coordinates_lat, coordinates_lng)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, location, address, capacity, reserved, tariff, daytariff, created_at, coordinateds_lat, coordinateds_lng))
        self.connection.commit()
    
    def insert_parking_session(self, parking_lot_id, license_plate, started, stopped, username, duration_minutes, cost, payment_status):
        self.cursor.execute('''
            INSERT INTO parking_sessions (parking_lot_id, license_plate, started, stopped, username, duration_minutes, cost, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (parking_lot_id, license_plate, started, stopped, username, duration_minutes, cost, payment_status))
        self.connection.commit()
    
    def insert_reservation(self, user_id, parking_lot_id, license_plate, start_time, end_time, status, created_at, cost):
        self.cursor.execute('''
            INSERT INTO reservations (user_id, parking_lot_id, license_plate, start_time, end_time, status, created_at, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, parking_lot_id, license_plate, start_time, end_time, status, created_at, cost))
        self.connection.commit()
    
    def insert_transaction(self, amount, date, method, issuer, bank):
        self.cursor.execute('''
            INSERT INTO transactions (amount, date, method, issuer, bank)
            VALUES (?, ?, ?, ?, ?)
        ''', (amount, date, method, issuer, bank))
        self.connection.commit()
    
    def insert_payment(self, transaction, amount, initiator_id, created_at, completed, hash, t_data_id, parking_session_id, parking_lot_id):
        self.cursor.execute('''
            INSERT INTO payments (transaction, amount, initiator_id, created_at, completed, hash, t_data_id, parking_session_id, parking_lot_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (transaction, amount, initiator_id, created_at, completed, hash, t_data_id, parking_session_id, parking_lot_id))
        self.connection.commit()
        
    def get_user_by_username(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()
    
    def get_vehicle_by_vehicle_id(self, vehicle_id):
        self.cursor.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,))
        return self.cursor.fetchone()
    

    def close(self):
        self.connection.close()
    