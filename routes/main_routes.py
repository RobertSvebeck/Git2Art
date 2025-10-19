"""Main application routes."""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app, session
from services.art_service import generate_art_from_github, get_all_gallery_artworks
from services.git_service import validate_github_url
from models.artwork import ArtworkLike
import os
import hashlib

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Render the main page with the art generation form."""
    return render_template('index.html')


@bp.route('/gallery')
def gallery():
    """Display gallery of all generated artworks."""
    artworks = get_all_gallery_artworks(current_app.config['GENERATED_IMAGES_DIR'])
    return render_template('gallery.html', artworks=artworks)


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


def get_user_identifier():
    """Get or create a unique identifier for the current user."""
    if 'user_id' not in session:
        session['user_id'] = hashlib.md5(os.urandom(32)).hexdigest()
    return session['user_id']


@bp.route('/api/artwork/<int:artwork_id>/like', methods=['POST'])
def like_artwork(artwork_id):
    """Toggle like for an artwork."""
    user_id = get_user_identifier()

    try:
        has_liked = ArtworkLike.has_liked(artwork_id, user_id)

        if has_liked:
            ArtworkLike.remove_like(artwork_id, user_id)
            action = 'unliked'
        else:
            ArtworkLike.add_like(artwork_id, user_id)
            action = 'liked'

        from models.artwork import Artwork
        artwork = Artwork.get_by_id(artwork_id)

        return jsonify({
            'success': True,
            'action': action,
            'like_count': artwork['like_count'] if artwork else 0
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/artwork/<int:artwork_id>/has_liked', methods=['GET'])
def check_has_liked(artwork_id):
    """Check if current user has liked an artwork."""
    user_id = get_user_identifier()

    try:
        has_liked = ArtworkLike.has_liked(artwork_id, user_id)
        return jsonify({'has_liked': has_liked})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
