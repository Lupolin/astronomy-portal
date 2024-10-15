from flask import render_template, request, redirect, url_for, flash, session
from backend.database.database import login_required, User, db
import bcrypt  # 用于密码加密
from .nasa_api import get_apod_data
from datetime import datetime  # 用于时间戳
from backend.database.database import Comment  # 确保 Comment 模型已经导入

def register_routes(app):
    @app.route('/')
    @login_required  # 确保只有已登录的用户可以访问
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

    @app.route('/galaxies', methods=['GET'])
    @login_required  # 可以根据需求设置是否需要登录才可以查看评论
    def galaxies():
        # 从数据库中读取所有的评论，并按时间倒序排列
        comments = Comment.query.order_by(Comment.timestamp.desc()).all()
        return render_template('galaxies.html', comments=comments, current_page='galaxies')

    @app.route('/submit_comment', methods=['POST'])
    @login_required  # 确保用户登录才能提交评论
    def submit_comment():
        # 从 session 获取用户名，若无则使用默认用户名 'Anonymous'
        username = session.get('username', 'Anonymous')
        content = request.form.get('content')  # 获取评论内容

        if not content:  # 检查评论内容是否为空
            flash('Comment content cannot be empty!')
            return redirect(url_for('galaxies'))

        # 查找或创建用户
        user = User.query.filter_by(username=username).first()
        if not user:
            # 如果用户不存在则创建新用户
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        # 创建新评论
        try:
            new_comment = Comment(content=content, user_id=user.id, timestamp=datetime.utcnow())
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment has been posted!')
        except Exception as e:
            db.session.rollback()  # 回滚数据库事务
            flash(f"Error submitting your comment: {str(e)}")

        return redirect(url_for('galaxies'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # 在数据库中查找用户
            user = User.query.filter_by(username=username).first()

            # 如果找不到用户，显示 "未註冊" 的提示
            if not user:
                flash('The username is not registered. Please sign up.')
                return redirect(url_for('login'))

            # 如果用戶名存在，繼續檢查密碼
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode()):
                # 如果密碼正確，登錄成功
                session['username'] = username  # 记录用户会话
                session.permanent = True  # 设置 session 为永久性
                return redirect(url_for('home'))
            else:
                # 如果密碼不正確，顯示 "帳號或密碼不正確"
                flash('Invalid username or password')
                return redirect(url_for('login'))

        # 传递 'tab' 参数
        return render_template('login_signup.html', tab="Login")

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # 检查用户名是否已存在
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists!')
                return redirect(url_for('signup'))
            else:
                # 加密密码并创建新用户
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                new_user = User(username=username, password=hashed_password.decode('utf-8'))
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username  # 记录会话
                flash('Sign up successful! You are now logged in.')
                return redirect(url_for('home'))

        return render_template('signup.html')

    @app.route('/admin/users')
    @login_required
    def show_users():
        # 从数据库中查询所有用户
        users = User.query.all()
        # 将用户列表传递给模板进行显示
        return render_template('show_users.html', users=users)

    @app.route('/api/nasa/apod', methods=['GET'])
    @login_required
    def api_nasa_apod():
        return get_apod_data()

    @app.route('/logout')
    def logout():
        session.pop('username', None)  # 移除用户会话
        flash('You have been logged out')
        return redirect(url_for('login'))
