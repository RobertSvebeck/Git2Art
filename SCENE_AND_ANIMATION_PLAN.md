# Scene model and history animation: plan

Status: steps 1 and 2 done 2026-11-21; step 3 next.

## Problem

The existing generators reseed Python's global `random` from
`fingerprint['total_lines']` in nearly every drawing pass. Any one-line change
anywhere reshuffles most of the canvas. Measured on this repo, adding a single
line to `README.md` changed 15% (expressionist), 23% (nature), 55% (face) and
83% (psychedelic) of pixels. The art is deterministic but not stable, so a
frame-per-commit animation would be a strobe of unrelated images. The mapping
from repo to picture is also not legible: apart from the palette, nothing in
an image says anything recognisable about the repo.

## Design

Pipeline: **git history -> repo state -> scene -> renderer**.

1. **History** (`scene/history.py`). One pass of
   `git log --first-parent --reverse -M --numstat --summary`. Gives, per
   commit, added/deleted line counts, renames, creations and deletions.
   Running line counts are the cumulative sum, so no tree checkout or blob
   reads are needed. First-parent keeps the history linear and counts exact.
2. **State** (`scene/state.py`). Files are entities with a stable id that
   survives renames. Each entity carries line count, birth commit, last-touched
   commit and last author.
3. **Layout** (`scene/layout.py`). Position is a pure function of the path:
   each directory sits at a hash-derived angle from its parent, each file at a
   hash-derived offset from its directory. Adding a file never moves another.
   Size is `sqrt(lines)` normalised by total lines. Colour comes from the
   language (Linguist-like hues, normalised for harmony).
4. **Renderer** (`scene/render.py`). Draws a list of entities and directory
   nodes; knows nothing about git. Supersampled for anti-aliasing, glow layer
   blurred at low resolution.
5. **Animation** (`scene/animate.py`). Frames map to positions in the commit
   sequence. Displayed size, position and opacity ease towards their targets
   (exponential smoothing), so the motion is smooth whether a frame covers
   0.1 commits or 100. Births grow in with a flash, deletions shrink and fade,
   renames glide, touched files flare. Frames are piped into ffmpeg (H.264).
6. **Static image** (`generators/constellation_style.py`). The settled final
   state rendered by the same renderer and layout, so the video ends on the
   same composition as the still (apart from caption and touch rings).

## Results of step 1

- History replay matches the real HEAD exactly (line counts and file set) on
  this repo (85 commits) and on pallets/flask (2,283 first-parent commits).
- Stability: a one-line edit changes 0.53% of pixels (mostly the
  "recently touched" ring moving), a new one-line file 0.08%. The old styles
  changed 15% to 83%.
- Speed: about 50 ms per frame at 1280x720; Flask's history (946 frames)
  renders in 47 s. History extraction takes 0.35 s for Flask.
- Known limitation: the web clone is blobless, and `git log --numstat` on a
  blobless clone fetches every historical blob lazily. The web version of the
  constellation style therefore needs a full (size-capped) clone; it is not
  exposed on the web yet (not in the `art_styles` table).

## Steps

1. CLI prototype: `python git2art.py --animate` writes an MP4 of a repo's
   history in the new `constellation` style; `--style constellation` writes the
   still. Verify stability (one-line change should alter a tiny fraction of
   pixels) and render time per frame.
2. Web fixes found during review: `--depth 1` clone makes commit and author
   counts always 1 (switch to a blobless clone), temp folders keyed by repo
   name collide (use a unique folder per request), no clone timeout or size cap.
3. Port the other styles to renderers of the shared scene, dropping or redoing
   the weakest (watercolor, impressionist, pixel).
4. Web animation: server returns the history timeline as compact JSON (cached
   in MariaDB); the browser renders it on Canvas/WebGL with a scrubber and
   exports WebM/MP4 via MediaRecorder or WebCodecs. Oderland has 2 cores and no
   background workers, so server-side video rendering is not viable.
