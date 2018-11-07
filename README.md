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

This approach is based on learnings from a fast.ai MOOC that will be publicly available in Jan 2019.

Deployment approach inspired by [@simonw](https://github.com/simonw)'s [repo](https://github.com/simonw/cougar-or-not).
