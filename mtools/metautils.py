import importlib
import re
from typing import cast

from mutagen.id3._frames import APIC, PRIV
from mutagen.mp4 import AtomDataType, MP4FreeForm, MP4Tags

from mtools.meta_data import EasyID3Keys, EasyMP4Keys, ID3MiscFrameClasses


class Key:
    raw: str
    key_display: str
    label: str | None

    def __init__(self, raw_key: str):
        self.raw = raw_key

    def __repr__(self):
        return f"{self.__class__.__name__}({", ".join([f"{k}={repr(v)}" for k, v in self.__dict__.items()]):})"

    @property
    def is_known(self):
        return self.label is not None


class MP4Key(Key):

    def __init__(self, raw_key: str):
        super().__init__(raw_key)

        if self.raw in EasyMP4Keys:
            self.key_display = self.raw
            self.label = EasyMP4Keys[self.raw]
            return

        if bytes(raw_key, "utf-8") in MP4Tags._MP4Tags__atoms:
            self.key_display = self.raw
            self.label = self.label_from_mp4tags_docstring(self.raw)
            return

        if raw_key.startswith("----:com.apple.iTunes:"):
            self.key_display = "----"
            self.label = raw_key.lstrip("----:com.apple.iTunes:")
            return

        self.key_display = raw_key
        self.label = self.label_from_mp4tags_docstring(self.raw)

    @staticmethod
    def label_from_mp4tags_docstring(key: str):
        pattern = rf"\s*\* '{''.join(f'\\\\\\\\x{ord(c):02x}' if ord(c) > 127 else c for c in key)}' -- ([\w /]+)"
        m = re.search(pattern, MP4Tags.__doc__)
        if m:
            return cast(str, m.group(1))
        return None


class IndexTotalDisplay:
    def __init__(self, index_total: tuple[int, int]):
        self.index, self.total = index_total

    def __repr__(self):
        if self.total:
            return f"{self.index}/{self.total}"
        return f"{self.index}"


def format_m4a_value(value):
    if isinstance(value, (str, bool, int, float)):
        return value
    elif isinstance(value, tuple):
        return IndexTotalDisplay(value)
    elif isinstance(value, MP4FreeForm) and value.dataformat == AtomDataType.UTF8:
        return value.decode()
    else:
        return value.__class__


def format_m4a_values(values):
    return [format_m4a_value(value) for value in values]


_ID3_FRAMES_MODULE = importlib.import_module("mutagen.id3._frames")


class MP3Key(Key):
    def __init__(self, raw_key: str):
        super().__init__(raw_key)

        if self.raw in EasyID3Keys:
            self.key_display = self.raw
            self.label = EasyID3Keys[self.raw]
            return

        if self.raw in ID3MiscFrameClasses:
            self.key_display = self.raw
            self.label = self.label_from_frame_docstring(raw_key)
            return

        if self.raw.startswith("TXXX:"):
            self.key_display = "TXXX"
            self.label = self.raw.lstrip("TXXX:")
            return

        if self.raw.startswith("PRIV:"):
            self.key_display = "PRIV"
            self.label = self.raw.split(":")[1]
            return

        for cmp_key in ID3MiscFrameClasses:
            if raw_key.startswith(cmp_key):
                self.key_display = cmp_key
                self.label = self.label_from_frame_docstring(cmp_key)
                return

        if cls := getattr(_ID3_FRAMES_MODULE, self.raw.split(":")[0]):
            self.key_display = cls.__name__
            self.label = cls.__doc__.split("\n")[0].strip(".")
            return

        self.key_display = raw_key
        self.label = None

    @staticmethod
    def label_from_frame_docstring(key: str):
        return ID3MiscFrameClasses[key].__doc__.split("\n")[0].strip(".")


def format_mp3_value(value):
    if isinstance(value, PRIV):
        return f"{value.__class__.__name__}(owner={value.owner})"
    if isinstance(value, (APIC,)):
        return value.__class__
    return value
