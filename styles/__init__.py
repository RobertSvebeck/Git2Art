"""Art styles rendered from repository data (scene/repodata.py), not from clones."""

from . import pixel_city

DATA_STYLES = {
    'pixel_city': pixel_city.render,
}
