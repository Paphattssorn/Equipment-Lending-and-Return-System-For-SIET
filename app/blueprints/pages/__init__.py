from flask import Blueprint

# ต้องใช้ __name__ ไม่ใช่ name
pages_bp = Blueprint("pages", __name__)

from . import routes  # noqa