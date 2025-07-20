from argparse import ArgumentParser, Namespace
from datetime import timedelta
from pathlib import Path

from mutagen._file import FileType
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4

from mtools.errors import UnrecognisedFormat
from mtools.metautils import MP3Key, MP4Key, format_m4a_values, format_mp3_value
from mtools.utils import make_mutagen_file


class ProgramArgsNamespace(Namespace):
    path: Path
    show_skipped: bool
    include_replaygain: bool
    raw: bool


def get_args() -> ProgramArgsNamespace:
    parser = ArgumentParser()
    parser.add_argument(
        "path",
        metavar="PATH",
        type=Path,
    )
    parser.add_argument(
        "--include-replaygain",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--show-skipped",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--raw",
        action="store_true",
    )
    return parser.parse_args(namespace=ProgramArgsNamespace())


def view_m4a(
    file: MP4,
    raw: bool = False,
):
    print(f"[    ] length: {timedelta(seconds=round(file.info.length))}")
    keys_values = [(MP4Key(key_str), value) for key_str, value in file.items()]
    keys_values = sorted(keys_values, key=lambda kv: kv[0].raw)
    for key, values in keys_values:
        if key.raw == "covr" or not raw:
            values_shown = format_m4a_values(values)
        else:
            values_shown = values

        if key.is_known:
            if raw:
                print(f"[{key.raw}] {key.label}: {values_shown}")
            else:
                print(f"[{key.key_display}] {key.label}: {values_shown}")
        else:
            if raw:
                print(f"[{key.raw}]: {values_shown}")
            else:
                print(f"[{key.key_display}]: {values_shown}")


def view_mp3(
    file: MP3,
    raw: bool = False,
    include_replaygain: bool = False,
    show_skipped: bool = False,
):
    print(f"[    ] length: {timedelta(seconds=round(file.info.length))}")
    keys_values = [(MP3Key(key_str), value) for key_str, value in file.items()]
    keys_values = sorted(keys_values, key=lambda kv: kv[0].raw)
    for key, value in keys_values:
        if not key.is_known and not show_skipped:
            continue
        if "replaygain" in key.raw and not include_replaygain and not show_skipped:
            continue
        if key.is_known:
            if raw:
                if key.raw == "APIC:":
                    print(f"[{key.raw}] {key.label}: {value.__class__}")
                else:
                    print(f"[{key.raw}] {key.label}: {repr(value)}")
            else:
                print(f"[{key.key_display}] {key.label}: {format_mp3_value(value)}")
        else:
            print(f"[{key.raw}]: {format_mp3_value(value)}")


def view_file(
    file: FileType,
    raw: bool = False,
    show_skipped: bool = False,
    include_replaygain: bool = False,
):
    match file:
        case MP3():
            view_mp3(
                file,
                raw=raw,
                include_replaygain=include_replaygain,
                show_skipped=show_skipped,
            )
        case MP4():
            view_m4a(
                file,
                raw=raw,
            )
        case _:
            raise UnrecognisedFormat(f"Unrecognised file type {file.__class__}")


def main(args: ProgramArgsNamespace) -> None:
    file = make_mutagen_file(args.path)
    view_file(
        file,
        raw=args.raw,
        show_skipped=args.show_skipped,
        include_replaygain=args.include_replaygain,
    )


if __name__ == "__main__":
    args = get_args()
    main(args)
