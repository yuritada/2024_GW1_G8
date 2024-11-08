from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from db import get_db_connection, close_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理用の秘密鍵

# @app.route('/')
# def home():
#     """ホームページ"""
#     return render_template('index.html')

@app.route('/')
def home():
    """ホームページ"""
    # ここでreviewsのデータを用意
    reviews = [
        {'visited': '東京', 'place': '浅草', 'attitude': '良い', 'price': '安い', 'speed': '早い'},
        {'visited': '京都', 'place': '金閣寺', 'attitude': '普通', 'price': '高い', 'speed': '遅い'},
    ]
    return render_template('index.html', reviews=reviews)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザー登録"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # データベース接続
        conn = get_db_connection()
        cursor = conn.cursor()

        # ユーザーが既に存在するかチェック
        cursor.execute("SELECT * FROM user_map WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "このユーザー名はすでに使われています"
        
        # 新しいユーザーをデータベースに挿入
        cursor.execute("INSERT INTO user_map (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

        # 接続を閉じる
        close_db_connection(conn)

        return redirect(url_for('login'))  # ログインページにリダイレクト

    return render_template('register.html')  # ユーザー登録フォームを表示

@app.route('/logout')
def logout():
    """ユーザーのログアウト"""
    session.pop('user_id', None)  # セッションからユーザーIDを削除
    return redirect(url_for('home'))  # ホームページにリダイレクト

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ユーザーログイン"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # データベース接続
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user_map WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        # 接続を閉じる
        close_db_connection(conn)

        if user:
            session['user_id'] = user[0]  # ユーザーIDをセッションに保存
            return redirect(url_for('profile'))
        else:
            return "ログイン失敗"

    return render_template('login.html')

@app.route('/profile')
def profile():
    """ユーザーのプロフィールページ"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM evaluation WHERE user_id = ?", (user_id,))
    evaluations = cursor.fetchall()

    # 接続を閉じる
    close_db_connection(conn)

    return render_template('profile.html', evaluations=evaluations) 

@app.route('/add', methods=['GET', 'POST'])
def add():
    """レビューを追加"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        visited = request.form['visited']
        place = request.form['place']
        attitude = request.form['attitude']
        price = request.form['price']
        speed = request.form['speed']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO evaluation (user_id, visited, place, attitude, price, speed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, visited, place, attitude, price, speed))

        conn.commit()

        # 接続を閉じる
        close_db_connection(conn)

        return redirect(url_for('profile'))

    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True ,use_reloader=True)