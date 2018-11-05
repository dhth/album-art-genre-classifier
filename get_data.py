import requests
import json
import pprint
import pickle
from pathlib import Path
import argparse
import yaml

parser = argparse.ArgumentParser(description='Fetch album art urls')
parser.add_argument('genre', type=str,)
# parser.add_argument('artist_name', type=str,)
parser.add_argument('--dry-run', type=bool,)

args = parser.parse_args()

ARTISTS_CONFIG_FILE = 'artists.yml'

with open('artists.yml') as f:
    training_artists = yaml.load(f)

GENRE = args.genre

# ARTIST_NAME = args.artist_name
try:
    ARTISTS_TO_GET = training_artists['genres'][GENRE]
except Exception as e:
    print(str(e))

SEEN_ARTISTS_FILENAME = f'seen_artists_{GENRE}'

seen_artists_file = Path(SEEN_ARTISTS_FILENAME)

if seen_artists_file.is_file():
    infile = open(seen_artists_file,'rb')
    artists_pool = pickle.load(infile)
    infile.close()
else:
    artists_pool = {}

with open('token.txt') as f:
    TOKEN = f.read().strip()

search_url = "https://api.spotify.com/v1/search"

headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Authorization': f"Bearer {TOKEN}",
    'cache-control': "no-cache"
    }

artists_pool_temp = {}

for ARTIST_NAME in ARTISTS_TO_GET:
    print(ARTIST_NAME)

    search_query_string = {"q":ARTIST_NAME,"type":"artist"}

    response = requests.request("GET", search_url, headers=headers, params=search_query_string)

    resp = json.loads(response.text)
    
    if len(resp["artists"]["items"]) > 0:
        artist_id = resp["artists"]["items"][0]["id"]

        similar_url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'

        similar_response = requests.request("GET", similar_url, headers=headers)

        similar_resp = json.loads(similar_response.text)

        for artist in similar_resp["artists"]:
            if not ARTIST_NAME.lower() in artists_pool:
                artists_pool[ARTIST_NAME.lower()] = artist["id"]
                artists_pool_temp[ARTIST_NAME.lower()] = artist["id"]

            if not artist["name"].lower() in artists_pool:
                artists_pool[artist["name"].lower()] = artist["id"]
                artists_pool_temp[artist["name"].lower()] = artist["id"]

            else:
                print(f'Already seen {artist["name"].lower()}')

# pprint.pprint(artists_pool)

# for artist in similar_resp["artists"]:
#     if not ARTIST_NAME.lower() in seen_artists:
#         seen_artists[ARTIST_NAME.lower()] = artist["id"]
#         artist_ids.append(artist_id)
#         artist_names.append(ARTIST_NAME.lower())
#     # print(artist["name"], artist["id"])
#     if not artist["name"].lower() in seen_artists:
#         # seen_artists.append(artist["name"])
#         artist_ids.append(artist["id"])
#         artist_names.append(artist["name"].lower())
#         seen_artists[artist["name"].lower()] = artist["id"]
#     else:
#         print(f'Already seen {artist["name"].lower()}')

albums = {}

for artist_name, artist_id in artists_pool_temp.items():
    print(f'Fetching {artist_name}\'s albums')
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'

    albums_query_string = {"limit":"30"}

    response = requests.request("GET", url, headers=headers, params=albums_query_string)

    resp = json.loads(response.text)

    artist_albums = []
    
    if not resp.get("items",-1) == -1:
        for album in resp["items"]:
            if album["album_type"] == "album":
                try:
                    # print(album["album_type"], album["images"][1]["url"])
                    artist_albums.append(album["images"][1]["url"])
                except Exception as e:
                    print(str(e))

    albums[artist_id] = artist_albums

outfile = open(SEEN_ARTISTS_FILENAME,'wb')
pickle.dump(artists_pool,outfile)
outfile.close()

# pprint.pprint(albums)
# with open(f"{ARTIST_NAME.replace(' ','_')}.txt",'wa') as f:
with open(f"spotify_urls/{GENRE}.txt",'a') as f:
    for artist_id,album in albums.items():
        for album_url in album:
            f.write(album_url+'\n')
