"""Curate the catalogue into wings and rooms for the 2D museum."""

ROOM_SIZE = 8
SCULPTURES_PER_ROOM = 5
INSTALLATIONS_PER_ROOM = 4
INSTALLATION_ROOMS = 4

STYLE_ROOMS = {
    'expressionist': ('Expressionism', 'Gestural painting with a bristle brush: one sweep for every folder, black calligraphic strokes along the folder tree, splatter where the code is most edited.', 'Salon'),
    'impressionist': ('Impressionism', 'Thousands of broken brushstrokes swirling around each folder like eddies in a pond; the busiest files catch the light.', 'Sandstone'),
    'watercolor': ('Watercolour', 'Layered glazes on cold-press paper: each folder a broad wash, each file a smaller glaze, tied together by an ink sketch of the folder tree. Where pigment pools, the code is dense.', 'Blush'),
    'pixel': ('Pixel', 'Repositories reduced to blocks on a dark ground, in the spirit of early computer graphics.', 'Graphite'),
    'garden': ('The Garden', 'Every folder grows as a plant: files are leaves, the busiest files flower in their language colour, documentation blooms as daisies. Old code turns woody; butterflies are the contributors.', 'Sandstone'),
    'de_stijl': ('De Stijl', 'After Mondrian, but every line is real: the folder tree divides the canvas by size, and primary colours mark the heaviest and busiest code.', 'White Cube'),
    'pixel_city': ('Pixel City', 'Each repository as an 8-bit city: folders are districts, files are buildings, documentation grows as parks. Busy projects are painted by day; quiet ones by night.', 'Nocturne'),
    'nature': ('Nature', 'Code grown into forests, flowers and undergrowth.', 'Verdigris'),
    'psychedelic': ('Psychedelia', 'Every folder is the eye of a spiral; the spirals interfere into neon bands, the largest folders bloom into mandalas, and the busiest files stare back.', 'Ultraviolet'),
    'constellation': ('Constellations', 'The directory tree drawn as a star map: every star a file, every branch a folder.', 'Nocturne'),
}

ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']


def _chunks(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]


def _numbered(name, index, total):
    return name if total == 1 else f'{name} {ROMAN[index] if index < len(ROMAN) else index + 1}'


def _room(room_id, name, intro, mood, works, kind='paintings'):
    return {'id': room_id, 'name': name, 'intro': intro, 'mood': mood, 'kind': kind, 'works': works}


def _commit_count(artwork):
    return artwork.get('commits') or 0


def build_museum(artworks):
    """Return wings -> rooms -> works, in walking order."""
    newest = sorted(artworks, key=lambda a: -a['id'])[:ROOM_SIZE]
    entrance = {'id': 'entrance', 'name': 'Entrance Hall', 'rooms': [_room(
        'new-acquisitions', 'New Acquisitions',
        'The most recent works in the collection, freshly generated from public repositories.',
        'White Cube', newest)]}

    by_style = {}
    for artwork in artworks:
        by_style.setdefault(artwork['style'], []).append(artwork)
    painting_rooms = []
    for style, works in sorted(by_style.items(), key=lambda kv: -len(kv[1])):
        name, intro, mood = STYLE_ROOMS.get(style, (style.title(), '', 'White Cube'))
        chunks = _chunks(sorted(works, key=lambda a: a['title'].lower()), ROOM_SIZE)
        for index, chunk in enumerate(chunks):
            painting_rooms.append(_room(f'{style}-{index + 1}', _numbered(name, index, len(chunks)),
                                        intro if index == 0 else '', mood, chunk))
    paintings = {'id': 'paintings', 'name': 'Painting Galleries', 'rooms': painting_rooms}

    sculptures = []
    seen = set()
    for artwork in sorted(artworks, key=lambda a: a['title'].lower()):
        if artwork.get('data') and artwork['repo_url'] not in seen:
            seen.add(artwork['repo_url'])
            sculptures.append({**artwork, 'style': 'sculpture'})
    chunks = _chunks(sculptures, SCULPTURES_PER_ROOM)
    court = {'id': 'sculpture', 'name': 'Sculpture Court', 'rooms': [
        _room(f'sculpture-{i + 1}', _numbered('Sculpture Court', i, len(chunks)),
              'Each sculpture is a whole repository: beads are files, sized by their bytes and coloured by '
              'language; bronze branches are folders. Hover to watch it grow commit by commit.' if i == 0 else '',
              'Nocturne', chunk, kind='sculpture')
        for i, chunk in enumerate(chunks)]}

    by_history = sorted(sculptures, key=lambda a: -_commit_count(a))[:INSTALLATIONS_PER_ROOM * INSTALLATION_ROOMS]
    light_chunks = _chunks([{**a, 'style': 'installation'} for a in by_history], INSTALLATIONS_PER_ROOM)
    light = {'id': 'light', 'name': 'Light Installations', 'rooms': [
        _room(f'light-{i + 1}', _numbered('Light Installations', i, len(light_chunks)),
              'A repository\'s whole history as a spiral of light: every point is a change, rising from the first '
              'commit at the bottom to today at the top. A pulse travels through time while you look.' if i == 0 else '',
              'Void', chunk, kind='light')
        for i, chunk in enumerate(light_chunks)]}

    loved = sorted((a for a in artworks if a['likes'] > 0), key=lambda a: (-a['likes'], a['id']))[:ROOM_SIZE]
    wings = [entrance, paintings, court, light]
    if loved:
        wings.append({'id': 'loved', 'name': 'Most Loved', 'rooms': [_room(
            'most-loved', 'Most Loved', 'The works visitors have liked most.', 'Salon', loved)]})
    return [wing for wing in wings if wing['rooms']]
