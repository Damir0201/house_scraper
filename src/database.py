import os
import psycopg2
from psycopg2.extras import execute_values

db_host=os.getenv("DB_HOST", "localhost")
db_name=os.getenv("DB_NAME", "house_of_tracks_db")
db_user=os.getenv("DB_USER", "postgres_user")
db_password=os.getenv("DB_PASSWORD", "secure_password")

def get_connection():
  return psycopg2.connect(
      host=db_host, database=db_name, user=db_user, password=db_password
  )

def init_db():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            genre VARCHAR(100),
            price VARCHAR(50),
            track_url TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
  cursor.execute("""
                 CREATE TABLE IF NOT EXISTS users
                 (
                     chat_id BIGINT PRIMARY KEY,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )
                 """)
  conn.commit()
  cursor.close()
  conn.close()

def save_new_tracks(tracks_list):
  conn = get_connection()
  cursor = conn.cursor()

  new_tracks = []
  for track in tracks_list:
    try:
      cursor.execute(
          """
                INSERT INTO tracks (title, genre, price, track_url)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (track_url) DO NOTHING
                RETURNING id;
            """,
          (
              track["title"],
              track["genre"],
              track["price"],
              track["track_url"],
          ),
      )
      result = cursor.fetchone()
      if result:
        new_tracks.append(track)
    except Exception as e:
      print(f"Error on saving track {e}")

  conn.commit()
  cursor.close()
  conn.close()
  return new_tracks

def add_user(chat_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (chat_id) VALUES (%s)
        ON CONFLICT (chat_id) DO NOTHING
    """, (chat_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]
def get_latest_tracks(limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT title, genre, price, track_url
                   FROM tracks
                   ORDER BY id DESC
                       LIMIT %s
                   """, (limit,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"title": r[0], "genre": r[1], "price": r[2], "track_url": r[3]} for r in rows]

if __name__ == "__main__":
  init_db()
  print("Database initialized")