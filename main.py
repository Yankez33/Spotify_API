import json
import requests
# “pretty-print” arbitrary Python data structures in a form which can be used as input to the interpreter
from pprint import pprint
import secrets
import sys

from requests.models import Response


class lastFmSpotify:
    def __init__(self):
        self.token = secrets.spotify_token()
        self.api_key = secrets.last_fm_api_key()
        self.user_id = secrets.spotify_user_id()
        self.spotify_headers = {
            "Content-Type": "application/json", "Authorization": f"Bearer{self.token}"}
        self.playlist_id = " "
        self.song_info = {}
        self.uris = []

    def fetchSongsLastFm(self):
        params = {"limit": 10, "api_key": self.api_key}
        url = "http://ws.audioscrobbler.com/2.0/?method=chart.gettoptracks&api_key=YOUR_API_KEY&format=json"
        response = requests.get(url, params=params)
        if response.status_code != 200:
            self.exceptionalExceptions(response.status_code, response.text())
        res = response.json()
        print("Top songs are: ")
        for item in res['tracks']['track']:
            song = item['name'].title()
            artist = item['artist']['name']
            print(f"{song} by {artist}")
            self.song_info[song] = artist
        print(" Getting songs   URI\n")
        self.getUriFromSpotify()
        print("Creating a playlist \n")
        self.createSongsPlaylist()
        print("Adding songs\n")
        self.addPlaylistSongs()
        print("Songs are as follows: \n")
        self.listSongsInPlaylist()

    def getUriFromSpotify(self):
        for song_name, artist in self.song_info.items():
            url = f"https://api.spotify.com/v1/search?query=tracks%3A{song_name}+artist&3A{artist}&type=track&offset=0limit=10"
            response = requests.get(url, headers=self.spotify_headers)
            res = response.json()
            output_uri = res['tracks', 'items']
            uri = output_uri[0]['uri']
            self.uris.append(uri)

    def createSongsPlaylist(self):
        data = {
            "name": "LastFM top songs",
            "description": "Songs from the top charts of LastFM created with an API",
            "public": True
        }
        data = json.dumps(data)
        url = "https://api.spotify.com/v1/users/{self.user_id}/playlists"

        response = requests.post(url, data=data, headers=self.spotify_headers)
        if response.status_code == 201:
            res = response.json()
            self.playlist_id = res['id']
        else:
            self.exceptionalExceptions(response.status_code, response.text())

    def addPlaylistSongs(self):
        uri_list = json.dumps(self.uris)
        url = "https://api.spotify.com/v1/playlists/{self.playlist_id}/tracks"
        response = requests.post(
            url, data=uri_list, headers=self.spotify_headers)
        if response.status_code == 201:
            print("Added songs successfully")
        else:
            self.exceptionalExceptions(response.status_code, response.text())

    def listSongsInPlaylist(self):
        url = 'https://api.spotify.com/v1/playlists/{self.playlist_id}/tracks'
        response = requests.get(url, headers=self.spotify_headers)
        if response.status_code != 200:
            self.exceptionalExceptions(response.status_code, response.text())
        else:
            res = response.json()
            for item in res["items"]:
                print(item["track"]["name"])

    def exceptionalExceptions(self, status_code, err):
        print("Exception occured with status code", status_code)
        print("Error: ", err)
        sys.exit(0)


if __name__ == '__main__':
    d = lastFmSpotify()
    d.fetchSongsLastFm()
