from pathlib import Path

from mutagen._file import FileType
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from utils_python import PathInput


def arg_to_enum(enum_class, arg):
    return enum_class(arg.upper())

class UnsupportedFormat(Exception): ...

def make_mutagen_file(path: PathInput) -> FileType:
    path = Path(path)
    suffixes_filetypes = {
        ".mp3": MP3,
        ".m4a": MP4,
    }
    try:
        filetype = suffixes_filetypes[path.suffix]
    except KeyError as exc:
        raise UnsupportedFormat(exc.args[0]) from exc
    return filetype(path)


def get_prefix_file_paths(
    file_path: PathInput,
    stem_only=True,
) -> list[Path]:
    """
    gets all paths in same directory as given path whose names/stems are a shorter version of the given path
    """
    file_path = Path(file_path)
    prefix_file_paths: list[Path] = []
    for path in file_path.parent.iterdir():
        if path == file_path:
            continue
        if stem_only:
            should_append = file_path.stem.startswith(path.stem)
        else:
            should_append = file_path.name.startswith(path.name)
        if should_append:
            prefix_file_paths.append(path)

    return prefix_file_paths


def ensure_file(file_path: Path) -> None:
    if file_path.is_dir():
        raise IsADirectoryError
    if not file_path.exists():
        raise FileNotFoundError(file_path)
