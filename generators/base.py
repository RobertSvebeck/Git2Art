"""Base generator class with common functionality."""

import git
from pathlib import Path
from collections import defaultdict
import hashlib


class BaseArtGenerator:
    """Base class for all art generators."""

    STYLE_NAME = "base"
    STYLE_DESCRIPTION = "Base generator - should not be used directly"

    # Common canvas aspect ratios
    ASPECT_RATIOS = {
        'square': (1, 1),
        '16:10': (16, 10),
        '16:9': (16, 9),
        '3:2': (3, 2),
        '4:3': (4, 3),
        '5:4': (5, 4),
        'portrait_3:4': (3, 4),
        'portrait_2:3': (2, 3),
    }

    def __init__(self, repo_path='.', width=1600, height=1200, aspect_ratio='auto', **kwargs):
        """Initialize base generator.

        Args:
            repo_path: Path to git repository
            width: Canvas width (base dimension)
            height: Canvas height (ignored if aspect_ratio is specified)
            aspect_ratio: Aspect ratio name or 'auto' for detection
            **kwargs: Additional style-specific parameters
        """
        self.repo = git.Repo(repo_path)
        self.repo_path = Path(repo_path)

        # Get fingerprint (may be needed for aspect ratio detection)
        fingerprint = self.get_repo_fingerprint()

        # Auto-detect aspect ratio if requested
        if aspect_ratio == 'auto':
            aspect_ratio = self.detect_aspect_ratio(fingerprint)

        # Apply aspect ratio
        if aspect_ratio and aspect_ratio in self.ASPECT_RATIOS:
            ratio_w, ratio_h = self.ASPECT_RATIOS[aspect_ratio]
            self.width = width
            self.height = int(width * ratio_h / ratio_w)
            self.aspect_ratio = aspect_ratio
        else:
            self.width = width
            self.height = height
            self.aspect_ratio = 'custom'

    def get_repo_fingerprint(self):
        """Generate repository fingerprint - common for all styles."""
        fingerprint_data = {
            'files': {},
            'total_lines': 0,
            'file_types': defaultdict(int),
            'commit_count': 0,
            'authors': set()
        }

        try:
            head_commit = self.repo.head.commit
            fingerprint_data['commit_count'] = len(list(self.repo.iter_commits()))
            fingerprint_data['authors'] = {c.author.name for c in self.repo.iter_commits()}
        except:
            pass

        try:
            for item in self.repo.tree().traverse():
                if item.type == 'blob':
                    file_path = item.path
                    if self._should_skip_file(file_path):
                        continue
                    try:
                        content = item.data_stream.read().decode('utf-8', errors='ignore')
                        lines = content.split('\n')
                        line_count = len(lines)
                        ext = Path(file_path).suffix or 'no_ext'
                        fingerprint_data['file_types'][ext] += line_count
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        fingerprint_data['files'][file_path] = {
                            'lines': line_count,
                            'hash': content_hash,
                            'extension': ext
                        }
                        fingerprint_data['total_lines'] += line_count
                    except:
                        continue
        except:
            pass

        return fingerprint_data

    def _should_skip_file(self, file_path):
        """Determine if a file should be skipped."""
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
                          '.pdf', '.zip', '.tar', '.gz', '.bin', '.exe'}
        skip_names = {'package-lock.json', 'yarn.lock', '.gitattributes'}
        path = Path(file_path)
        return path.suffix in skip_extensions or path.name in skip_names

    @staticmethod
    def detect_aspect_ratio(fingerprint):
        """Detect aspect ratio based on repository characteristics.

        Portrait (3:4) - Mobile apps
        Landscape (16:9) - Web frontends, documentation
        Square (1:1) - Backend, libraries, general purpose
        """
        file_types = fingerprint['file_types']
        total_lines = fingerprint['total_lines']

        if total_lines == 0:
            return 'square'

        mobile_lines = sum(file_types.get(ext, 0) for ext in ['.swift', '.kt', '.dart', '.m', '.mm'])
        mobile_pct = mobile_lines / total_lines

        web_lines = sum(file_types.get(ext, 0) for ext in ['.html', '.css', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte'])
        web_pct = web_lines / total_lines

        doc_lines = sum(file_types.get(ext, 0) for ext in ['.md', '.rst', '.txt'])
        doc_pct = doc_lines / total_lines

        if mobile_pct > 0.15:
            return 'portrait_3:4'
        elif web_pct > 0.25 or doc_pct > 0.40:
            return '16:9'
        else:
            return 'square'

    def generate_art(self, output_path='repo_art.png'):
        """Generate art - must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement generate_art()")

    def get_style_info(self):
        """Return information about this style."""
        return {
            'name': self.STYLE_NAME,
            'description': self.STYLE_DESCRIPTION,
            'class': self.__class__.__name__
        }
