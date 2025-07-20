import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from mutagen._file import FileType
from utils_python import setup_logger

from mtools.errors import UnrecognisedTag
from mtools.tag_mapper import TagMapper, get_tag_format
from mtools.utils import make_mutagen_file

LOGGER = logging.getLogger(__name__)


class ProgramArgsNamespace(Namespace):
    input_file_path: Path
    output_file_path: Path


def get_args() -> ProgramArgsNamespace:
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input-file",
        dest="input_file_path",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-file",
        dest="output_file_path",
        type=Path,
        required=True,
    )
    return parser.parse_args(namespace=ProgramArgsNamespace())


def copy_metadata(
    input_file_path: Path,
    output_file_path: Path,
):
    LOGGER.info(f"Copying metadata: '{input_file_path}' -> '{output_file_path}'")
    input_file = make_mutagen_file(input_file_path)
    output_file = make_mutagen_file(output_file_path)

    tag_mapper = TagMapper()

    input_format = get_tag_format(input_file)
    output_format = get_tag_format(output_file)

    for k, v in sorted(input_file.items()):
        if "replaygain" in k:
            continue
        try:
            k_dest, v_dest, label = tag_mapper.translate_tag(
                k, v, input_format, output_format
            )
        except UnrecognisedTag:
            LOGGER.info(f"Skipping tag {k!r}")
            continue

        if label == "COVER":
            LOGGER.info(f"{label=}: output_file[{k_dest!r}]={v_dest.__class__!r}")
        else:
            LOGGER.info(f"{label=}: output_file[{k_dest!r}]={v_dest!r}")
        output_file[k_dest] = v_dest

    output_file.save()


def main(args: ProgramArgsNamespace) -> None:
    copy_metadata(args.input_file_path, args.output_file_path)


if __name__ == "__main__":
    args = get_args()
    setup_logger()
    main(args)
