"""Running repository state built by replaying commits."""

from dataclasses import dataclass


@dataclass
class FileEntity:
    entity_id: str
    path: str
    lines: int
    born: int
    touched: int
    author: str


class RepoState:
    """Files alive after a given commit, keyed by current path."""

    def __init__(self):
        self.files = {}
        self.commit_index = -1
        self.commit = None
        self.authors = set()

    def apply(self, commit, index):
        self.commit_index = index
        self.commit = commit
        self.authors.add(commit.author)
        for change in commit.changes:
            entity = None
            if change.old_path and change.old_path in self.files:
                entity = self.files.pop(change.old_path)
                entity.path = change.path
            elif change.path in self.files:
                entity = self.files[change.path]
            if entity is None:
                entity = FileEntity(f'{change.path}@{index}', change.path, 0, index, index, commit.author)
            entity.lines = max(0, entity.lines + change.added - change.deleted)
            entity.touched = index
            entity.author = commit.author
            self.files[change.path] = entity
        for path in commit.deleted_paths:
            self.files.pop(path, None)

    @property
    def total_lines(self):
        return sum(f.lines for f in self.files.values())


def final_state(commits):
    state = RepoState()
    for index, commit in enumerate(commits):
        state.apply(commit, index)
    return state
