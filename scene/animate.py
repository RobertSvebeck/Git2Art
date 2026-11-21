"""Animate a repository's history: files are born, grow, move, flare and fade."""

import math
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone

from .builder import build_scene, layout_stretch
from .layout import file_colour, file_position, file_radius, size_scale
from .render import Camera, Star, fit_camera, render
from .state import RepoState

SIZE_TAU = 0.35
POSITION_TAU = 0.6
CAMERA_TAU = 0.9
TOTAL_TAU = 0.5
FLARE_TAU = 0.7
FLASH_TAU = 0.25
FADE_TAU = 0.4
SUBJECT_MAX = 90
MASS_CHANGE_FLARE = 6.0


@dataclass
class Sprite:
    path: str
    colour: tuple
    x: float
    y: float
    radius: float = 0.0
    alpha: float = 1.0
    flare: float = 0.0
    flash: float = 1.0
    alive: bool = True


def _plural(count, noun):
    return f'{count:,} {noun}' + ('' if count == 1 else 's')


def auto_duration(commit_count):
    return min(40.0, max(12.0, commit_count / 80))


def _ease(current, target, dt, tau):
    return current + (target - current) * (1 - math.exp(-dt / tau))


class HistoryAnimator:
    def __init__(self, commits, width, height, fps=30, duration=None, hold=3.0,
                 pace='commits', repo_name=''):
        if not commits:
            raise ValueError('Repository has no commits to animate')
        self.commits = commits
        self.width, self.height = width, height
        self.fps = fps
        self.dt = 1.0 / fps
        self.duration = duration or auto_duration(len(commits))
        self.animated_frames = max(1, int(round(self.duration * fps)))
        self.hold_frames = int(round(hold * fps))
        self.pace = pace
        self.repo_name = repo_name
        self.stretch = layout_stretch(width, height)
        self.state = RepoState()
        self.next_commit = 0
        self.sprites = {}
        self.camera = None
        self.smoothed_total = None

    @property
    def frame_count(self):
        return self.animated_frames + self.hold_frames

    def _commit_limit(self, frame):
        progress = min(1.0, (frame + 1) / self.animated_frames)
        if self.pace == 'time':
            first, last = self.commits[0].timestamp, self.commits[-1].timestamp
            cutoff = first + progress * (last - first)
            limit = self.next_commit
            while limit < len(self.commits) and self.commits[limit].timestamp <= cutoff:
                limit += 1
            return max(limit, 1)
        return max(1, int(math.ceil(progress * len(self.commits))))

    def _advance(self, frame):
        touched = {}
        limit = self._commit_limit(frame)
        while self.next_commit < limit:
            commit = self.commits[self.next_commit]
            self.state.apply(commit, self.next_commit)
            strength = min(1.0, MASS_CHANGE_FLARE / math.sqrt(max(1, len(commit.changes))))
            for change in commit.changes:
                touched[change.path] = max(touched.get(change.path, 0.0), strength)
            self.next_commit += 1
        return touched

    def _sync_sprites(self, touched):
        live = {}
        for path, entity in self.state.files.items():
            live[entity.entity_id] = path
            sprite = self.sprites.get(entity.entity_id)
            if sprite is None:
                x, y = file_position(path)
                sprite = Sprite(path, file_colour(path), x * self.stretch, y)
                self.sprites[entity.entity_id] = sprite
            elif sprite.path != path:
                sprite.path = path
                sprite.colour = file_colour(path)
            if path in touched:
                sprite.flare = max(sprite.flare, touched[path])
        for entity_id, sprite in self.sprites.items():
            sprite.alive = entity_id in live

    def _step_sprites(self, scale):
        dt = self.dt
        dead = []
        for entity_id, sprite in self.sprites.items():
            entity = self.state.files.get(sprite.path) if sprite.alive else None
            target_radius = file_radius(entity.lines, scale) if entity else 0.0
            tx, ty = file_position(sprite.path)
            sprite.x = _ease(sprite.x, tx * self.stretch, dt, POSITION_TAU)
            sprite.y = _ease(sprite.y, ty, dt, POSITION_TAU)
            sprite.radius = _ease(sprite.radius, target_radius, dt, SIZE_TAU)
            sprite.flare *= math.exp(-dt / FLARE_TAU)
            sprite.flash *= math.exp(-dt / FLASH_TAU)
            if not sprite.alive:
                sprite.alpha *= math.exp(-dt / FADE_TAU)
                if sprite.alpha < 0.02:
                    dead.append(entity_id)
        for entity_id in dead:
            del self.sprites[entity_id]

    def _target_camera(self, scale):
        stars = []
        for path, entity in self.state.files.items():
            x, y = file_position(path)
            stars.append(Star(x * self.stretch, y, file_radius(entity.lines, scale), (0, 0, 0)))
        return fit_camera(stars, self.width, self.height)

    def _step_camera(self, scale):
        target = self._target_camera(scale)
        if self.camera is None:
            self.camera = target
            return
        self.camera = Camera(
            _ease(self.camera.cx, target.cx, self.dt, CAMERA_TAU),
            _ease(self.camera.cy, target.cy, self.dt, CAMERA_TAU),
            math.exp(_ease(math.log(self.camera.scale), math.log(target.scale), self.dt, CAMERA_TAU)),
        )

    def _caption(self):
        commit = self.state.commit
        date = datetime.fromtimestamp(commit.timestamp, tz=timezone.utc).strftime('%Y-%m-%d')
        subject = commit.subject if len(commit.subject) <= SUBJECT_MAX else commit.subject[:SUBJECT_MAX - 3] + '...'
        return [
            self.repo_name,
            f'{date}    commit {self.state.commit_index + 1:,} of {len(self.commits):,}    '
            f'{_plural(len(self.state.files), "file")}    {self.state.total_lines:,} lines    '
            f'{_plural(len(self.state.authors), "author")}',
            f'{commit.author}: {subject}',
        ]

    def frames(self, caption=True):
        for frame in range(self.frame_count):
            touched = self._advance(frame)
            self._sync_sprites(touched)
            total = max(1, self.state.total_lines)
            self.smoothed_total = total if self.smoothed_total is None else \
                _ease(self.smoothed_total, total, self.dt, TOTAL_TAU)
            scale = size_scale(self.smoothed_total)
            self._step_sprites(scale)
            self._step_camera(scale)
            stars = [(Star(s.x, s.y, s.radius, s.colour, s.alpha, s.flare, s.flash), s.path)
                     for s in self.sprites.values()]
            scene = build_scene(stars, self.stretch, self._caption() if caption else None)
            yield render(scene, self.camera, self.width, self.height)


