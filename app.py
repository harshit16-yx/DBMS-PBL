from flask import Flask, render_template
from datetime import datetime
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Custom Jinja filters for clean formatting
    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return f"₹{value}"

    @app.template_filter("datetime_format")
    def datetime_format_filter(value, fmt="%d %b %Y, %I:%M %p"):
        if not value:
            return ""
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
                return dt.strftime(fmt)
            except Exception:
                return value
        if isinstance(value, datetime):
            return value.strftime(fmt)
        return str(value)

    @app.template_filter("date_only")
    def date_only_filter(value, fmt="%d %b %Y"):
        if not value:
            return ""
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
                return dt.strftime(fmt)
            except Exception:
                return value
        if isinstance(value, datetime):
            return value.strftime(fmt)
        return str(value)

    # Register blueprints
    from routes.main import main_bp
    from routes.booking import booking_bp
    from routes.admin import admin_bp
    from routes.passengers import passengers_bp
    from routes.reports import reports_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(booking_bp, url_prefix="/booking")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(passengers_bp, url_prefix="/passengers")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("500.html", error=str(e)), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
