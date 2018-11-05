import requests
import json
import pprint
import pickle
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description='Fetch album art urls')
parser.add_argument('genre', type=str,)
parser.add_argument('artist_name', type=str,)

args = parser.parse_args()

GENRE = args.genre

ARTIST_NAME = args.artist_name

SEEN_ARTISTS_FILENAME = 'seen_artists'

seen_artists_file = Path(SEEN_ARTISTS_FILENAME)

with open('token.txt') as f:
    TOKEN = f.read().strip()

if seen_artists_file.is_file():
    infile = open(seen_artists_file,'rb')
    seen_artists = pickle.load(infile)
    infile.close()
else:
    seen_artists = {}

url = "https://api.spotify.com/v1/search"

# ARTIST_NAME = "metallica"

querystring = {"q":ARTIST_NAME,"type":"artist"}

headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Authorization': f"Bearer {TOKEN}",
    'cache-control': "no-cache"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

resp = json.loads(response.text)
# pprint.pprint(resp)
artist_id = resp["artists"]["items"][0]["id"]

# ------------

url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'

response = requests.request("GET", url, headers=headers)

resp = json.loads(response.text)

artist_ids = []
artist_names = []

for artist in resp["artists"]:
    if not ARTIST_NAME.lower() in seen_artists:
        seen_artists[ARTIST_NAME.lower()] = artist["id"]
        artist_ids.append(artist_id)
        artist_names.append(ARTIST_NAME.lower())
    # print(artist["name"], artist["id"])
    if not artist["name"].lower() in seen_artists:
        # seen_artists.append(artist["name"])
        artist_ids.append(artist["id"])
        artist_names.append(artist["name"].lower())
        seen_artists[artist["name"].lower()] = artist["id"]
    else:
        print(f'Already seen {artist["name"].lower()}')

albums = {}

for artist_id, artist_name in zip(artist_ids, artist_names):
    print(artist_name)
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'

    albums_querystring = {"limit":"30"}

    response = requests.request("GET", url, headers=headers, params=albums_querystring)

    resp = json.loads(response.text)

    artist_albums = []

    for album in resp["items"]:
        if album["album_type"] == "album":
            try:
                # print(album["album_type"], album["images"][1]["url"])
                artist_albums.append(album["images"][1]["url"])
            except Exception as e:
                print(str(e))

    albums[artist_id] = artist_albums

outfile = open(SEEN_ARTISTS_FILENAME,'wb')
pickle.dump(seen_artists,outfile)
outfile.close()

# pprint.pprint(albums)
# with open(f"{ARTIST_NAME.replace(' ','_')}.txt",'wa') as f:
with open(f"spotify_urls/{GENRE}.txt",'a') as f:
    for artist_id,album in albums.items():
        for album_url in album:
            f.write(album_url+'\n')