def write_video(frames, output_path, width, height, fps, frame_count, progress=print):
    if output_path.lower().endswith('.gif'):
        return _write_gif(frames, output_path, fps, frame_count, progress)
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        raise RuntimeError('ffmpeg not found; install it or write a .gif instead')
    process = subprocess.Popen(
        [ffmpeg, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
         '-s', f'{width}x{height}', '-r', str(fps), '-i', '-',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
         '-movflags', '+faststart', output_path],
        stdin=subprocess.PIPE,
    )
    try:
        for index, image in enumerate(frames):
            process.stdin.write(image.tobytes())
            _report(progress, index, frame_count)
    finally:
        process.stdin.close()
        process.wait()
    if process.returncode != 0:
        raise RuntimeError(f'ffmpeg exited with code {process.returncode}')


def _write_gif(frames, output_path, fps, frame_count, progress):
    images = []
    for index, image in enumerate(frames):
        images.append(image.convert('P', palette=1, colors=255))
        _report(progress, index, frame_count)
    images[0].save(output_path, save_all=True, append_images=images[1:],
                   duration=int(1000 / fps), loop=0, optimize=False)


def _report(progress, index, total):
    step = max(1, total // 10)
    if (index + 1) % step == 0 or index + 1 == total:
        progress(f'  frame {index + 1}/{total}')
