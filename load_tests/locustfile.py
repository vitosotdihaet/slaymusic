import random
import uuid
from locust import HttpUser, task, between, events
import requests
from fastapi import status
from dotenv import load_dotenv
import os

assert load_dotenv(".env", override=True)

base_url = f"http://localhost:{os.getenv('BACKEND_PORT', default='8000')}"

USER_CREDENTIALS = {}


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

        resp = self.client.post(
            "/user/register/", params=register_data, name="/user/register/"
        )

        if resp.status_code == 201:
            token = resp.json()["token"]
        elif resp.status_code == 400:
            login_data = {"username": username, "password": password}
            resp = self.client.post(
                "/user/login/", params=login_data, name="/user/login/"
            )
            if resp.status_code == 200:
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

        resp = self.client.get(
            "/user/", headers=self.headers, name="/user/get_current/"
        )
        self.user_id = resp.json()["id"]

        global USER_CREDENTIALS
        USER_CREDENTIALS[self.username] = {"token": token, "user_id": self.user_id}

    @task(3)
    def get_all_playlists(self):
        self.client.get("/playlists/", headers=self.headers)

    @task(2)
    def create_and_get_playlist(self):
        playlist_name = "Locust Playlist"
        playlist_data = {
            "author_id": self.user_id,
            "name": playlist_name,
        }

        with self.client.post(
            "/playlist/",
            params=playlist_data,
            headers=self.headers,
            catch_response=True,
            name="/playlist/create/",
        ) as response:
            if response.status_code == 201:
                playlist_id = response.json()["id"]
                response.success()
                self.client.get(
                    "/playlist/",
                    params={"id": playlist_id},
                    headers=self.headers,
                    name="/playlist/get_by_id/",
                )
            else:
                response.failure(
                    f"Failed to create playlist: {response.status_code} - {response.text}"
                )

    # @task(1)
    # def get_tracks_by_playlist(self):
    #     playlist_id = random.randint(1, 100)
    #     self.client.get(
    #         "/playlist/tracks/", params={"id": playlist_id}, headers=self.headers
    #     )

    # @task(1)
    # def register_new_user_and_login(self):
    #     username = f"dynamic_user_{uuid.uuid4().hex[:8]}"
    #     password = "dynamic_password"
    #     name = "Dynamic Test User"

    #     register_data = {
    #         "name": name,
    #         "username": username,
    #         "password": password,
    #     }

    #     with self.client.post(
    #         "/user/register/",
    #         params=register_data,
    #         catch_response=True,
    #         name="/user/register_dynamic/",
    #     ) as response:
    #         if response.status_code == 201:
    #             response.success()
    #             print(f"Dynamic user {username} registered successfully.")
    #             login_data = {"username": username, "password": password}
    #             self.client.post(
    #                 "/user/login/", params=login_data, name="/user/login_dynamic/"
    #             )
    #         elif response.status_code == 409:
    #             response.success()
    #             print(f"Dynamic user {username} already exists.")
    #         else:
    #             response.failure(
    #                 f"Failed to register dynamic user {username}: {response.status_code} - {response.text}"
    #             )

    # @task(1)
    # def create_single_track(self):
    #     track_name = f"Locust Single {uuid.uuid4().hex[:6]}"
    #     track_data = {
    #         "name": track_name,
    #         "artist_id": self.user_id,
    #         "release_date": "2024-01-01",
    #     }
    #     files = {
    #         "track_file": ("single.mp3", b"fakesingledata", "audio/mpeg"),
    #         "cover_file": ("", "", "")
    #     }
    #     self.client.post("/track/single/", params=track_data, files=files, headers=self.headers, name="/track/single/create/")

    # @task(1)
    # def get_random_track(self):
    #     track_id = random.randint(1, 1000)
    #     self.client.get(f"/track/", params={"id": track_id}, headers=self.headers)


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
