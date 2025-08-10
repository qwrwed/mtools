from argparse import ArgumentError, ArgumentParser, Namespace
from pathlib import Path

import ffmpeg
from utils_python import copy_filedate, setup_logger

from mtools.metacopy import copy_metadata
from mtools.utils import ensure_file, get_prefix_file_paths


class ProgramArgsNamespace(Namespace):
    input_file_path: Path
    output_file_path: Path
    metadata_source_file: Path
    run_metacopy: bool
    keep_input: bool


def get_args() -> ProgramArgsNamespace:
    parser = ArgumentParser()
    parser.add_argument(
        "input_file_path",
        metavar="INPUT_FILE",
        type=Path,
    )
    parser.add_argument(
        "-o",
        "--output-file",
        dest="output_file_path",
        type=Path,
    )
    meta_source_parser = parser.add_mutually_exclusive_group()
    meta_source_parser.add_argument(
        "-m",
        "--metadata-source-file",
        type=Path,
    )
    infer_source_arg = meta_source_parser.add_argument(
        "-a",
        "--infer-metadata-source-file",
        action="store_true",
        help="automatically guess which file to use as meta source",
    )
    parser.add_argument(
        "-k",
        "--keep-input",
        action="store_true",
        help="Keep input file instead of deleting it",
    )
    parser.add_argument(
        "--no-metacopy",
        help="don't run metacopy after conversion (may still get some metadata)",
        action="store_false",
        dest="run_metacopy",
    )
    args = parser.parse_args(namespace=ProgramArgsNamespace())

    if args.output_file_path is None:
        args.output_file_path = args.input_file_path.with_suffix(".m4a")

    if args.metadata_source_file is None:
        if args.infer_metadata_source_file:
            prefix_paths = get_prefix_file_paths(args.output_file_path)
            if prefix_paths:
                print("Got candidate input paths:")
                print("\n".join(f"  {path}" for path in prefix_paths))
                args.input_file_path = prefix_paths[0]
                print(f"Will copy metadata from path '{args.input_file_path}'")
                input("Enter to continue, or Ctrl-C to cancel")
            else:
                raise ArgumentError(
                    infer_source_arg, "was passed but no inferred paths found"
                )
        else:
            args.metadata_source_file = args.input_file_path

    return args


def main(args: ProgramArgsNamespace):
    ensure_file(args.input_file_path)

    print(f"'{args.input_file_path}' -> '{args.output_file_path}'")

    cmd = ffmpeg.input(args.input_file_path)
    cmd = cmd.output(
        str(args.output_file_path),
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
        copy_metadata(args.metadata_source_file, args.output_file_path)

    copy_filedate(args.input_file_path, args.output_file_path)

    if not args.keep_input:
        args.input_file_path.unlink()


if __name__ == "__main__":
    args = get_args()
    setup_logger()
    main(args)
