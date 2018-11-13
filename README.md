An image classifier that predicts genre from album art as input.

## Dataset Creation:

### Pre-requisites:
- Add `token.txt` file containing Spotify Web API auth token.
- Change `artists.yml` if needed.

### Getting data:
File to be used: `get_data.py`. Getting data is divided into to parts:
- Generating pool of artists
    ```bash
    $ python get_data.py GENRE_NAME --artists_file ARTISTS_FILE --fetch n
    ```
- Cleanup of duplicate artists (eg. black sabbath can appear in rock as well as heavy metal). This will individually ask you to assign an artist to a single genre.
    ```bash
    $ python clean_duplicates.py y
    ```
- Fetching albums
    ```bash
    $ python get_data.py GENRE_NAME --artists_file ARTISTS_FILE --fetch y --fetch_only y
    ```
Running this will generate `GENRE_NAME.txt` file containing album art urls in `spotify_urls` directory.

## Classifier:
Experiments can be found in `experiments` directory.

This approach is based on learnings from a fast.ai MOOC that will be publicly available in Jan 2019.

## Deployment:
Deployment approach inspired by [@simonw](https://github.com/simonw)'s [repo](https://github.com/simonw/cougar-or-not).

## ToDo:
- Handle cleanup of duplicates, and fetching albums after new artists are appended to `ARTISTS_FILE`.