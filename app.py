from flask import Flask
from dotenv import load_dotenv  # ⭐ 新增
import os  # ⭐ 新增
import secrets

from backend.database.database import login_required, User, db, init_db
from backend.routes import register_routes
from backend.session_config import configure_session

# ⭐ 讀取 .env 檔案
load_dotenv()

# 創建 Flask 應用
app = Flask(__name__, template_folder="templates", static_folder="static")

# 設置秘鑰以加密會話（從.env讀取，如果沒有就自動生成）
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

# 配置會話參數
configure_session(app)

# 配置資料庫URI，這裡使用SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
init_db(app)

# 註冊所有路由
register_routes(app)

if __name__ == "__main__":
    # ⭐ 從.env讀取port（沒有就預設5000）
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
