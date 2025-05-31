import random
import uuid
from locust import HttpUser, task, between, events


USER_CREDENTIALS = {}


@events.init.add_listener
def _(environment, **kw):
    print("Locust test environment initialized.")


class MusicServiceUser(HttpUser):
    wait_time = between(1, 3)

    host = "http://localhost:8000"

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
            print(f"User {username} registered successfully.")
            token = resp.json()["token"]
        elif resp.status_code == 400:
            print(f"User {username} already exists, attempting to log in.")
            login_data = {"username": username, "password": password}
            resp = self.client.post(
                "/user/login/", params=login_data, name="/user/login/"
            )
            if resp.status_code == 200:
                token = resp.json()["token"]
                print(f"User {username} logged in successfully.")
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
        if resp.status_code == 200:
            self.user_id = resp.json()["id"]
            print(f"User {self.username} (ID: {self.user_id}) initialized.")
        else:
            self.environment.runner.quit()
            raise Exception(
                f"Failed to get user ID for {self.username}: {resp.status_code} - {resp.text}"
            )

        global USER_CREDENTIALS
        USER_CREDENTIALS[self.username] = {"token": token, "user_id": self.user_id}

    @task(3)
    def get_all_playlists(self):
        self.client.get("/playlists/", headers=self.headers)

    @task(2)
    def create_and_get_playlist(self):
        playlist_name = f"Locust Playlist {uuid.uuid4().hex[:6]}"
        playlist_data = {
            "author_id": self.user_id,
            "name": playlist_name,
        }
        files = {"image_file": ("", "", "")}  # Без изображения для простоты

        # Создание плейлиста
        with self.client.post(
            "/playlist/",
            params=playlist_data,
            files=files,
            headers=self.headers,
            catch_response=True,
            name="/playlist/create/",
        ) as response:
            if response.status_code == 201:
                playlist_id = response.json()["id"]
                response.success()  # Отметить успешное выполнение запроса
                # Получение созданного плейлиста
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

    @task(1)
    def get_tracks_by_playlist(self):
        """
        Симулирует получение треков из существующего плейлиста.
        Для этого нам нужен реальный playlist_id. В данном примере мы берем
        случайный ID, предполагая, что какие-то плейлисты уже существуют.
        В реальном нагрузочном тестировании лучше иметь подготовленные тестовые данные.
        """
        # В идеале, мы должны были бы создать плейлист заранее или получить список
        # существующих плейлистов, чтобы получить реальный ID.
        # Для простоты, используем заглушку или случайный ID, который может существовать.
        # Замените 1, 2, 3 на реальные ID плейлистов из вашей БД, если они есть.
        # Или можно добавить логику, чтобы получить ID из ранее созданных плейлистов.
        playlist_id = random.randint(
            1, 100
        )  # Предполагаем, что есть плейлисты с ID от 1 до 100
        self.client.get(
            "/playlist/tracks/", params={"id": playlist_id}, headers=self.headers
        )

    @task(1)
    def register_new_user_and_login(self):
        """
        Симулирует регистрацию нового пользователя и последующий логин.
        Эта задача полезна для тестирования масштабируемости процесса регистрации.
        """
        username = f"dynamic_user_{uuid.uuid4().hex[:8]}"
        password = "dynamic_password"
        name = "Dynamic Test User"

        register_data = {
            "name": name,
            "username": username,
            "password": password,
        }

        # Использование catch_response=True позволяет нам явно отмечать запрос как успешный или неуспешный
        with self.client.post(
            "/user/register/",
            params=register_data,
            catch_response=True,
            name="/user/register_dynamic/",
        ) as response:
            if response.status_code == 201:
                response.success()
                print(f"Dynamic user {username} registered successfully.")
                # Попытка логина сразу после регистрации
                login_data = {"username": username, "password": password}
                self.client.post(
                    "/user/login/", params=login_data, name="/user/login_dynamic/"
                )
            elif response.status_code == 409:
                response.success()  # Считаем успешным, если пользователь уже существует
                print(f"Dynamic user {username} already exists.")
            else:
                response.failure(
                    f"Failed to register dynamic user {username}: {response.status_code} - {response.text}"
                )

    # Вы можете добавить больше задач здесь, например:
    # @task(1)
    # def create_single_track(self):
    #     """
    #     Симулирует создание нового сингла.
    #     """
    #     track_name = f"Locust Single {uuid.uuid4().hex[:6]}"
    #     track_data = {
    #         "name": track_name,
    #         "artist_id": self.user_id, # Используем ID текущего пользователя как ID артиста
    #         "release_date": "2024-01-01",
    #     }
    #     files = {
    #         "track_file": ("single.mp3", b"fakesingledata", "audio/mpeg"),
    #         "cover_file": ("", "", "")
    #     }
    #     self.client.post("/track/single/", params=track_data, files=files, headers=self.headers, name="/track/single/create/")

    # @task(1)
    # def get_random_track(self):
    #     """
    #     Симулирует получение информации о случайном треке.
    #     """
    #     # Для этого нужна реальная база данных треков
    #     track_id = random.randint(1, 1000) # Предполагаем, что есть треки с ID от 1 до 1000
    #     self.client.get(f"/track/", params={"id": track_id}, headers=self.headers)


@events.test_stop.add_listener
def _(environment, **kw):
    print("\nLocust test finished. Performing cleanup (if any)...")
    for username, data in USER_CREDENTIALS.items():
        try:
            # requests.delete(f"http://localhost:8000/user/", headers={"Authorization": f"Bearer {data['token']}"})
            print(f"Would delete user: {username} (ID: {data['user_id']})")
        except Exception as e:
            print(f"Failed to delete user {username}: {e}")
    USER_CREDENTIALS.clear()
    pass
