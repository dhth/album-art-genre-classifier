from pathlib import Path
import argparse
import yaml
import pickle
from sys import exit

parser = argparse.ArgumentParser(description='Remove duplicate artists')
parser.add_argument('remove', type=str, default="y")

args = parser.parse_args()

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False

REMOVE = str2bool(args.remove)    

if REMOVE is None:
    print('Enter correct value of argument remove -> y or n')
    exit()
    
ARTISTS_CONFIG_FILE = "artists.yml"

with open(ARTISTS_CONFIG_FILE) as f:
    training_artists = yaml.load(f)


GENRES = list(training_artists["genres"].keys())

artists = []
seen_artists = []

for genre in GENRES:
    SEEN_ARTISTS_FILENAME = f'seen_artists_{genre}'

    seen_artists_file = Path(SEEN_ARTISTS_FILENAME)

    if seen_artists_file.is_file():
        infile = open(seen_artists_file,'rb')
        artists_pool = pickle.load(infile)
        infile.close()
    else:
        artists_pool = {}

    artists.append(set(list(artists_pool.keys())))
    seen_artists.append(artists_pool)


for i in range(len(artists)-1):
    for j in range(i+1,len(artists)):
        print(f'Intersection between {GENRES[i]} and {GENRES[j]}')
        artist_1 = set(list(seen_artists[i].keys()))
        artist_2 = set(list(seen_artists[j].keys()))
        
        for el in artist_1.intersection(artist_2):
            print(f'\t{el}')
            if REMOVE:
                remove_from = int(input(f'Is {el} {GENRES[i]}(0) or {GENRES[j]}(1)?\n'))
                if remove_from == 0:
                    remove_index = j
                elif remove_from == 1:
                    remove_index = i
                if remove_from in [0,1]:
                    seen_artists[remove_index].pop(el, None)
            
        print('\n\n\t-------------\n\n')

# check
if REMOVE:             
    artists_check = []
    for i,genre in enumerate(GENRES):
        artists_pool = seen_artists[i]
        artists_check.append(set(list(artists_pool.keys())))

    for i in range(len(artists_check)-1):
        for j in range(i+1,len(artists_check)):
            print(f'Intersection between {GENRES[i]} and {GENRES[j]}')
            for el in artists_check[i].intersection(artists_check[j]):
                print(f'\t{el}')
            print('\n\n\t-------------\n\n')    

if REMOVE:        
    for i, genre in enumerate(GENRES):
        SEEN_ARTISTS_FILENAME = f'seen_artists_{genre}'
        outfile = open(SEEN_ARTISTS_FILENAME,'wb')
        pickle.dump(seen_artists[i],outfile)
        outfile.close()