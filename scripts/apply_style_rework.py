"""Apply the 2026-11 art style rework to the database (run on the server).

- Adds/updates the new styles (active) with their display names and order
- Disables the retired styles (face, pixel, nature); their images stay in the gallery
- With --render: re-renders every style for every repository from repodata
  (needs scripts/make_repo_data.py to have run), replacing older images of
  the same commit

Usage: python scripts/apply_style_rework.py [--yes] [--render]
Without --yes it only prints what it would do.
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(ROOT, '.env'))

STYLES = [
    ('expressionist', 'Expressionist', 'Gestural bristle-brush painting: a sweep for every folder, black calligraphy along the tree, splatter from busy files'),
    ('impressionist', 'Impressionist', 'Broken brushstrokes swirling around each folder like eddies in a pond'),
    ('watercolor', 'Watercolour', 'Layered glazes on cold-press paper: folders as washes, files as glazes, an ink sketch of the tree'),
    ('psychedelic', 'Psychedelic', 'Op-art spirals around every folder, mandalas for the largest, glowing eyes for busy files'),
    ('pixel_city', 'Pixel City', 'Isometric 8-bit city: folders are districts, files are buildings, activity sets the time of day'),
    ('de_stijl', 'De Stijl', 'Mondrian-style map of the code: the folder tree divides the canvas, primaries mark the busiest code'),
    ('garden', 'Garden', 'Botanical plate: folders grow as plants, files are leaves, busy files flower, contributors are butterflies'),
    ('tapestry', 'Tapestry', 'The history woven as cloth: a warp band per folder, colour where the code grew'),
]
RETIRED = ['face', 'pixel', 'nature']


def main():
    confirm = '--yes' in sys.argv
    render = '--render' in sys.argv
    for order, (style_id, name, description) in enumerate(STYLES):
        print(f'add/update {style_id:<14} "{name}" (sort {order})')
    for style_id in RETIRED:
        print(f'disable    {style_id}')
    if render:
        print('render     every style for every repository with repo data')
    if not confirm:
        print('\nPreview only. Run again with --yes to apply.')
        return 0

    from models import ArtStyle
    for order, (style_id, name, description) in enumerate(STYLES):
        ArtStyle.create(style_id, name, description, '', is_active=True, sort_order=order)
    for style_id in RETIRED:
        if ArtStyle.exists(style_id):
            ArtStyle.update_status(style_id, False)
    print('database updated')

    if render:
        script = os.path.join(ROOT, 'scripts', 'render_data_style.py')
        for style_id, _, _ in STYLES:
            print(f'--- rendering {style_id}')
            subprocess.run([sys.executable, script, style_id], check=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
