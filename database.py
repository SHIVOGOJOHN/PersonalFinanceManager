"""
SQLite database handler for offline-first storage
"""
import sqlite3
from datetime import datetime
from config import DB_PATH, DEFAULT_CATEGORIES, DEFAULT_MONTHLY_BUDGET
from utils import generate_uuid, format_datetime


class DatabaseHandler:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL UNIQUE,
                monthly_limit REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                icon TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Sync metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id INTEGER PRIMARY KEY,
                last_sync TEXT,
                sync_status TEXT,
                sync_message TEXT
            )
        ''')
        
        conn.commit()
        
        # Initialize default categories and budgets
        self._init_default_data(cursor)
        conn.commit()
        conn.close()
    
    def _init_default_data(self, cursor):
        """Initialize default categories and budgets"""
        # Check if categories already exist
        cursor.execute("SELECT COUNT(*) as count FROM categories")
        if cursor.fetchone()['count'] == 0:
            # Add default categories
            now = format_datetime(datetime.now())
            for cat_type, categories in DEFAULT_CATEGORIES.items():
                for cat_name in categories:
                    cursor.execute('''
                        INSERT INTO categories (id, name, type, created_at)
                        VALUES (?, ?, ?, ?)
                    ''', (generate_uuid(), cat_name, cat_type, now))
        
        # Check if budgets already exist
        cursor.execute("SELECT COUNT(*) as count FROM budgets")
        if cursor.fetchone()['count'] == 0:
            # Add default budgets
            now = format_datetime(datetime.now())
            for category, limit in DEFAULT_MONTHLY_BUDGET.items():
                cursor.execute('''
                    INSERT INTO budgets (id, category, monthly_limit, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (generate_uuid(), category, limit, now, now))
        
        # Initialize sync metadata
        cursor.execute("SELECT COUNT(*) as count FROM sync_metadata")
        if cursor.fetchone()['count'] == 0:
            cursor.execute('''
                INSERT INTO sync_metadata (last_sync, sync_status, sync_message)
                VALUES (?, ?, ?)
            ''', (None, 'never', 'Not synced yet'))
    
    # ==================== TRANSACTION OPERATIONS ====================
    
    def add_transaction(self, date, category, trans_type, amount, description=""):
        """Add a new transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        trans_id = generate_uuid()
        now = format_datetime(datetime.now())
        
        cursor.execute('''
            INSERT INTO transactions (id, date, category, type, amount, description, created_at, updated_at, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (trans_id, date, category, trans_type, amount, description, now, now))
        
        conn.commit()
        conn.close()
        return trans_id
    
    def update_transaction(self, trans_id, date=None, category=None, trans_type=None, amount=None, description=None):
        """Update an existing transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        updates = []
        params = []
        
        if date is not None:
            updates.append("date = ?")
            params.append(date)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if trans_type is not None:
            updates.append("type = ?")
            params.append(trans_type)
        if amount is not None:
            updates.append("amount = ?")
            params.append(amount)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(format_datetime(datetime.now()))
            updates.append("synced = 0")  # Mark as unsynced
            params.append(trans_id)
            
            query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    def delete_transaction(self, trans_id):
        """Delete a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
        conn.commit()
        conn.close()
    
    def get_transaction(self, trans_id):
        """Get a single transaction by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (trans_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def get_all_transactions(self, start_date=None, end_date=None, trans_type=None, category=None):
        """Get all transactions with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if trans_type:
            query += " AND type = ?"
            params.append(trans_type)
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY date DESC, created_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_recent_transactions(self, limit=10):
        """Get most recent transactions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions 
            ORDER BY date DESC, created_at DESC 
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    # ==================== AGGREGATION QUERIES ====================
    
    def get_total_by_type(self, trans_type, start_date=None, end_date=None):
        """Get total amount by transaction type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = ?"
        params = [trans_type]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result['total'] if result else 0
    
    def get_category_breakdown(self, trans_type, start_date=None, end_date=None):
        """Get spending/income breakdown by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM transactions 
            WHERE type = ?
        '''
        params = [trans_type]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " GROUP BY category ORDER BY total DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def get_monthly_summary(self, year_month):
        """Get monthly income and expense summary"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        start_date = f"{year_month}-01"
        # Get last day of month
        if year_month.endswith("12"):
            year = int(year_month.split("-")[0]) + 1
            end_date = f"{year}-01-01"
        else:
            year, month = year_month.split("-")
            next_month = int(month) + 1
            end_date = f"{year}-{next_month:02d}-01"
        
        cursor.execute('''
            SELECT 
                type,
                SUM(amount) as total
            FROM transactions
            WHERE date >= ? AND date < ?
            GROUP BY type
        ''', (start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        
        summary = {"income": 0, "expense": 0}
        for row in results:
            summary[row['type']] = row['total']
        
        return summary
    
    # ==================== BUDGET OPERATIONS ====================
    
    def get_budget(self, category):
        """Get budget for a category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budgets WHERE category = ?", (category,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def get_all_budgets(self):
        """Get all budgets"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budgets ORDER BY category")
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def update_budget(self, category, monthly_limit):
        """Update budget for a category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = format_datetime(datetime.now())
        
        cursor.execute('''
            INSERT OR REPLACE INTO budgets (id, category, monthly_limit, created_at, updated_at)
            VALUES (
                COALESCE((SELECT id FROM budgets WHERE category = ?), ?),
                ?, ?, 
                COALESCE((SELECT created_at FROM budgets WHERE category = ?), ?),
                ?
            )
        ''', (category, generate_uuid(), category, monthly_limit, category, now, now))
        
        conn.commit()
        conn.close()
    
    # ==================== CATEGORY OPERATIONS ====================
    
    def get_categories(self, cat_type=None):
        """Get all categories, optionally filtered by type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if cat_type:
            cursor.execute("SELECT * FROM categories WHERE type = ? ORDER BY name", (cat_type,))
        else:
            cursor.execute("SELECT * FROM categories ORDER BY type, name")
        
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def add_category(self, name, cat_type):
        """Add a new category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cat_id = generate_uuid()
        now = format_datetime(datetime.now())
        
        try:
            cursor.execute('''
                INSERT INTO categories (id, name, type, created_at)
                VALUES (?, ?, ?, ?)
            ''', (cat_id, name, cat_type, now))
            conn.commit()
            conn.close()
            return cat_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # Category already exists
    
    # ==================== SYNC OPERATIONS ====================
    
    def get_unsynced_transactions(self):
        """Get all transactions that haven't been synced"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE synced = 0")
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def mark_transactions_synced(self, trans_ids):
        """Mark transactions as synced"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(trans_ids))
        cursor.execute(f"UPDATE transactions SET synced = 1 WHERE id IN ({placeholders})", trans_ids)
        
        conn.commit()
        conn.close()
    
    def update_sync_metadata(self, status, message):
        """Update sync metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = format_datetime(datetime.now())
        
        cursor.execute('''
            UPDATE sync_metadata 
            SET last_sync = ?, sync_status = ?, sync_message = ?
            WHERE id = 1
        ''', (now, status, message))
        
        conn.commit()
        conn.close()
    
    def get_sync_metadata(self):
        """Get sync metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sync_metadata WHERE id = 1")
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def export_all_data(self):
        """Export all data for backup"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        data = {
            "transactions": [],
            "budgets": [],
            "categories": []
        }
        
        cursor.execute("SELECT * FROM transactions")
        data["transactions"] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM budgets")
        data["budgets"] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM categories")
        data["categories"] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return data
    
    def import_data(self, data):
        """Import data from backup (merge with existing)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Import transactions
        for trans in data.get("transactions", []):
            cursor.execute('''
                INSERT OR REPLACE INTO transactions 
                (id, date, category, type, amount, description, created_at, updated_at, synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (trans['id'], trans['date'], trans['category'], trans['type'], 
                  trans['amount'], trans.get('description', ''), trans['created_at'], 
                  trans['updated_at'], trans.get('synced', 1)))
        
        # Import budgets
        for budget in data.get("budgets", []):
            cursor.execute('''
                INSERT OR REPLACE INTO budgets 
                (id, category, monthly_limit, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (budget['id'], budget['category'], budget['monthly_limit'], 
                  budget['created_at'], budget['updated_at']))
        
        # Import categories
        for cat in data.get("categories", []):
            cursor.execute('''
                INSERT OR IGNORE INTO categories 
                (id, name, type, created_at)
                VALUES (?, ?, ?, ?)
            ''', (cat['id'], cat['name'], cat['type'], cat['created_at']))
        
        conn.commit()
        conn.close()
