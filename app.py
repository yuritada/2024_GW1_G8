from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from db import get_db_connection, close_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理用の秘密鍵

userid = 0

# @app.route('/')
# def home():
#     """ホームページ"""
#     return render_template('index.html')

# データベースから全ての口コミを取得
def get_reviews(Calum,db_name):
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    c.execute(f'SELECT {Calum} FROM {db_name}')
    print(c.fetchall())
    reviews = c.fetchall()
    conn.close()
    return reviews

# 口コミ一覧ページ
@app.route('/')
def home():
    a = get_reviews("*","evaluation")
    return render_template('index.html', evaluation=a)

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
    global userid
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
            userid = user[0]
            return redirect(url_for('profile'))
        else:
            return "ログイン失敗"

    return render_template('login.html')

@app.route('/profile')
def profile():
    """ユーザーのプロフィールページ"""
    # ログインしていない場合、ログインページにリダイレクト
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # データベース接続の確立
    conn = get_db_connection()
    cursor = conn.cursor()

    # 全てのユーザー情報を取得
    user_map = get_reviews("user_id, username", "user_map")

    # ログイン中のユーザーの評価情報を取得
    cursor.execute("SELECT * FROM evaluation WHERE user_id = ?", (user_id,))
    evaluation = cursor.fetchall()

    # ユーザーIDに対応するユーザーネームを取得
    cursor.execute("SELECT username FROM user_map WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    username = result[0] if result else "Unknown"

    # データベース接続を閉じる
    conn.close()

    # テンプレートにデータを渡してレンダリング
    return render_template('profile.html', evaluation=evaluation, user_map=user_map, username=username)

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

# @app.route('/index')
# def index():
#     """口コミ一覧ページ"""
#     # ログインしているかチェック
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     user_id = session['user_id']
    
#     # データベース接続
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # 現在のユーザーの評価データを取得
#     cursor.execute("SELECT visited, place, attitude, price, speed FROM evaluation WHERE user_id = ?", (user_id,))
#     reviews = cursor.fetchall()

#     # データを辞書形式に変換
#     reviews_list = [{'visited': r[0], 'place': r[1], 'attitude': r[2], 'price': r[3], 'speed': r[4]} for r in reviews]

#     # 接続を閉じる
#     close_db_connection(conn)

#     return render_template('index.html', reviews=reviews_list)

if __name__ == '__main__':
    app.run(debug=True ,use_reloader=True)