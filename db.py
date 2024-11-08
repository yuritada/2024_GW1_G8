import sqlite3

DB_PATH = 'travel.db'

def init_db():
    """データベースを初期化し、必要なテーブルを作成"""
    conn = sqlite3.connect(DB_PATH)  # 新しい接続を開く
    cursor = conn.cursor()

    # ユーザー管理テーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_map (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # 評価テーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluation (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            visited TEXT,
            place INTEGER,
            attitude INTEGER,
            price INTEGER,
            speed INTEGER,
            FOREIGN KEY(user_id) REFERENCES user_map(user_id)
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    """データベース接続を作成し、すぐに閉じることを確実にする"""
    conn = sqlite3.connect(DB_PATH)  # 新しい接続を開く
    return conn

def close_db_connection(conn):
    """データベース接続を閉じる"""
    conn.close()

if __name__ == '__main__':
    init_db()  # 初期化関数を実行