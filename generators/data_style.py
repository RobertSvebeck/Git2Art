"""Adapter: run a repository-data style (styles/) through the generator interface."""

from pathlib import Path

from .base import BaseArtGenerator
from scene.repodata import build_repo_data
from styles import DATA_STYLES


class DataStyleGenerator(BaseArtGenerator):
    STYLE_KEY = None

    def generate_art(self, output_path='repo_art.png'):
        path = str(self.repo_path.resolve())
        name = Path(path).name.removesuffix('.git')
        data = build_repo_data(path, path, name)
        image = DATA_STYLES[self.STYLE_KEY](data, self.width, self.height)
        image.save(output_path)
        print(f"Saved {output_path} ({self.width}x{self.height}, {self.STYLE_KEY})")
        return output_path


class PixelCityStyleGenerator(DataStyleGenerator):
    STYLE_KEY = 'pixel_city'
    STYLE_NAME = "Pixel City"
    STYLE_DESCRIPTION = "Isometric 8-bit city: folders are districts, files are buildings, activity sets the time of day"


class DeStijlStyleGenerator(DataStyleGenerator):
    STYLE_KEY = 'de_stijl'
    STYLE_NAME = "De Stijl"
    STYLE_DESCRIPTION = "Mondrian-style composition: the folder tree divides the canvas, primary colours mark the heaviest and busiest code"


class GardenStyleGenerator(DataStyleGenerator):
    STYLE_KEY = 'garden'
    STYLE_NAME = "Garden"
    STYLE_DESCRIPTION = "Botanical plate: folders grow as plants, files as leaves, busy files flower, contributors are butterflies"


class WatercolourStyleGenerator(DataStyleGenerator):
    STYLE_KEY = 'watercolor'
    STYLE_NAME = "Watercolour"
    STYLE_DESCRIPTION = "Layered transparent glazes on cold-press paper: folders as washes, files as glazes, an ink sketch of the tree"


class ImpressionistStyleGenerator(DataStyleGenerator):
    STYLE_KEY = 'impressionist'
    STYLE_NAME = "Impressionist"
    STYLE_DESCRIPTION = "Broken brushstrokes swirling around each folder; busy files catch the light"


class ExpressionistStyleGenerator(DataStyleGenerator):
    STYLE_KEY = 'expressionist'
    STYLE_NAME = "Expressionist"
    STYLE_DESCRIPTION = "Gestural bristle-brush painting: a sweep per folder, black strokes along the tree, splatter from busy files"


class PsychedelicStyleGenerator(DataStyleGenerator):
    STYLE_KEY = 'psychedelic'
    STYLE_NAME = "Psychedelic"
    STYLE_DESCRIPTION = "Op-art poster: interfering spirals around every folder, mandalas for the largest, glowing eyes for busy files"


class TapestryStyleGenerator(DataStyleGenerator):
    STYLE_KEY = 'tapestry'
    STYLE_NAME = "Tapestry"
    STYLE_DESCRIPTION = "The history woven as textile: a warp band per folder, weft rows through time, colour where the code grew"
