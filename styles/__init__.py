"""Art styles rendered from repository data (scene/repodata.py), not from clones."""

from . import de_stijl, garden, pixel_city

DATA_STYLES = {
    'pixel_city': pixel_city.render,
    'de_stijl': de_stijl.render,
    'garden': garden.render,
}
