"""Render the settled final state of a repository as a still image."""

from .builder import build_scene, layout_stretch
from .history import read_history
from .layout import file_colour, file_position, file_radius, size_scale
from .render import Star, fit_camera, render
from .state import final_state

RECENT_FLARE = (0.55, 0.3, 0.15)


def stars_for_state(state, stretch):
    scale = size_scale(state.total_lines)
    last = state.commit_index
    stars = []
    for path, entity in sorted(state.files.items()):
        x, y = file_position(path)
        age = last - entity.touched
        flare = RECENT_FLARE[age] if 0 <= age < len(RECENT_FLARE) else 0.0
        stars.append((Star(x * stretch, y, file_radius(entity.lines, scale),
                           file_colour(path), 1.0, flare, 0.0), path))
    return stars


def render_still(repo_path, width, height, caption=None):
    state = final_state(read_history(repo_path))
    stretch = layout_stretch(width, height)
    scene = build_scene(stars_for_state(state, stretch), stretch, caption)
    camera = fit_camera(scene.stars, width, height)
    return render(scene, camera, width, height)
