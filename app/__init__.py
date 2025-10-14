# app/__init__.py
import os
from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import text

from .config import Config
from app.db.db import Base, engine

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ----- Config -----
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key-change-this")
    app.config.from_object(Config)

    # ----- Uploads -----
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads", "equipment")
    app.config["ALLOWED_IMAGE_EXT"] = {"jpg", "jpeg", "png", "gif", "webp"}
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ----- Blueprints -----
    from .blueprints.pages import pages_bp
    from .blueprints.auth import auth_bp
    from .blueprints.inventory import inventory_bp
    from .blueprints.tracking import tracking_bp
    from app.blueprints.admin.routes import admin_bp, admin_users_bp, admin_history_bp
    from app.blueprints.history.routes import history_bp
    from app.blueprints.inventory.api_equipment import api_equipment_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp)
    app.register_blueprint(tracking_bp, url_prefix="/track-status")
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_history_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(api_equipment_bp)

    # ----- DB bootstrap -----
    with app.app_context():
        from app.db import models  # noqa: F401
        with engine.begin() as conn:
            try:
                if engine.dialect.name == "postgresql":
                    conn.execute(text("SELECT pg_advisory_lock(987654321)"))
                Base.metadata.create_all(bind=conn)
            finally:
                if engine.dialect.name == "postgresql":
                    conn.execute(text("SELECT pg_advisory_unlock(987654321)"))

    # ----- Health check -----
    @app.get("/healthz")
    def healthz():
        return {"ok": True}, 200

    # ----- Root redirect (เลือกหน้าที่มีอยู่จริง) -----
    @app.get("/")
    def _root():
        from flask import redirect, url_for
        for endpoint in ("pages.home", "admin.admin_home", "inventory.lend", "tracking.track_index"):
            try:
                return redirect(url_for(endpoint))
            except Exception:
                pass
        return {"status": "ok", "hint": "No landing page found."}, 200

    # ✅ สำคัญ: ต้อง return app
    return app
