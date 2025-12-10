"""
Audio Modifier - A tool for reading and modifying FLAC audio file metadata
"""

from mutagen import MutagenError
from mutagen.flac import FLAC

FLAC_PATH = "/Users/sundalei/Downloads/Taylor Swift_1989.02.Blank Space.flac"

try:
    flac = FLAC(FLAC_PATH)
    print(flac.pictures)
    print(flac.pprint())
except MutagenError as e:
    print(e)
    print(type(e))
