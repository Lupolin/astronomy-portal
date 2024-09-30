from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import secrets
from flask_sqlalchemy import SQLAlchemy
import requests
import bcrypt # 帳號密碼加密


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# 配置資料庫URI，這裡使用SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
db = SQLAlchemy(app)

# NASA API 金鑰
NASA_API_KEY = 'NeBwtfWqeNneNUgh4TYQmCbcWbcyD2iy1bkBalYN'  # 替換成您自己的 API 金鑰
NASA_APOD_URL = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}'

# 定義使用者模型（用來表示使用者表）
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# 創建資料庫和表
with app.app_context():
    db.create_all()

# 驗證使用者是否已經登錄的裝飾器
def login_required(f):
    def wrap(*args, **kwargs):
        if 'username' not in session:
            flash('You need to login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/')
def home():
    return redirect(url_for('signup'))  # 註冊頁面作為首頁

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 在資料庫中查詢使用者
        user = User.query.filter_by(username=username).first()

        # 驗證密碼
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode()):
            session['username'] = username  # 記錄使用者會話
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 檢查使用者是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!')
            return redirect(url_for('signup'))
        else:
            # 密碼加密
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # 創建新使用者並保存到資料庫
            new_user = User(username=username, password=hashed_password.decode('utf-8'))
            db.session.add(new_user)
            db.session.commit()

            # 註冊成功後自動登錄
            session['username'] = username
            flash('Sign up successful! You are now logged in.')
            return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/admin/users')
@login_required  # 限制只有登錄的使用者可以訪問
def show_users():
    # 從資料庫中查詢所有使用者
    users = User.query.all()
    
    # 將使用者清單傳遞給模板進行顯示
    return render_template('show_users.html', users=users)


@app.route('/dashboard')
@login_required  # 限制只有登錄用戶才能訪問
def dashboard():
    return render_template('dashboard.html')

# 調用 NASA API 並返回天文每日一圖數據給前端
@app.route('/api/nasa/apod', methods=['GET'])
@login_required  # 限制只有登錄用戶才能訪問
def get_apod():
    response = requests.get(NASA_APOD_URL)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Unable to fetch data from NASA API'}), 500

@app.route('/logout')
def logout():
    session.pop('username', None)  # 清除使用者會話
    flash('You have been logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
