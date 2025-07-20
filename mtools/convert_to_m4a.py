from argparse import ArgumentParser, Namespace
from pathlib import Path

import ffmpeg
from utils_python import copy_filedate, setup_logger

from mtools.metacopy import copy_metadata


class ProgramArgsNamespace(Namespace):
    input_file: Path
    output_file: Path
    metadata_source_file: Path
    run_metacopy: bool


def get_args() -> ProgramArgsNamespace:
    parser = ArgumentParser()
    parser.add_argument(
        "input_file",
        metavar="INPUT_FILE",
        type=Path,
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=Path,
    )
    parser.add_argument(
        "-m",
        "--metadata-source-file",
        type=Path,
    )
    parser.add_argument(
        "--no-metacopy",
        help="don't run metacopy after conversion (may still get some metadata)",
        action="store_false",
        dest="run_metacopy",
    )
    args = parser.parse_args(namespace=ProgramArgsNamespace())

    if args.output_file is None:
        args.output_file = args.input_file.with_suffix(".m4a")

    if args.metadata_source_file is None:
        args.metadata_source_file = args.input_file

    return args


def main(args: ProgramArgsNamespace):
    print(f"'{args.input_file}' -> '{args.output_file}'")

    cmd = ffmpeg.input(args.input_file)
    cmd = cmd.output(
        str(args.output_file),
        acodec="aac",
        map="0:a",
    )
    print(" ".join(str(c) for c in cmd.compile()))

    try:
        stdout, stderr = cmd.run()
    except Exception as exc:
        print("    " + " ".join(str(c) for c in cmd.compile()))
        raise

    if args.run_metacopy:
        copy_metadata(args.metadata_source_file, args.output_file)

    copy_filedate(args.input_file, args.output_file)


if __name__ == "__main__":
    args = get_args()
    setup_logger()
    main(args)
