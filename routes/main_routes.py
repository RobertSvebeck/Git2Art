"""Main application routes."""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app, session, Response
from services.art_service import generate_art_from_github, get_all_gallery_artworks
from services.git_service import validate_github_url
from models.artwork import ArtworkLike, Artwork
from models import ArtStyle
from datetime import datetime
import os
import hashlib
import base64

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Render the main page with the art generation form."""
    art_styles = ArtStyle.get_active_styles()
    return render_template('index.html', art_styles=art_styles)


@bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')


@bp.route('/privacy')
def privacy():
    """Render the privacy policy page."""
    return render_template('privacy.html')


@bp.route('/terms')
def terms():
    """Render the terms of service page."""
    return render_template('terms.html')


@bp.route('/gallery')
def gallery():
    """Display gallery of all generated artworks."""
    artworks = get_all_gallery_artworks(current_app.config['GENERATED_IMAGES_DIR'])
    art_styles = ArtStyle.get_active_styles()
    return render_template('gallery.html', artworks=artworks, art_styles=art_styles)


@bp.route('/gallery3d')
def gallery3d():
    """Display 3D sphere gallery of all generated artworks."""
    artworks = get_all_gallery_artworks(current_app.config['GENERATED_IMAGES_DIR'])
    art_styles = ArtStyle.get_active_styles()
    return render_template('gallery3d.html', artworks=artworks, art_styles=art_styles)


@bp.route('/artwork/<int:artwork_id>')
def artwork_view(artwork_id):
    """Display full-size artwork view with frame and passepartout."""
    from models.artwork import Artwork

    artwork = Artwork.get_by_id(artwork_id)
    if not artwork:
        return "Artwork not found", 404

    # Build image URL from filename
    image_url = f'/static/generated/{artwork["image_filename"]}'

    art_style = artwork.get('art_style', 'expressionist')
    art_style_name = art_style.replace('_', ' ').title()

    artwork_data = {
        'id': artwork['id'],
        'repo_name': artwork['repo_name'],
        'repo_url': artwork['repo_url'],
        'commit_hash': artwork['commit_hash'],
        'image_url': image_url,
        'like_count': artwork['like_count'],
        'art_style': art_style,
        'art_style_name': art_style_name,
        'created_at_formatted': artwork['created_at'].strftime('%B %d, %Y') if artwork.get('created_at') else 'Unknown'
    }

    return render_template('artwork_view.html', artwork=artwork_data)


@bp.route('/generate', methods=['POST'])
def generate():
    """Generate artwork from a GitHub repository URL."""
    github_url = request.json.get('github_url')
    force_regenerate = request.json.get('force_regenerate', False)
    art_style = request.json.get('art_style', 'expressionist')

    if not github_url:
        return jsonify({'error': 'GitHub URL is required'}), 400

    # Validate GitHub URL
    is_valid, error_msg = validate_github_url(github_url)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    # Validate art style
    if not ArtStyle.is_active(art_style):
        return jsonify({'error': f'Invalid or inactive art style: {art_style}'}), 400

    try:
        # Generate artwork
        result = generate_art_from_github(
            github_url,
            current_app.config['TEMP_REPOS_DIR'],
            current_app.config['GENERATED_IMAGES_DIR'],
            force=force_regenerate,
            art_style=art_style
        )

        return jsonify({
            'success': True,
            'image_url': result['image_url'],
            'repo_name': result['repo_name'],
            'artwork_id': result['artwork_id'],
            'cached': result['cached'],
            'art_style': art_style
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


@bp.route('/api/versions/<repo_url_encoded>', methods=['GET'])
def get_versions(repo_url_encoded):
    """Get all versions for a specific repository."""
    try:
        # Decode the repo URL (it's base64 encoded in the URL)
        repo_url = base64.urlsafe_b64decode(repo_url_encoded).decode('utf-8')

        versions = Artwork.get_versions_by_repo(repo_url)

        if not versions:
            return jsonify({'error': 'No versions found for this repository'}), 404

        version_list = [
            {
                'id': v['id'],
                'commit_hash': v['commit_hash'],
                'image_url': v['image_path'],
                'image_filename': v['image_filename'],
                'created_at_formatted': v['created_at'].strftime('%b %d, %Y at %I:%M %p'),
                'like_count': v['like_count']
            }
            for v in versions
        ]

        return jsonify({
            'success': True,
            'versions': version_list,
            'total_versions': len(version_list)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate sitemap.xml for search engines."""
    pages = [
        {
            'loc': 'https://git2art.com/',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '1.0'
        },
        {
            'loc': 'https://git2art.com/about',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        },
        {
            'loc': 'https://git2art.com/gallery',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '0.9'
        }
    ]

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_xml += '  <url>\n'
        sitemap_xml += f'    <loc>{page["loc"]}</loc>\n'
        sitemap_xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        sitemap_xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        sitemap_xml += f'    <priority>{page["priority"]}</priority>\n'
        sitemap_xml += '  </url>\n'

    sitemap_xml += '</urlset>'

    return Response(sitemap_xml, mimetype='application/xml')
