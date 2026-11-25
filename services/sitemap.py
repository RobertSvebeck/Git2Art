"""sitemap.xml: the fixed pages and one entry per artwork in the museum."""

from xml.sax.saxutils import escape

PAGES = ['/', '/gallery', '/museum', '/gallery3d', '/about']


def _entry(url, lastmod=None):
    modified = f'<lastmod>{escape(lastmod)}</lastmod>' if lastmod else ''
    return f'  <url><loc>{escape(url)}</loc>{modified}</url>'


def build_sitemap(site_url, artworks):
    entries = [_entry(site_url + path) for path in PAGES]
    entries += [_entry(f'{site_url}/artwork/{artwork["id"]}', artwork['added'][:10]) for artwork in artworks]
    return '\n'.join(['<?xml version="1.0" encoding="UTF-8"?>',
                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                      *entries, '</urlset>', ''])
