from flask import Flask
import secrets
from backend.database.database import login_required, User, db, init_db
from backend.routes import register_routes
from backend.session_config import configure_session

# 創建 Flask 應用
app = Flask(__name__, template_folder="templates", static_folder="static")

# 設置秘鑰以加密會話
app.secret_key = secrets.token_hex(32)

# 配置會話參數
configure_session(app)

# 配置資料庫URI，這裡使用SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
init_db(app)

# 註冊所有路由
register_routes(app)

if __name__ == '__main__':
    # 開啟debug模式以便開發時使用
    app.run(debug=True)
