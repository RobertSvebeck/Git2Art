"""Curate the catalogue into wings and rooms for the 2D museum."""

ROOM_SIZE = 8
SCULPTURES_PER_ROOM = 5

STYLE_ROOMS = {
    'expressionist': ('Expressionism', 'Bold strokes and colliding colour. Every shape is seeded by the code, so no two repositories paint alike.', 'Salon'),
    'impressionist': ('Impressionism', 'Thousands of soft dabs of light, the way a codebase looks from across the room.', 'Sandstone'),
    'watercolor': ('Watercolour', 'Transparent washes that bleed into one another, quiet and pale.', 'Blush'),
    'pixel': ('Pixel', 'Repositories reduced to blocks on a dark ground, in the spirit of early computer graphics.', 'Graphite'),
    'face': ('Portraits', 'Cubist faces: eyes from file counts, noses from commits, smiles from collaborators.', 'Verdigris'),
    'nature': ('Nature', 'Code grown into forests, flowers and undergrowth.', 'Verdigris'),
    'psychedelic': ('Psychedelia', 'No straight lines allowed: spirals, mandalas and neon, at full volume.', 'Ultraviolet'),
    'constellation': ('Constellations', 'The directory tree drawn as a star map: every star a file, every branch a folder.', 'Nocturne'),
}

ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']


def _chunks(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]


def _numbered(name, index, total):
    return name if total == 1 else f'{name} {ROMAN[index] if index < len(ROMAN) else index + 1}'


def _room(room_id, name, intro, mood, works, kind='paintings'):
    return {'id': room_id, 'name': name, 'intro': intro, 'mood': mood, 'kind': kind, 'works': works}


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

    loved = sorted((a for a in artworks if a['likes'] > 0), key=lambda a: (-a['likes'], a['id']))[:ROOM_SIZE]
    wings = [entrance, paintings, court]
    if loved:
        wings.append({'id': 'loved', 'name': 'Most Loved', 'rooms': [_room(
            'most-loved', 'Most Loved', 'The works visitors have liked most.', 'Salon', loved)]})
    return [wing for wing in wings if wing['rooms']]
