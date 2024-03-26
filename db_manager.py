import mysql.connector
import re
from datetime import datetime

DB_NAME = 'neteye'

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
RULES_COL_TARGET_DEVICE = 'target'

EMAILS_TABLE_NAME = 'emails'
EMAILS_COL_ID = 'id'
EMAILS_COL_ADDRESS = 'email'
EMAILS_COL_NAME = 'name'

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
            {NOTIFICATIONS_COL_DESCRIPTION} VARCHAR(255),
            {NOTIFICATIONS_COL_DATE} DATETIME,
            {NOTIFICATIONS_COL_IS_READ} BOOL)
    ''')

def is_rules_table(cursor):
    create_table_if_not_exists(cursor, RULES_TABLE_NAME, f'''
        CREATE TABLE {RULES_TABLE_NAME} (
            {RULES_COL_ID} INT AUTO_INCREMENT PRIMARY KEY,
            {RULES_COL_NAME} VARCHAR(255) UNIQUE,
            {RULES_COL_ACTION} INT,
            {RULES_COL_PARAMETER} INT,
            {RULES_COL_AMOUNT} INT,
            {RULES_COL_TARGET_DEVICE} VARCHAR(255))
    ''')

def is_emails_table(cursor):
    create_table_if_not_exists(cursor, EMAILS_TABLE_NAME, f'''
        CREATE TABLE {EMAILS_TABLE_NAME} (
            {EMAILS_COL_ID} INT AUTO_INCREMENT PRIMARY KEY,
            {EMAILS_COL_ADDRESS} VARCHAR(255) UNIQUE,
            {EMAILS_COL_NAME} VARCHAR(255))
    ''')

def connect_to_db():
    return mysql.connector.connect(
        host='localhost',
        user='admin',
        password='admin',
        database=DB_NAME)

def create_database():
    try:
        with mysql.connector.connect(host='localhost',user='admin',password='admin') as conn:
            cursor = conn.cursor()
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS {DB_NAME}')

    except Exception as e:
        print(f"Error creating database: {e}")

def insert_rule(name, parameter, action, amount, target):
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            insert_query = f'''
                INSERT INTO {RULES_TABLE_NAME} 
                ({RULES_COL_NAME}, {RULES_COL_PARAMETER}, {RULES_COL_ACTION}, {RULES_COL_AMOUNT}, {RULES_COL_TARGET_DEVICE})
                VALUES (%s, %s, %s, %s, %s)'''

            cursor.execute(insert_query, (name, parameter, action, amount, target))
            conn.commit()
            print("Rule inserted successfully!")

    except Exception as e:
        print(f"Error inserting rule: {e}")

def print_emails_table():
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            for email in get_emails():
                print(f"{EMAILS_COL_ADDRESS}: {email[1]}, {EMAILS_COL_ID}: {email[0]}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    except Exception as e:
        print(f"Error when printing emails table: {e}")

def is_valid_email(email):
    # Use a regular expression to check if the email format is valid
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def insert_email(email, name):
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            if is_valid_email(email):
                insert_query = f"INSERT INTO {EMAILS_TABLE_NAME} ({EMAILS_COL_ADDRESS}, {EMAILS_COL_NAME}) VALUES (%s, %s)"
                cursor.execute(insert_query, (email, name,))
                conn.commit()

                print(f"'{name}' email '{email}' added successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    except Exception as e:
        print(f"Error when inserting mail: {e}")

def remove_email(email):
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()
          
            delete_query = f"DELETE FROM {EMAILS_TABLE_NAME} WHERE {EMAILS_COL_ADDRESS} = %s"
            cursor.execute(delete_query, (email,))

            conn.commit()

            if cursor.rowcount > 0:
                print(f"Email '{email}' removed successfully!")
            else:
                print(f"Email '{email}' not found in the table.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    except Exception as e:
        print(f"Error when removing email: {e}")

def changes_in_emails_table():
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            choice = -1
            while choice != '0':
                print_emails_table(cursor)
                choice = input("Which action would you like to do? \n0. Exit. \n1. Insert email. \n2. Remove email.\n")
                if choice == '1':
                    email = input("Enter the email to add to the table: ")

                    if not is_valid_email(email):
                        print("Invalid email format. Please enter a valid email.")
                    else:
                        insert_email(cursor, conn, email)

                if choice == '2':
                    email = input("Enter the email to remove from the table: ")
                    
                    if not is_valid_email(email):
                        print("Invalid email format. Please enter a valid email.")
                    else:
                        remove_email(email)

                print()

    except Exception as e:
        print(f"Error making changes in emails table: {e}")

def insert_notification(name, type, description, date, is_read):
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            insert_query = f'''
                INSERT INTO {NOTIFICATIONS_TABLE_NAME} 
                ({NOTIFICATIONS_COL_NAME}, {NOTIFICATIONS_COL_TYPE}, {NOTIFICATIONS_COL_DESCRIPTION}, {NOTIFICATIONS_COL_DATE}, {NOTIFICATIONS_COL_IS_READ})
                VALUES (%s, %s, %s, %s, %s)'''

            cursor.execute(insert_query, (name, type, description, date, is_read))
            conn.commit()

            get_id_query = f"SELECT {NOTIFICATIONS_COL_ID} FROM {NOTIFICATIONS_TABLE_NAME} ORDER BY {NOTIFICATIONS_COL_ID} DESC LIMIT 1"
            cursor.execute(get_id_query)
            return cursor.fetchall()[0]

    except Exception as e:
        print(f"Error inserting notification: {e}")

def remove_notification(notification_id):
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            delete_query = f"DELETE FROM {NOTIFICATIONS_TABLE_NAME} WHERE {NOTIFICATIONS_COL_ID} = %s"
            cursor.execute(delete_query, (notification_id,))

            conn.commit()

            if cursor.rowcount > 0:
                print(f"Notification with ID {notification_id} removed successfully!")
            else:
                print(f"Notification with ID {notification_id} not found in the table.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    except Exception as e:
        print(f"Error when removing notification: {e}")

def get_rules():
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM {RULES_TABLE_NAME} ORDER BY {RULES_COL_ID}")
            rows = cursor.fetchall()
            return rows

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    except Exception as e:
        print(f"Error getting rules: {e}")

def get_notifications():
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM {NOTIFICATIONS_TABLE_NAME} ORDER BY {NOTIFICATIONS_COL_DATE} DESC")
            rows = cursor.fetchall()

            list_rows = []

            for row in rows:
                list_rows.append(list(row))
            
            for list_row in list_rows:
                if list_row[5] == 0:
                    list_row[5] = False

                else:
                    list_row[5] = True

            return list_rows

    except mysql.connector.Error as err:
        return f"Error: {err}"

    except Exception as e:
        return f"Error getting notifications: {e}"

def get_emails():
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM {EMAILS_TABLE_NAME} ORDER BY {EMAILS_COL_NAME}")
            rows = cursor.fetchall()
            return rows

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    except Exception as e:
        print(f"Error getting emails: {e}")

def remove_rule(rule_name):
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            delete_query = f"DELETE FROM {RULES_TABLE_NAME} WHERE {RULES_COL_NAME} = %s"
            cursor.execute(delete_query, (rule_name,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"Rule {rule_name} removed successfully!")
            else:
                print(f"Rule {rule_name} not found in the table.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    except Exception as e:
        print(f"Error removing rule: {e}")


def main():
    create_database()
    
    # get_emails()
    # insert_email('savva@gmail.com', 'Savva Spiridonov')
    # insert_email('yosi@gmail.com', 'Yosi Hagever')
    # insert_rule('Good Rulegggggg', 3, 1, 60, "192.168.1.1")
    # remove_notification(4)
    # insert_notification('Sample Notificationnnnnn', 'Network Problem', 'High latency', datetime.now(), False)
    # print(get_notifications())
    

    with connect_to_db() as conn:
        cursor = conn.cursor()

        is_devices_table(cursor)
        is_notifications_table(cursor)
        is_rules_table(cursor)
        is_emails_table(cursor)


    # changes_in_emails_table()

if __name__ == '__main__':
    main()
