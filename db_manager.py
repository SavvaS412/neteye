import mysql.connector

DB_NAME = 'netEye'

DEVICES_TABLE_NAME = 'devices'
DEVICES_COL_ID = 'id'
DEVICES_COL_NAME = 'name'
DEVICES_COL_IP = 'ip'
DEVICES_COL_MAC = 'mac'
DEVICES_COL_IS_AVAILABLE = 'isAvailable'

NOTIFICATIONS_TABLE_NAME = 'notifications'
NOTIFICATIONS_COL_ID = 'id'
NOTIFICATIONS_COL_NAME = 'name'
NOTIFICATIONS_COL_TYPE = 'type'
NOTIFICATIONS_COL_DESCRIPTION = 'description'
NOTIFICATIONS_COL_DATE = 'date'
NOTIFICATIONS_COL_IS_READ = 'isRead'

RULES_TABLE_NAME = 'rules'
RULES_COL_ID = 'id'
RULES_COL_NAME = 'name'
RULES_COL_ACTION = 'action'
RULES_COL_PARAMETER = 'parameter'
RULES_COL_AMOUNT = 'amount'

EMAILS_TABLE_NAME = 'emails'
EMAILS_COL_ID = 'id'
EMAILS_COL_EMAIL = 'email'

def create_table_if_not_exists(cursor, table_name, table_definition):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    if not cursor.fetchone():
        cursor.execute(table_definition)

def is_devices_table(cursor):
    create_table_if_not_exists(cursor, DEVICES_TABLE_NAME, f'''
            CREATE TABLE {DEVICES_TABLE_NAME} ( 
            {DEVICES_COL_ID} INT AUTO_INCREMENT PRIMARY KEY,
            {DEVICES_COL_NAME} VARCHAR(255),
            {DEVICES_COL_IP} VARCHAR(15),
            {DEVICES_COL_MAC} VARCHAR(17),
            {DEVICES_COL_IS_AVAILABLE} BOOL)
    ''')

def is_notifications_table(cursor):
    create_table_if_not_exists(cursor, NOTIFICATIONS_TABLE_NAME, f'''
        CREATE TABLE {NOTIFICATIONS_TABLE_NAME} (
            {NOTIFICATIONS_COL_ID} INT AUTO_INCREMENT PRIMARY KEY,
            {NOTIFICATIONS_COL_NAME} VARCHAR(255),
            {NOTIFICATIONS_COL_TYPE} VARCHAR(255),
            {NOTIFICATIONS_COL_DESCRIPTION} TEXT,
            {NOTIFICATIONS_COL_DATE} DATETIME,
            {NOTIFICATIONS_COL_IS_READ} BOOL)
    ''')

def is_rules_table(cursor):
    create_table_if_not_exists(cursor, RULES_TABLE_NAME, f'''
        CREATE TABLE {RULES_TABLE_NAME} (
            {RULES_COL_ID} INT AUTO_INCREMENT PRIMARY KEY,
            {RULES_COL_NAME} VARCHAR(255),
            {RULES_COL_ACTION} INT,
            {RULES_COL_PARAMETER} INT,
            {RULES_COL_AMOUNT} INT)
    ''')

def is_emails_table(cursor):
    create_table_if_not_exists(cursor, EMAILS_TABLE_NAME, f'''
        CREATE TABLE {EMAILS_TABLE_NAME} (
            {EMAILS_COL_ID} INT AUTO_INCREMENT PRIMARY KEY,
            {EMAILS_COL_EMAIL} VARCHAR(255) UNIQUE)
    ''')

def connect_to_db():
    return mysql.connector.connect(
        host='localhost',
        user='admin',
        password='admin',
        database=DB_NAME)

def create_database():
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS {DB_NAME}')

    except Exception as e:
        print(f"Error creating database: {e}")

def insert_rule(name, parameter, action, amount):
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            insert_query = f'''
                INSERT INTO {RULES_TABLE_NAME} 
                ({RULES_COL_NAME}, {RULES_COL_PARAMETER}, {RULES_COL_ACTION}, {RULES_COL_AMOUNT})
                VALUES (%s, %s, %s, %s)'''

            cursor.execute(insert_query, (name, parameter, action, amount))
            cursor.connection.commit()
            print("Rule inserted successfully!")

    except Exception as e:
        print(f"Error inserting rule: {e}")

def main():
    create_database()

    with connect_to_db() as conn:
        cursor = conn.cursor()

        is_devices_table(cursor)
        is_notifications_table(cursor)
        is_rules_table(cursor)
        is_emails_table(cursor)

        insert_rule('Sample Rule', 1, 2, 100)

if __name__ == '__main__':
    main()
