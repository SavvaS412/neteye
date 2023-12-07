import sqlite3

def create_table_if_not_exists(cursor, table_name, table_definition):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if not cursor.fetchone():
        cursor.execute(table_definition)

# Connect to the database (or create if not exists)
with sqlite3.connect('neteye.db') as conn:
    cursor = conn.cursor()

    create_table_if_not_exists(cursor, 'devices', '''
        CREATE TABLE devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ip TEXT,
            mac TEXT,
            isAvailable INTEGER
        )
    ''')

    create_table_if_not_exists(cursor, 'notifications', '''
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            description TEXT,
            date TEXT,
            isRead INTEGER
        )
    ''')

    create_table_if_not_exists(cursor, 'rules', '''
        CREATE TABLE rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            action INTEGER,
            parameter INTEGER,
            amount INTEGER
        )
    ''')

    create_table_if_not_exists(cursor, 'emails', '''
        CREATE TABLE emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE
        )
    ''')