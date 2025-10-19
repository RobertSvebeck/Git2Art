"""Flask application factory for Git2Art web application."""

from flask import Flask
import os


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    app.config['GENERATED_IMAGES_DIR'] = os.path.join(app.root_path, 'static', 'generated')
    app.config['TEMP_REPOS_DIR'] = os.path.join(app.root_path, 'temp_repos')

    # Ensure directories exist
    os.makedirs(app.config['GENERATED_IMAGES_DIR'], exist_ok=True)
    os.makedirs(app.config['TEMP_REPOS_DIR'], exist_ok=True)

    # Register routes
    from routes import main_routes
    app.register_blueprint(main_routes.bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)
