from flask import Flask
import secrets
from database.user_account import init_db
from routes import register_routes
from session_config import configure_session


app = Flask(__name__, template_folder="../templates", static_folder="../static")  # 指定模板文件夾的路徑
app.secret_key = secrets.token_hex(32)
configure_session(app)

# 配置資料庫URI，這裡使用SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
init_db(app)

# 註冊路由
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)