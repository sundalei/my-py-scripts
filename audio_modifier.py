"""
Audio Modifier - A tool for reading and modifying FLAC audio file metadata
"""

from mutagen.flac import Picture
from mutagen import MutagenError
from mutagen.flac import FLAC

FLAC_PATH = ""
COVER_PATH = ""

try:
    flac = FLAC(FLAC_PATH)
    print(flac.pictures)
    print(flac.pprint())

    # Read the cover art image data
    with open(COVER_PATH, "rb") as f:
        cover_data = f.read()

    # Create a Picture object
    picture = Picture()
    picture.data = cover_data
    picture.mime = "image/jpeg"
    picture.type = 3 # means front cover
    picture.width = 500
    picture.height = 500

    # Clear existing pictures and add new picture
    flac.clear_pictures()
    flac.add_picture(picture)

    flac.save()
    print(f"Successfully added album art")
except MutagenError as e:
    print(e)
    print(type(e))
