from mutagen.flac import FLAC

flac_path = "/Users/sundalei/Downloads/Taylor Swift_1989.02.Blank Space.flac"

try:
    audio = FLAC(flac_path)
except:
    pass

print(audio.pprint())