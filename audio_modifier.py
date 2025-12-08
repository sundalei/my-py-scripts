from mutagen.flac import FLAC

flac_path = "/Users/sundalei/Downloads/Taylor Swift_1989.02.Blank Space.flac"

try:
    flac = FLAC(flac_path)
    print(flac.pictures)
except:
    pass

print(flac.pprint())