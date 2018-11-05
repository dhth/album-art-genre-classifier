An image classifier that predicts genre from album art as input.

Includes album art fetching utility.

Getting data:
- Add `token.txt` file containing Spotify Web API auth token.
- Change `artists.yml` if needed.
- Run `get_data.py` as follows:
    ```bash
    $ python get_data.py GENRE_NAME
    ```
- Running this will generate `GENRE.txt` file containing album art urls in `spotify_urls` directory.