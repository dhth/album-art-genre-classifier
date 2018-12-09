import requests
import json
import pprint
import pickle
from pathlib import Path
import argparse
import yaml
from sys import exit
from time import sleep

parser = argparse.ArgumentParser(description='Fetch album art urls')
parser.add_argument('genre', type=str,)
parser.add_argument('--artists_file', type=str, default="artists.yml")
parser.add_argument('--fetch', type=str, default="n")
parser.add_argument('--delta', type=str, default="n")
parser.add_argument('--fetch_only', type=str, default="n")
parser.add_argument('--find_similar', type=str, default="n")

args = parser.parse_args()

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False

ARTISTS_CONFIG_FILE = args.artists_file

FETCH = str2bool(args.fetch)
DELTA = str2bool(args.delta)
FETCH_ONLY = str2bool(args.fetch_only)
FIND_SIMILAR = str2bool(args.find_similar)

with open(ARTISTS_CONFIG_FILE) as f:
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

token_file = Path("token.txt")
if token_file.is_file():
    with open('token.txt') as f:
        TOKEN = f.read().strip()
else:
    print("\nAdd token.txt file containing valid token.\n")
    exit()

search_url = "https://api.spotify.com/v1/search"

headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Authorization': f"Bearer {TOKEN}",
    'cache-control': "no-cache"
    }

artists_pool_temp = {}

########## -------- GENERATING POOL ----------
if not FETCH_ONLY:
    for ARTIST_NAME in ARTISTS_TO_GET:

        print(f'--> {ARTIST_NAME}')

        try:
            search_query_string = {"q":ARTIST_NAME,"type":"artist"}

            response = requests.request("GET", search_url, headers=headers, params=search_query_string)

            resp = json.loads(response.text)

            if len(resp["artists"]["items"]) > 0:
                artist_id = resp["artists"]["items"][0]["id"]

                if not ARTIST_NAME.lower() in artists_pool:
                    artists_pool[ARTIST_NAME.lower()] = artist_id
                    artists_pool_temp[ARTIST_NAME.lower()] = artist_id
                # else:
                #     print(f'Already seen {ARTIST_NAME.lower()}')
                
                if FIND_SIMILAR:

                    similar_url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'

                    similar_response = requests.request("GET", similar_url, headers=headers)

                    similar_resp = json.loads(similar_response.text)

                    for artist in similar_resp["artists"]:
                        if not artist["name"].lower() in artists_pool:
                            artists_pool[artist["name"].lower()] = artist["id"]
                            artists_pool_temp[artist["name"].lower()] = artist["id"]

                        #else:
                            #print(f'Already seen {artist["name"].lower()}')
        except Exception as e:
            print(str(e))


    print(f"Collected {len(artists_pool.keys())} unique artists for genre: {GENRE}")

    outfile = open(SEEN_ARTISTS_FILENAME,'wb')
    pickle.dump(artists_pool,outfile)
    outfile.close()

########## -------- FETCHING ----------

if FETCH:
    albums = {}

    if DELTA:
        dict_to_fetch = artists_pool_temp
    else:
        dict_to_fetch = artists_pool
    
    count = 1
    
    for artist_name, artist_id in dict_to_fetch.items():
        
        #workaround for rate-limiting
        if count % 50 == 0:
            print('\n\n\t\tsleeping...\n\n')
            sleep(3)
            
        print(f'Fetching {artist_name}\'s albums',)
        url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'

        albums_query_string = {"limit":"30"}

        response = requests.request("GET", url, headers=headers, params=albums_query_string)

        resp = json.loads(response.text)

        artist_albums = []
        
        if not resp.get("items",-1) == -1:
            print(f' --> {len(resp["items"])}')
            for album in resp["items"]:
                if album["album_type"] == "album":
                    try:
                        # print(album["album_type"], album["images"][1]["url"])
                        artist_albums.append(album["images"][1]["url"])
                    except Exception as e:
                        print(str(e))

        albums[artist_id] = artist_albums
        count+=1

    url_dir = Path('spotify_urls').mkdir(parents=True, exist_ok=True) 

    with open(f"spotify_urls/{GENRE}.txt",'a') as f:
        for artist_id,album in albums.items():
            for album_url in album:
                f.write(album_url+'\n')
