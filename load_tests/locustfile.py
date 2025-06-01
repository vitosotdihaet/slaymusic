import random
import uuid
from locust import HttpUser, task, between, events
import requests
from fastapi import status
from dotenv import load_dotenv
import os
from datetime import date

assert load_dotenv(".env", override=True)

base_url = f"http://localhost:{os.getenv('BACKEND_PORT', default='8000')}"

USER_CREDENTIALS = {}
FAKE_IMAGE_DATA = b"y00" * 1024 * 50
FAKE_MP3_DATA = b"x00" * 1024 * 100


track_file = "track.mp3", FAKE_MP3_DATA, "audio/mpeg"

image_file = "image.png", FAKE_IMAGE_DATA, "image/png"


class MusicServiceUser(HttpUser):
    wait_time = between(1, 3)

    host = base_url

    def on_start(self):
        self.client.headers = {}

        username = f"locust_user_{uuid.uuid4().hex[:8]}"
        password = "locust_password"
        name = "Locust Test"

        register_data = {
            "name": name,
            "username": username,
            "password": password,
        }

        files = {"cover_file": image_file}

        resp = self.client.post(
            "/user/register/", params=register_data, files=files, name="/user/register/"
        )

        if resp.status_code == status.HTTP_201_CREATED:
            token = resp.json()["token"]
        elif resp.status_code == status.HTTP_400_BAD_REQUEST:
            login_data = {"username": username, "password": password}
            resp = self.client.post(
                "/user/login/", params=login_data, name="/user/login/"
            )
            if resp.status_code == status.HTTP_200_OK:
                token = resp.json()["token"]
            else:
                self.environment.runner.quit()
                raise Exception(
                    f"Failed to login user {username}: {resp.status_code} - {resp.text}"
                )
        else:
            self.environment.runner.quit()
            raise Exception(
                f"Failed to register user {username}: {resp.status_code} - {resp.text}"
            )

        self.headers = {"Authorization": f"Bearer {token}"}
        self.username = username
        self.user_id = None

        resp = self.client.get("/user/", headers=self.headers, name="/user/")
        self.user_id = resp.json()["id"]

        global USER_CREDENTIALS
        USER_CREDENTIALS[self.username] = {"token": token, "user_id": self.user_id}

    @task(2)
    def create_single(self):
        track_data = {
            "name": "Locust single track",
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": track_file, "cover_file": image_file}
        self.client.post(
            "/track/single/",
            params=track_data,
            files=files,
            headers=self.headers,
            name="/track/single/",
        )

    @task(3)
    def create_playlist(self):
        playlist_data = {
            "name": "Locust playlist",
        }
        files = {"image_file": image_file}

        self.client.post(
            "/playlist/",
            params=playlist_data,
            files=files,
            headers=self.headers,
            name="/playlist/",
        )

    @task(2)
    def create_album(self):
        album_data = {
            "name": "Locust album",
            "release_date": date.today().isoformat(),
        }
        files = {"cover_file": image_file}

        self.client.post(
            "/album/",
            params=album_data,
            files=files,
            headers=self.headers,
            name="/album/",
        )

    @task(10)
    def get_tracks(self):
        self.client.get("/tracks/", name="/tracks/")

    @task(10)
    def get_albums(self):
        self.client.get("/albums/", name="/albums")

    @task(10)
    def get_playlists(self):
        self.client.get("/playlists/", name="/playlists/")

    @task(10)
    def get_artists(self):
        self.client.get("/users/artist/", name="/users/artist/")

    @task(30)
    def get_track(self):
        resp = self.client.get("/tracks/", name="/tracks/")
        tracks = resp.json()
        if tracks:
            random_track = random.choice(tracks)
            track_id = random_track["id"]
            search_data = {"id": track_id}

            self.client.get("/track/", params=search_data, name="/track/")
        else:
            pass

    @task(30)
    def get_album(self):
        resp = self.client.get("/albums/", name="/albums")
        albums = resp.json()
        if albums:
            random_album = random.choice(albums)
            album_id = random_album["id"]
            search_data = {"id": album_id}

            self.client.get("/album/", params=search_data, name="/album/")
        else:
            pass

    @task(30)
    def get_playlist(self):
        resp = self.client.get("/playlists/", name="/playlists/")
        playlists = resp.json()
        if playlists:
            random_playlist = random.choice(playlists)
            playlist_id = random_playlist["id"]
            search_data = {"id": playlist_id}

            self.client.get("/playlist/", params=search_data, name="/playlist/")
        else:
            pass

    @task(20)
    def get_artist(self):
        resp = self.client.get("/users/artist/", name="/users/artist/")
        artists = resp.json()
        if artists:
            random_artist = random.choice(artists)
            artist_id = random_artist["id"]
            search_data = {"id": artist_id}

            self.client.get("/user/artist/", params=search_data, name="/user/artist/")
        else:
            pass

    @task(10)
    def get_tracks_by_playlist(self):
        resp = self.client.get("/playlists/", name="/playlists/")
        playlists = resp.json()
        if playlists:
            playlist_id = playlists[0]["id"]
            search_data = {"id": playlist_id}
            self.client.get(
                "/playlist/tracks/", params=search_data, name="/playlist/tracks/"
            )
        else:
            pass

    @task(2)
    def delete_track(self):
        search_data = {"artist_id": self.user_id}
        resp = self.client.get("/tracks/", params=search_data, name="/tracks/")
        tracks = resp.json()
        if tracks:
            random_track = random.choice(tracks)
            track_id = random_track["id"]
            search_data = {"id": track_id}

            self.client.delete(
                "/track/", params=search_data, headers=self.headers, name="/track/"
            )
        else:
            pass

    @task(1)
    def delete_album(self):
        search_data = {"artist_id": self.user_id}
        resp = self.client.get("/albums/", params=search_data, name="/albums")
        albums = resp.json()
        if albums:
            random_album = random.choice(albums)
            album_id = random_album["id"]
            search_data = {"id": album_id}

            self.client.delete(
                "/album/", params=search_data, headers=self.headers, name="/album/"
            )
        else:
            pass

    @task(1)
    def delete_playlist(self):
        search_data = {"author_id": self.user_id}
        resp = self.client.get("/playlists/", params=search_data, name="/playlists/")
        playlists = resp.json()
        if len(playlists) > 1:
            playlist = playlists[1]
            playlist_id = playlist["id"]
            search_data = {"id": playlist_id}

            self.client.delete(
                "/playlist/",
                params=search_data,
                headers=self.headers,
                name="/playlist/",
            )
        else:
            pass

    @task(20)
    def get_track_file(self):
        resp = self.client.get("/tracks/", name="/tracks/")
        tracks = resp.json()
        if tracks:
            random_track = random.choice(tracks)
            track_id = random_track["id"]
            search_data = {"id": track_id}

            self.client.get(
                "/track/stream/",
                params=search_data,
                name="/track/stream/",
            )
        else:
            pass

    @task(20)
    def get_track_image(self):
        resp = self.client.get("/tracks/", name="/tracks/")
        tracks = resp.json()
        if tracks:
            random_track = random.choice(tracks)
            track_id = random_track["id"]
            search_data = {"id": track_id}

            self.client.get(
                "/track/image/",
                params=search_data,
                name="/track/image/",
            )
        else:
            pass

    @task(20)
    def get_album_image(self):
        resp = self.client.get("/albums/", name="/albums")
        albums = resp.json()
        if albums:
            random_album = random.choice(albums)
            album_id = random_album["id"]
            search_data = {"id": album_id}

            self.client.get("/album/image/", params=search_data, name="/album/image/")
        else:
            pass

    @task(20)
    def get_user_image(self):
        resp = self.client.get("/users/artist/", name="/users/artist/")
        artists = resp.json()
        if artists:
            random_artist = artists[1]
            artist_id = random_artist["id"]
            search_data = {"id": artist_id}

            self.client.get("/user/image/", params=search_data, name="/user/image/")
        else:
            pass

    @task(10)
    def add_to_queue(self):
        resp = self.client.get("/tracks/", name="/tracks/")
        tracks = resp.json()
        if tracks:
            random_track = random.choice(tracks)
            track_id = random_track["id"]
            search_data = {"id": track_id}

            self.client.post(
                "/track_queue/right",
                params=search_data,
                headers=self.headers,
                name="/track_queue/right",
            )
        else:
            pass

    @task(5)
    def get_queue(self):
        with self.client.get(
            "/track_queue/",
            headers=self.headers,
            name="/track_queue/",
            catch_response=True,
        ) as resp:
            if resp.status_code == status.HTTP_404_NOT_FOUND:
                resp.success()


@events.test_stop.add_listener
def _(environment, **kw):
    print("\nLocust test finished. Performing cleanup...")
    for _, data in USER_CREDENTIALS.items():
        host = base_url
        delete_url = f"{host}/user/"
        headers = {"Authorization": f"Bearer {data['token']}"}

        requests.delete(delete_url, headers=headers)
    USER_CREDENTIALS.clear()
    print("Cleanup complete.")
