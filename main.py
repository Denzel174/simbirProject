import os
import time
import psycopg2 as ps
import requests
import sys

def create_connection():
    try:
        connection = ps.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),  
            port=os.getenv('DATABASE_PORT', '5432'),
            user=os.getenv('DATABASE_USER', 'myuser'),
            password=os.getenv('DATABASE_PASSWORD', 'password'),
            database=os.getenv('DATABASE_NAME', 'mydatabase')
        )
        return connection
    except ps.OperationalError as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def create_table(connection):
    cursor = connection.cursor()
    joke_tb = '''
    CREATE TABLE IF NOT EXISTS joke_data (
        id INT PRIMARY KEY,
        genre VARCHAR(255) NOT NULL,
        setup VARCHAR(255) NOT NULL,
        punchline VARCHAR(255) NOT NULL
    );
    '''
    cursor.execute(joke_tb)
    connection.commit()
    cursor.close()

def fetch_and_store_joke(connection):
    api_url = 'https://official-joke-api.appspot.com/random_joke'
    try:
        response = requests.get(api_url)
        response.raise_for_status()  
    except requests.RequestException as e:
        print(f"HTTP request failed: {e}")
        return

    joke_data = response.json()
    cursor = connection.cursor()

    id = joke_data['id']
    genre = joke_data['type']
    setup = joke_data['setup']
    punchline = joke_data['punchline']

    try:
        
        cursor.execute('''
        INSERT INTO joke_data (id, genre, setup, punchline)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        ''', (id, genre, setup, punchline))
        connection.commit()
    except ps.Error as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()

def main():
    connection = create_connection()
    create_table(connection)

    try:
        while True:
            fetch_and_store_joke(connection)
            print("New joke is already here")
            time.sleep(300)  
    except KeyboardInterrupt:
        print("Stopping the script.")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main()
