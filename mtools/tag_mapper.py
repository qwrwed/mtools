import importlib
import re
from enum import StrEnum
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from mutagen._file import FileType
from mutagen.id3._frames import TextFrame
from mutagen.id3._specs import Encoding, PictureType
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover, MP4FreeForm
from utils_python import PathInput, dump_data, read_dict_from_file

from mtools.errors import UnrecognisedFormat, UnrecognisedTag, UnrecognisedValue

_ID3_FRAMES_MODULE = importlib.import_module("mutagen.id3._frames")


class TagFormat(StrEnum):
    ID3v2_3 = "ID3v2.3"
    ID3v2_4 = "ID3v2.4"
    MP4 = "MP4"


def get_tag_format(file: FileType):
    match file:
        case MP3():
            if not file.tags:
                return TagFormat.ID3v2_4
            match file.tags.version:
                case (2, 3, 0):
                    return TagFormat.ID3v2_3
                case (2, 4, 0):
                    return TagFormat.ID3v2_4
                case _:
                    raise UnrecognisedFormat(
                        f"Unrecognised tags version {file.tags.version} for {file.__class__}"
                    )
        case MP4():
            return TagFormat.MP4
        case _:
            raise UnrecognisedFormat(f"Unrecognised file type {file.__class__}")


class TagMapper:
    mappings_by_label = {}
    mappings_by_format = {}

    def __init__(
        self,
        mappings_save_path: PathInput | None = None,
    ):
        self._mappings_save_path = (
            Path(mappings_save_path) if mappings_save_path else None
        )
        self._init_mappings()

    @staticmethod
    def get_misc_field_tag(
        fieldname: str,
        tag_format: TagFormat,
    ):
        return {
            TagFormat.ID3v2_3: "TXXX:{}",
            TagFormat.ID3v2_4: "TXXX:{}",
            TagFormat.MP4: "----:com.apple.iTunes:{}",
        }[tag_format].format(fieldname)

    @staticmethod
    def get_mp3_fieldname(key: str) -> str | None:
        if m := re.match("^TXXX:(.*)$", key):
            return m.group(1)
        return None

    def translate_tag_key(
        self,
        source_key: str,
        source_format: TagFormat,
        target_format: TagFormat,
    ):
        try:
            target_key = self.mappings_by_format[source_format][source_key][
                target_format
            ]
            if (
                target_format in {TagFormat.ID3v2_3, TagFormat.ID3v2_4}
                and target_key == "COMM"
            ):
                target_key = "COMM::eng"
            return target_key
        except KeyError as exc:
            if source_format == TagFormat.ID3v2_3:
                return self.translate_tag_key(
                    source_key,
                    source_format=TagFormat.ID3v2_4,
                    target_format=target_format,
                )
            if source_format == TagFormat.ID3v2_4:
                if fieldname := self.get_mp3_fieldname(source_key):
                    try:
                        if fieldname in self.mappings_by_label:
                            return self.mappings_by_label[fieldname][target_format]
                    except KeyError:
                        pass
                    return self.get_misc_field_tag(fieldname, target_format)
                if source_key == "COMM::eng":
                    try:
                        return self.mappings_by_format[source_format]["COMM"][
                            target_format
                        ]
                    except KeyError:
                        raise UnrecognisedTag(source_key) from exc
                if source_key == "APIC:":
                    pass
                else:
                    raise UnrecognisedTag(source_key) from exc
            if source_format == TagFormat.MP4:
                if m := re.match("^----:com.apple.iTunes:(.*)$", source_key):
                    fieldname = m.group(1)
                    if (
                        fieldname_mappings := self.mappings_by_label.get(fieldname)
                    ) is not None and (
                        target_key := fieldname_mappings.get(target_format)
                    ) is not None:
                        return self.mappings_by_label[fieldname][target_format]
                    return self.get_misc_field_tag(fieldname, target_format)
                raise UnrecognisedTag(source_key) from exc
            raise UnrecognisedTag(source_key) from exc

    def extract_cover(
        self,
        value: Any,
        source_format: TagFormat,
    ):
        if source_format in {TagFormat.ID3v2_3, TagFormat.ID3v2_4}:
            return (value.data, value.mime)

        if source_format == TagFormat.MP4:
            covers = []
            for v in value:
                mime = {
                    MP4Cover.FORMAT_JPEG: "image/jpeg",
                    MP4Cover.FORMAT_PNG: "image/png",
                }[v.imageformat]
                covers.append((bytes(v), mime))
            return covers[0]

        raise ValueError("Unsupported source type")

    def translate_tag_value(
        self,
        target_key: str,
        source_value: Any,
        source_format: TagFormat,
        target_format: TagFormat,
    ):
        if source_format == target_format:
            return source_value

        label = self.get_tag_label(target_key, target_format)

        if isinstance(source_value, TextFrame):
            value_text = [str(v) for v in source_value.text]
        elif label == "COVER":
            value_data, value_mime = self.extract_cover(source_value, source_format)
        elif isinstance(source_value, list):
            if all(isinstance(v, str) for v in source_value):
                value_text = source_value
            elif all(isinstance(v, MP4FreeForm) for v in source_value):
                value_text = [v.decode() for v in source_value]
            elif all(isinstance(v, tuple) for v in source_value):
                value_text = source_value
            else:
                raise UnrecognisedValue(repr(source_value))
        if target_format in {TagFormat.ID3v2_3, TagFormat.ID3v2_4}:
            if label in {"DISCNUMBER", "TRACK"}:
                result = []
                for v in value_text:
                    if isinstance(v, tuple):
                        index, total = v
                        if total:
                            result.append(f"{index}/{total}")
                        else:
                            result.append(f"{index}")
                    else:
                        result.append(v)
                value_text = result

            if hasattr(_ID3_FRAMES_MODULE, target_key):
                cls = getattr(_ID3_FRAMES_MODULE, target_key)
                if issubclass(cls, TextFrame):
                    return cls(text=value_text)
            elif target_key.startswith("COMM:"):
                cls = getattr(_ID3_FRAMES_MODULE, "COMM")
                return cls(text=value_text, lang="eng")
            elif target_key.startswith("TXXX:"):
                cls = getattr(_ID3_FRAMES_MODULE, "TXXX")
                fieldname = self.get_mp3_fieldname(target_key)
                return cls(text=value_text, desc=fieldname)
            elif label == "COVER":
                cls = getattr(_ID3_FRAMES_MODULE, "APIC")
                return cls(
                    encoding=Encoding.LATIN1,
                    mime=value_mime,
                    type=PictureType.COVER_FRONT,
                    desc="",
                    data=value_data,
                )
            raise UnrecognisedValue(source_value)
        elif target_format == TagFormat.MP4:
            if label in {"DISCNUMBER", "TRACK"}:
                result = []
                for v in value_text:
                    index_total = v.split("/")
                    if len(index_total) == 2:
                        index, total = index_total
                    elif len(index_total) == 1:
                        [index] = index_total
                        total = 0
                    result.append((int(index), int(total)))
                return result
            if label == "COVER":
                fmt = {
                    "image/jpeg": MP4Cover.FORMAT_JPEG,
                    "image/png": MP4Cover.FORMAT_PNG,
                }[value_mime]
                return [MP4Cover(value_data, imageformat=fmt)]
            if label is None:
                value_text = [v.encode(encoding="utf-8") for v in value_text]
            return value_text

        raise UnrecognisedFormat(target_format)

    def get_tag_label(
        self,
        source_key,
        source_format,
    ):
        source_key_normalized = self.translate_tag_key(
            source_key,
            source_format=source_format,
            target_format=source_format,
        )
        try:
            return self.mappings_by_format[source_format][source_key_normalized][
                "__LABEL__"
            ]
        except KeyError:
            return None

    def translate_tag(
        self,
        source_key,
        source_value,
        source_format,
        target_format,
    ):
        target_key = self.translate_tag_key(source_key, source_format, target_format)
        label = self.get_tag_label(source_key, source_format)
        target_value = self.translate_tag_value(
            target_key, source_value, source_format, target_format
        )
        return target_key, target_value, label

    @staticmethod
    def _retrieve_mappings():
        url = "https://docs.mp3tag.de/mapping-table/"
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"

        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.find("table")
        header_cells = table.find("thead").find_all("th")
        formats = [th.text.strip() for th in header_cells[1:]]

        mappings = {}

        for row in table.find("tbody").find_all("tr"):
            cells = row.find_all(["td", "th"])
            if not cells or len(cells) < 2:
                continue

            field_name = cells[0].text.strip()
            field_mappings = {}

            for fmt, cell in zip(formats, cells[1:]):
                val = cell.text.strip()
                if val:
                    field_mappings[fmt] = val

            mappings[field_name] = field_mappings

        return mappings

    def _init_mappings(self):
        if self._mappings_save_path:
            self.mappings_by_label = read_dict_from_file(self._mappings_save_path)

        if not self.mappings_by_label:
            self.mappings_by_label = self._retrieve_mappings()

        self.mappings_by_label = {
            k: v for k, v in self.mappings_by_label.items() if k != "Other fields"
        }
        self.mappings_by_label["COVER"] = {
            "ID3v2.3": "APIC:",
            "ID3v2.4": "APIC:",
            "MP4": "covr",
        }
        self.mappings_by_label["DESCRIPTION"] = {
            **self.mappings_by_label["DESCRIPTION"],
            "ID3v2.3": "TXXX:DESCRIPTION",
            "ID3v2.4": "TXXX:DESCRIPTION",
        }

        mappings_bl = {}
        for label, label_mappings in self.mappings_by_label.items():
            if label == "GENRE":
                mappings_bl[label] = label_mappings
            if "Notes" in label_mappings:
                del label_mappings["Notes"]
            for format_, tag_name in label_mappings.items():
                if "©art" in tag_name:
                    tag_name = tag_name.replace("©art", "©ART")
                if "©gen" in tag_name:
                    tag_name = "©gen"
                    # we don't want "©gen | gnre" unless we can get the
                    #  dict logic to have both in the "from m4a" keys but just
                    #  the first one in the "to m4a" values
                # if "|" in tag_name:
                #     tag_name = [t.strip() for t in tag_name.split("|")]
                label_mappings[format_] = tag_name

        for label, label_mappings in self.mappings_by_label.items():
            for format_, tag_name in label_mappings.items():
                format_mappings = self.mappings_by_format.setdefault(format_, {})
                format_mappings[tag_name] = label_mappings.copy()
                format_mappings[tag_name]["__LABEL__"] = label

        if self._mappings_save_path:
            dump_data(self.mappings_by_label, self._mappings_save_path)
