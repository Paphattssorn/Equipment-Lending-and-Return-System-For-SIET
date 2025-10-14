import os
from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import text

from .config import Config
from app.db.db import Base, engine

# โหลด .env เฉพาะตอน dev
load_dotenv()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ===== Secret Key / Config =====
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key-change-this")
    app.config.from_object(Config)

    # ===== Upload config =====
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads", "equipment")
    app.config["ALLOWED_IMAGE_EXT"] = {"jpg", "jpeg", "png", "gif", "webp"}
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ===== Register Blueprints =====
    from .blueprints.pages import pages_bp                     # home, etc.
    from .blueprints.auth import auth_bp                       # /auth/*
    from .blueprints.inventory import inventory_bp             # /inventory/*
    from .blueprints.tracking import tracking_bp               # /track-status/*
    from app.blueprints.admin.routes import (                  # admin scopes
        admin_bp,
        admin_users_bp,
        admin_history_bp,
    )
    from app.blueprints.history.routes import history_bp       # user history page
    from app.blueprints.inventory.api_equipment import api_equipment_bp  # REST API

    # ✅ Register ให้ครบ
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp)
    app.register_blueprint(tracking_bp, url_prefix="/track-status")
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_history_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(api_equipment_bp)

    # ===== Database bootstrap =====
    with app.app_context():
        from app.db import models  # noqa: F401

        with engine.begin() as conn:
            try:
                conn.execute(text("SELECT pg_advisory_lock(987654321)"))
                Base.metadata.create_all(bind=conn)
            finally:
                conn.execute(text("SELECT pg_advisory_unlock(987654321)"))

    # ===== Health check =====
    @app.get("/healthz")
    def healthz():
        return {"ok": True}, 200

    # ===== Fallback route (เข้าเว็บหลักแล้วไปหน้า home อัตโนมัติ) =====
    @app.get("/")
    def _root():
        from flask import redirect, url_for
        try:
            # 🔍 ใช้ชื่อ endpoint ปกติ 'pages.home' ถ้ามี
            return redirect(url_for("pages.home"))
        except Exception:
            # 🔄 fallback ถ้า blueprint ไม่ได้ชื่อ 'pages'
            return redirect(url_for("home"))

    # ✅ debug: แสดง route ทั้งหมด (ลบออกภายหลังได้)
    print("🧭 URL MAP =", app.url_map)

    return app
