"""Constellation style: the repository's directory tree as a star map.

Files are stars (size from line count, colour from language), directories are
branches. Layout is a pure function of each path, so small changes stay small.
"""

from .base import BaseArtGenerator
from scene.still import render_still


class ConstellationStyleGenerator(BaseArtGenerator):
    STYLE_NAME = "Constellation"
    STYLE_DESCRIPTION = "Star map of the directory tree; stable under small changes and animatable over history"

    def generate_art(self, output_path='repo_art.png'):
        image = render_still(str(self.repo_path), self.width, self.height)
        image.save(output_path)
        print(f"Saved {output_path} ({self.width}x{self.height}, constellation)")
        return output_path
