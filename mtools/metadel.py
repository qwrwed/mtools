import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from utils_python import setup_logger

from mtools.metaview import view_file
from mtools.utils import make_mutagen_file

LOGGER = logging.getLogger(__name__)


class ProgramArgsNamespace(Namespace):
    input_file_path: Path
    tag_to_delete: str | None


def get_args() -> ProgramArgsNamespace:
    parser = ArgumentParser()
    parser.add_argument(
        "input_file_path",
        metavar="FILE",
        type=Path,
        default=Path(__file__).parent / "forest_falls.m4a",
    )
    parser.add_argument(
        "-t",
        "--tag-to-delete",
    )
    return parser.parse_args(namespace=ProgramArgsNamespace())


def main(args: ProgramArgsNamespace) -> None:
    input_file = make_mutagen_file(args.input_file_path)
    if args.tag_to_delete:
        if args.tag_to_delete not in input_file:
            LOGGER.info(f"{args.tag_to_delete!r} not in {args.input_file_path!r}")
            return
        LOGGER.info(
            f"deleting {args.tag_to_delete!r} (was {input_file[args.tag_to_delete]!r})"
        )
        del input_file[args.tag_to_delete]
        input_file.save()
    else:
        view_file(input_file, raw=True)


if __name__ == "__main__":
    args = get_args()
    setup_logger()
    main(args)
