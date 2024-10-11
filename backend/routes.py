from flask import render_template, request, redirect, url_for, flash, session
from database.user_account import login_required, User, db
import bcrypt  # 帳號密碼加密
from nasa_api import get_apod_data

def register_routes(app):
    @app.route('/')
    @login_required  # 確保只有已登入的使用者可以訪問
    def home():
        return render_template('home.html', current_page='home')

    @app.route('/telescopes')
    @login_required
    def telescopes():
        return render_template('telescopes.html', current_page='telescopes')

    @app.route('/planets')
    @login_required
    def planets():
        return render_template('planets.html', current_page='planets')

    @app.route('/galaxies')
    @login_required
    def galaxies():
        return render_template('galaxies.html', current_page='galaxies')    

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
                session.permanent = True # 設置 session 為永久性
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password')
                return redirect(url_for('login'))
        
        # 傳遞 'tab' 參數
        return render_template('login_signup.html', tab="Login")

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists!')
                return redirect(url_for('signup'))
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                new_user = User(username=username, password=hashed_password.decode('utf-8'))
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash('Sign up successful! You are now logged in.')
                return redirect(url_for('home'))
        return render_template('signup.html')

    @app.route('/admin/users')
    @login_required
    def show_users():
        # 從資料庫中查詢所有使用者
        users = User.query.all()
        # 將使用者清單傳遞給模板進行顯示
        return render_template('show_users.html', users=users)

    @app.route('/api/nasa/apod', methods=['GET'])
    @login_required
    def api_nasa_apod():
        return get_apod_data()

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        flash('You have been logged out')
        return redirect(url_for('login'))
