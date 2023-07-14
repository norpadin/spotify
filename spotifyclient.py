import json

# import requests
from requests import post, get

import base64

from track import Track
from playlist import Playlist


class SpotifyClient:
    """SpotifyClient performs operations using the Spotify API."""

    def __init__(self, user_secret, user_id):
        """
        :param user_secret (str): Spotify user secret
        :param user_id (str): Spotify user id
        """
        self._user_secret = user_secret
        self._user_id = user_id

    def get_token(self, _client_id, _client_secret):
        auth_string = _client_id + ":" + _client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result["access_token"]
        return token

    def get_auth_header(self, _token):
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + _token
        }

    def get_last_played_tracks(self, limit=10):
        """Get the last n tracks played by a user

        :param limit (int): Number of tracks to get. Should be <= 50
        :return tracks (list of Track): List of last played tracks
        """
        url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}"
        response = self._place_get_api_request(url)
        response_json = response.json()

        print('\n', url)
        print(response)

        tracks = [Track(track["track"]["name"], track["track"]["id"], track["track"]["artists"][0]["name"]) for
                  track in response_json["items"]]
        return tracks

    def get_track_recommendations(self, seed_tracks, limit=50):
        """Get a list of recommended tracks starting from a number of seed tracks.

        :param seed_tracks (list of Track): Reference tracks to get recommendations. Should be 5 or less.
        :param limit (int): Number of recommended tracks to be returned
        :return tracks (list of Track): List of recommended tracks
        """
        seed_tracks_url = ""
        for seed_track in seed_tracks:
            seed_tracks_url += seed_track.id + ","
        seed_tracks_url = seed_tracks_url[:-1]
        url = f"https://api.spotify.com/v1/recommendations?seed_tracks={seed_tracks_url}&limit={limit}"
        response = self._place_get_api_request(url)
        response_json = response.json()
        tracks = [Track(track["name"], track["id"], track["artists"][0]["name"]) for
                  track in response_json["tracks"]]
        return tracks

    def create_playlist(self, name):
        """
        :param name (str): New playlist name
        :return playlist (Playlist): Newly created playlist
        """
        data = json.dumps({
            "name": name,
            "description": "Recommended songs",
            "public": True
        })
        url = f"https://api.spotify.com/v1/users/{self._user_id}/playlists"
        response = self._place_post_api_request(url, data)
        response_json = response.json()

        # create playlist
        playlist_id = response_json["id"]
        playlist = Playlist(name, playlist_id)
        return playlist

    def populate_playlist(self, playlist, tracks):
        """Add tracks to a playlist.

        :param playlist (Playlist): Playlist to which to add tracks
        :param tracks (list of Track): Tracks to be added to playlist
        :return response: API response
        """
        track_uris = [track.create_spotify_uri() for track in tracks]
        data = json.dumps(track_uris)
        url = f"https://api.spotify.com/v1/playlists/{playlist.id}/tracks"
        response = self._place_post_api_request(url, data)
        response_json = response.json()
        return response_json

    def _place_get_api_request(self, url):
        _authorization_token = self.get_token(self._user_id, self._user_secret)
        _headers = self.get_auth_header(_authorization_token)
        response = get(
            url,
            headers=_headers
        )
        return response

    def _place_post_api_request(self, url, data):
        _authorization_token = self.get_token(self._user_id, self._user_secret)
        _headers = self.get_auth_header(_authorization_token)
        print('\n', _authorization_token)
        print(_headers)
        response = post(
            url,
            data=data,
            headers=_headers
        )
        return response