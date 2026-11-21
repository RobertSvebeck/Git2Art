"""Art styles rendered from repository data (scene/repodata.py), not from clones."""

from . import de_stijl, expressionist, garden, impressionist, pixel_city, psychedelic, watercolour

DATA_STYLES = {
    'pixel_city': pixel_city.render,
    'de_stijl': de_stijl.render,
    'garden': garden.render,
    'watercolor': watercolour.render,
    'impressionist': impressionist.render,
    'expressionist': expressionist.render,
    'psychedelic': psychedelic.render,
}
