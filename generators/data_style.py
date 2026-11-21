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
