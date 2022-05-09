import re
import pathlib
from typing import Generator


def shrink_string(s: str, n: int) -> str:
    if len(s) <= n:
        return s
    else:
        return s[:n-3] + '...'


def iterate_files_paths(path: str) -> Generator[str, None, None]:
    for entry in pathlib.Path(path).iterdir():
        if entry.is_dir():
            yield from iterate_files_paths(str(entry))
        if entry.is_file():
            yield str(entry)


def split_string_to_words(s: str) -> list[str]:
    return [*filter(lambda s: s, re.split(r'[^\w]+', s.lower()))]
