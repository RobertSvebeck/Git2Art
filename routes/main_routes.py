"""Main application routes."""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from services.art_service import generate_art_from_github
from services.git_service import validate_github_url
import os

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Render the main page with the art generation form."""
    return render_template('index.html')


@bp.route('/generate', methods=['POST'])
def generate():
    """Generate artwork from a GitHub repository URL."""
    github_url = request.json.get('github_url')

    if not github_url:
        return jsonify({'error': 'GitHub URL is required'}), 400

    # Validate GitHub URL
    is_valid, error_msg = validate_github_url(github_url)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    try:
        # Generate artwork
        result = generate_art_from_github(
            github_url,
            current_app.config['TEMP_REPOS_DIR'],
            current_app.config['GENERATED_IMAGES_DIR']
        )

        return jsonify({
            'success': True,
            'image_url': result['image_url'],
            'repo_name': result['repo_name'],
            'cached': result['cached']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/download/<filename>')
def download(filename):
    """Download a generated artwork."""
    filepath = os.path.join(current_app.config['GENERATED_IMAGES_DIR'], filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    return send_file(filepath, as_attachment=True)
