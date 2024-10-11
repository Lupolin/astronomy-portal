# session_config.py
from flask import Flask
from flask_session import Session

def configure_session(app: Flask):
    app.secret_key = 'your_secret_key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 設置 session 過期時間為 1 天
    Session(app)
