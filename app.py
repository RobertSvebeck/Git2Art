"""Flask application factory for Git2Art web application."""

from flask import Flask
import os

ONE_WEEK = 7 * 24 * 3600
CACHED_EXTENSIONS = ('.webp', '.png', '.jpg', '.jpeg', '.json', '.ico', '.svg')


class Git2ArtFlask(Flask):
    """Lets browsers keep pictures and repo data for a week.

    Every request that reaches Python holds one of the hosting account's 30
    entry processes, so a revalidation per picture per visit adds up. Scripts
    and stylesheets still revalidate (no-cache), so a deploy never mixes old
    and new 3D museum modules.
    """

    def get_send_file_max_age(self, filename):
        if filename and filename.lower().endswith(CACHED_EXTENSIONS):
            return ONE_WEEK
        return super().get_send_file_max_age(filename)


def create_app():
    """Create and configure the Flask application."""
    app = Git2ArtFlask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    app.config['GENERATED_IMAGES_DIR'] = os.path.join(app.root_path, 'static', 'generated')
    app.config['TEMP_REPOS_DIR'] = os.path.join(app.root_path, 'temp_repos')
    app.config['PAGE_CACHE_DIR'] = os.path.join(app.root_path, 'page_cache')

    # Ensure directories exist
    os.makedirs(app.config['GENERATED_IMAGES_DIR'], exist_ok=True)
    os.makedirs(app.config['TEMP_REPOS_DIR'], exist_ok=True)
    os.makedirs(app.config['PAGE_CACHE_DIR'], exist_ok=True)

    @app.url_defaults
    def version_static_files(endpoint, values):
        """Add ?v=<mtime> to static URLs: LiteSpeed lets browsers keep them for
        a week, so a changed file needs a new address to be fetched again."""
        if endpoint != 'static' or 'v' in values or 'filename' not in values:
            return
        try:
            values['v'] = int(os.path.getmtime(os.path.join(app.static_folder, values['filename'])))
        except OSError:
            pass

    # Register routes
    from routes import main_routes
    app.register_blueprint(main_routes.bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False, port=5001)
