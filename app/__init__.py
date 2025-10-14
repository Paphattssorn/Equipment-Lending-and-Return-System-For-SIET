import os
from flask import Flask
from dotenv import load_dotenv
from .config import Config

# โหลดค่าจากไฟล์ .env เฉพาะตอน dev
load_dotenv()

# ✅ import DB Base + engine สำหรับสร้างตาราง
from app.db.db import Base, engine


def create_app():
    # ===== Flask App =====
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ===== Secret Key =====
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key-change-this")

    # ===== Config =====
    app.config.from_object(Config)

    # ===== Upload config =====
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads', 'equipment')
    app.config['ALLOWED_IMAGE_EXT'] = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ===== Register blueprints =====
    from .blueprints.pages import pages_bp
    from .blueprints.auth import auth_bp
    from .blueprints.inventory import inventory_bp
    from .blueprints.tracking import tracking_bp
    from app.blueprints.admin.routes import admin_bp, admin_users_bp, admin_history_bp
    from app.blueprints.pages.routes import pages_bp
    from app.blueprints.history.routes import history_bp
    from app.blueprints.inventory.api_equipment import api_equipment_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp)
    app.register_blueprint(tracking_bp, url_prefix="/track-status")
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_history_bp)
    app.register_blueprint(api_equipment_bp)

    # ===== สร้างตาราง DB ครั้งแรก (สำคัญมาก) =====
    with app.app_context():
        from app.db import models  # ✅ ต้อง import models ก่อน create_all()
        Base.metadata.create_all(bind=engine)

    # ===== Health check สำหรับ Railway =====
    @app.get("/healthz")
    def healthz():
        return {"ok": True}, 200

    return app