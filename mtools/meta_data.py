EasyID3TextKeys = {
    "TALB": ("album"),
    "TBPM": ("bpm"),
    "TCMP": ("compilation"),  # iTunes extension
    "TCOM": ("composer"),
    "TCOP": ("copyright"),
    "TENC": ("encodedby"),
    "TEXT": ("lyricist"),
    "TLEN": ("length"),
    "TMED": ("media"),
    "TMOO": ("mood"),
    "TIT1": ("grouping"),
    "TIT2": ("title"),
    "TIT3": ("version"),
    "TPE1": ("artist"),
    "TPE2": ("albumartist"),
    "TPE3": ("conductor"),
    "TPE4": ("arranger"),
    "TPOS": ("discnumber"),
    "TPUB": ("organization"),
    "TRCK": ("tracknumber"),
    "TOLY": ("author"),
    "TSO2": ("albumartistsort"),  # iTunes extension
    "TSOA": ("albumsort"),
    "TSOC": ("composersort"),  # iTunes extension
    "TSOP": ("artistsort"),
    "TSOT": ("titlesort"),
    "TSRC": ("isrc"),
    "TSST": ("discsubtitle"),
    "TLAN": ("language"),
}

EasyID3TXXXKeys = {
    "MusicBrainz Artist Id": ("musicbrainz_artistid"),
    "MusicBrainz Album Id": ("musicbrainz_albumid"),
    "MusicBrainz Album Artist Id": ("musicbrainz_albumartistid"),
    "MusicBrainz TRM Id": ("musicbrainz_trmid"),
    "MusicIP PUID": ("musicip_puid"),
    "MusicMagic Fingerprint": ("musicip_fingerprint"),
    "MusicBrainz Album Status": ("musicbrainz_albumstatus"),
    "MusicBrainz Album Type": ("musicbrainz_albumtype"),
    "MusicBrainz Album Release Country": ("releasecountry"),
    "MusicBrainz Disc Id": ("musicbrainz_discid"),
    "ASIN": ("asin"),
    "ALBUMARTISTSORT": ("albumartistsort"),
    "PERFORMER": ("performer"),
    "BARCODE": ("barcode"),
    "CATALOGNUMBER": ("catalognumber"),
    "MusicBrainz Release Track Id": ("musicbrainz_releasetrackid"),
    "MusicBrainz Release Group Id": ("musicbrainz_releasegroupid"),
    "MusicBrainz Work Id": ("musicbrainz_workid"),
    "Acoustid Fingerprint": ("acoustid_fingerprint"),
    "Acoustid Id": ("acoustid_id"),
}

from mutagen.easyid3 import (
    date_delete,
    date_get,
    date_set,
    gain_delete,
    gain_get,
    gain_set,
    genre_delete,
    genre_get,
    genre_set,
    musicbrainz_trackid_delete,
    musicbrainz_trackid_get,
    musicbrainz_trackid_set,
    original_date_delete,
    original_date_get,
    original_date_set,
    peak_delete,
    peak_get,
    peak_set,
    peakgain_list,
    performer_delete,
    performer_get,
    performer_list,
    performer_set,
    website_delete,
    website_get,
    website_set,
)

EasyID3MiscKeys = {
    "genre": (genre_get, genre_set, genre_delete),
    "date": (date_get, date_set, date_delete),
    "originaldate": (original_date_get, original_date_set, original_date_delete),
    "performer:*": (performer_get, performer_set, performer_delete, performer_list),
    "musicbrainz_trackid": (
        musicbrainz_trackid_get,
        musicbrainz_trackid_set,
        musicbrainz_trackid_delete,
    ),
    "website": (website_get, website_set, website_delete),
    "replaygain_*_gain": (gain_get, gain_set, gain_delete, peakgain_list),
    "replaygain_*_peak": (peak_get, peak_set, peak_delete),
}


EasyID3Keys = {
    **EasyID3TextKeys,
    **EasyID3TXXXKeys,
    **EasyID3MiscKeys,
}

from mutagen.id3._frames import COMM, TALB, TCON, TDRC, TIT2, TPE1, TRCK, TYER

ID3MiscFrameClasses = {
    "TIT2": TIT2,
    "TPE1": TPE1,
    "TALB": TALB,
    "TYER": TYER,
    "TDRC": TDRC,
    "COMM": COMM,
    "TRCK": TRCK,
    "TCON": TCON,
}

# ============================================= #


EasyMP4TextKeys = {
    "\xa9nam": "title",
    "\xa9alb": "album",
    "\xa9ART": "artist",
    "aART": "albumartist",
    "\xa9day": "date",
    "\xa9cmt": "comment",
    "desc": "description",
    "\xa9grp": "grouping",
    "\xa9gen": "genre",
    "cprt": "copyright",
    "soal": "albumsort",
    "soaa": "albumartistsort",
    "soar": "artistsort",
    "sonm": "titlesort",
    "soco": "composersort",
}

EasyMP4FreeformKeys = {
    "MusicBrainz Artist Id": "musicbrainz_artistid",
    "MusicBrainz Track Id": "musicbrainz_trackid",
    "MusicBrainz Album Id": "musicbrainz_albumid",
    "MusicBrainz Album Artist Id": "musicbrainz_albumartistid",
    "MusicIP PUID": "musicip_puid",
    "MusicBrainz Album Status": "musicbrainz_albumstatus",
    "MusicBrainz Album Type": "musicbrainz_albumtype",
    "MusicBrainz Release Country": "releasecountry",
}

EasyMP4IntKeys = {
    "tmpo": "bpm",
}

EasyMP4IntPairKeys = {
    "trkn": "tracknumber",
    "disk": "discnumber",
}

EasyMP4Keys = {
    **EasyMP4TextKeys,
    **EasyMP4FreeformKeys,
    **EasyMP4IntKeys,
    **EasyMP4IntPairKeys,
}
