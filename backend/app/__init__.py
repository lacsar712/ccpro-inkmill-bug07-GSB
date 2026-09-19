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

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(workshops.bp)
    app.register_blueprint(mills.bp)
    app.register_blueprint(viscosity_samples.bp)
    app.register_blueprint(grind_passes.bp)

    @app.after_request
    def _no_store_api(response):
        # 所有台账数据实时查库，禁止浏览器/中间缓存，避免切页后看到旧数。
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "InkMill"})

    return app
