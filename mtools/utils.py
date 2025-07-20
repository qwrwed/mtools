from pathlib import Path

from mutagen._file import FileType
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from utils_python import PathInput


def arg_to_enum(enum_class, arg):
    return enum_class(arg.upper())


def make_mutagen_file(path: PathInput) -> FileType:
    path = Path(path)
    suffixes_filetypes = {
        ".mp3": MP3,
        ".m4a": MP4,
    }
    filetype = suffixes_filetypes[path.suffix]
    return filetype(path)
