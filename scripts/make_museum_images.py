"""Create web-sized WebP copies of every generated artwork for the 3D museum.

Usage: python scripts/make_museum_images.py [--overwrite]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.museum_service import make_museum_image  # noqa: E402

IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'generated')


def main():
    overwrite = '--overwrite' in sys.argv
    names = sorted(f for f in os.listdir(IMAGES_DIR) if f.lower().endswith('.png'))
    for index, name in enumerate(names, 1):
        make_museum_image(IMAGES_DIR, name, overwrite=overwrite)
        if index % 20 == 0 or index == len(names):
            print(f'{index}/{len(names)}')


if __name__ == '__main__':
    main()
