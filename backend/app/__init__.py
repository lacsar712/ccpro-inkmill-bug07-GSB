from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import settings
from app.routes import auth, dashboard, grind_passes, mills, viscosity_samples, workshops


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = settings.jwt_secret
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.jwt_access_token_expires

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def _unauthorized(_reason):
        return jsonify({"message": "未登录或登录已过期"}), 401

    @jwt.invalid_token_loader
    def _invalid(_reason):
        return jsonify({"message": "未登录或登录已过期"}), 401

    @jwt.expired_token_loader
    def _expired(_jwt_header, _jwt_data):
        return jsonify({"message": "未登录或登录已过期"}), 401

    @app.after_request
    def _no_store_api(resp):
        # 台账/统计接口一律不走缓存，确保改状态后立即拉取到最新提交值。
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(workshops.bp)
    app.register_blueprint(mills.bp)
    app.register_blueprint(viscosity_samples.bp)
    app.register_blueprint(grind_passes.bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "InkMill"})

    return app
