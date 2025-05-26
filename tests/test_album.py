import pytest
from fastapi import status
from httpx import AsyncClient
import uuid
from datetime import date
import os


@pytest.mark.asyncio
class TestAlbumEndpoints:
    async def _get_auth_headers(
        self,
        client: AsyncClient,
        username: str | None = None,
        password: str = "testpass",
    ):
        if username is None:
            username = f"testuser_{uuid.uuid4().hex[:8]}"
        register_data = {
            "name": "testname",
            "username": username,
            "password": password,
        }
        response = await client.post("/user/register/", params=register_data)
        if response.status_code != status.HTTP_201_CREATED:
            response = await client.post(
                "/user/login/",
                params={"username": username, "password": password},
            )

        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "username": username}

    async def _delete_user(self, client: AsyncClient, headers):
        resp = await client.delete("/user/", headers=headers)
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ], f"Failed to delete user: {resp.status_code} - {resp.text}"

    async def _create_user_and_get_auth_headers(
        self, async_client: AsyncClient, username_prefix: str
    ):
        username = f"testuser{username_prefix}_{uuid.uuid4().hex[:8]}"
        user_data = {
            "name": f"TestName{username_prefix}",
            "username": username,
            "password": "testpass",
        }
        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to register user: {resp_reg.text}"
        )

        headers = {"Authorization": f"Bearer {resp_reg.json()['token']}"}

        resp_get_user = await async_client.get("/user/", headers=headers)
        assert resp_get_user.status_code == status.HTTP_200_OK
        user_id = resp_get_user.json()["id"]

        return user_id, headers

    async def _create_genre(self, async_client: AsyncClient, genre_name: str):
        headers = await self._get_auth_headers(
            async_client, "admin", os.getenv("AUTH_ADMIN_SECRET_KEY")
        )
        params = {"name": genre_name}
        response = await async_client.post("/genre/", params=params, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        genre_id = response.json()["id"]
        return genre_id, headers

    async def _delete_genre(self, async_client: AsyncClient, genre_id: int, headers):
        resp = await async_client.delete(
            "/genre/", params={"id": genre_id}, headers=headers
        )
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ]

    async def test_create_album_without_image_success(self, async_client: AsyncClient):
        user_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "NoImgAlbumUser"
        )
        params = {
            "name": "NoImgAlbum",
            "artist_id": user_id,
            "release_date": "2025-01-01",
        }
        resp = await async_client.post("/album/", params=params, headers=headers)
        assert resp.status_code == status.HTTP_201_CREATED
        aid = resp.json()["id"]

        await async_client.delete("/album/", params={"id": aid}, headers=headers)
        await self._delete_user(async_client, headers)

    async def test_create_album_with_image_success(self, async_client: AsyncClient):
        user_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "ImgAlbumUser"
        )
        params = {
            "name": "ImgAlbum",
            "artist_id": user_id,
            "release_date": "2025-02-02",
        }
        files = {"cover_file": ("cover.png", b"fake", "image/png")}
        resp = await async_client.post(
            "/album/", params=params, files=files, headers=headers
        )
        assert resp.status_code == status.HTTP_201_CREATED
        aid = resp.json()["id"]

        await async_client.delete("/album/", params={"id": aid}, headers=headers)
        await self._delete_user(async_client, headers)

    async def test_get_album_success(self, async_client: AsyncClient):
        user_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "GetAlbUser"
        )
        create = await async_client.post(
            "/album/",
            params={
                "name": "GetAlbum",
                "artist_id": user_id,
                "release_date": "2025-03-03",
            },
            headers=headers,
        )
        aid = create.json()["id"]

        resp = await async_client.get("/album/", params={"id": aid}, headers=headers)
        assert resp.status_code == status.HTTP_200_OK

        await async_client.delete("/album/", params={"id": aid}, headers=headers)
        await self._delete_user(async_client, headers)

    async def test_get_album_image_success_and_not_found(
        self, async_client: AsyncClient
    ):
        user_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "ImgFetchAlbUser"
        )
        files = {"cover_file": ("c.png", b"\x89PNG", "image/png")}
        create = await async_client.post(
            "/album/",
            params={
                "name": "ImgFetchAlbum",
                "artist_id": user_id,
                "release_date": "2025-05-05",
            },
            files=files,
            headers=headers,
        )
        aid = create.json()["id"]

        resp = await async_client.get("/album/image/", params={"id": aid})
        assert resp.status_code == status.HTTP_200_OK

        resp_nf = await async_client.get("/album/image/", params={"id": 123456})
        assert resp_nf.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/album/", params={"id": aid}, headers=headers)
        await self._delete_user(async_client, headers)

    async def test_delete_album_success_and_not_found(self, async_client: AsyncClient):
        user_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "DelAlbUser"
        )
        create = await async_client.post(
            "/album/",
            params={
                "name": "DelAlbum",
                "artist_id": user_id,
                "release_date": "2025-10-10",
            },
            headers=headers,
        )
        aid = create.json()["id"]

        resp = await async_client.delete("/album/", params={"id": aid}, headers=headers)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        chk = await async_client.get("/album/", params={"id": aid}, headers=headers)
        assert chk.status_code == status.HTTP_404_NOT_FOUND

        resp2 = await async_client.delete(
            "/album/", params={"id": 777777}, headers=headers
        )
        assert resp2.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_user(async_client, headers)

    async def test_create_album_with_nonexistent_artist(
        self, async_client: AsyncClient
    ):
        headers = await self._get_auth_headers(async_client)

        params = {
            "name": "InvalidArtistAlbum",
            "artist_id": 999999,
            "release_date": "2025-01-01",
        }
        resp = await async_client.post("/album/", params=params, headers=headers)
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        await self._delete_user(async_client, headers)

    async def test_get_albums_with_date_filter(self, async_client: AsyncClient):
        user_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "FilterDateUser"
        )
        params = {
            "name": "FilterAlbum",
            "artist_id": user_id,
            "release_date": "2025-05-05",
        }
        create_resp = await async_client.post("/album/", params=params, headers=headers)
        aid = create_resp.json()["id"]

        resp = await async_client.get(
            "/albums/",
            params={"search_start": "2025-01-01", "search_end": "2025-12-31"},
            headers=headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert any(album["id"] == aid for album in resp.json())

        await async_client.delete("/album/", params={"id": aid}, headers=headers)
        await self._delete_user(async_client, headers)

    async def test_add_track_to_album_success(self, async_client: AsyncClient):
        genre_id, genre_headers = await self._create_genre(
            async_client, "AlbumTrackGenre"
        )

        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "AlbumTrackUser"
        )

        album_params = {
            "name": "AlbumWithTrack",
            "artist_id": user_id,
            "release_date": "2025-06-01",
        }
        album_resp = await async_client.post(
            "/album/", params=album_params, headers=user_headers
        )
        assert album_resp.status_code == status.HTTP_201_CREATED
        album_id = album_resp.json()["id"]

        track_params = {
            "name": "AlbumSong1",
            "artist_id": user_id,
            "genre_id": genre_id,
            "album_id": album_id,
            "release_date": date.today().isoformat(),
        }
        track_files = {
            "track_file": ("album_track.mp3", b"ALBUMTRACKDATA", "audio/mpeg")
        }

        track_resp = await async_client.post(
            "/track/", params=track_params, files=track_files, headers=user_headers
        )
        assert track_resp.status_code == status.HTTP_201_CREATED
        track_id = track_resp.json()["id"]

        await async_client.delete(
            "/track/", params={"id": track_id}, headers=user_headers
        )
        await async_client.delete(
            "/album/", params={"id": album_id}, headers=user_headers
        )
        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_user(async_client, user_headers)

    async def test_add_track_to_nonexistent_album(self, async_client: AsyncClient):
        genre_id, genre_headers = await self._create_genre(
            async_client, "NonExistentAlbumGenre"
        )

        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "NonExistentAlbumUser"
        )

        track_params = {
            "name": "BadAlbumSong",
            "artist_id": user_id,
            "genre_id": genre_id,
            "album_id": 999999,
            "release_date": date.today().isoformat(),
        }
        track_files = {"track_file": ("bad_track.mp3", b"BADTRACKDATA", "audio/mpeg")}

        track_resp = await async_client.post(
            "/track/", params=track_params, files=track_files, headers=user_headers
        )
        assert track_resp.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_user(async_client, user_headers)

    async def test_create_single_success_and_errors(self, async_client: AsyncClient):
        genre_id, genre_headers = await self._create_genre(async_client, "SingleGenre")

        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "SingleUser"
        )

        params = {
            "name": "MySingle",
            "artist_id": user_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("track.mp3", b"FAKEMP3DATA", "audio/mpeg")}

        resp = await async_client.post(
            "/track/single/", params=params, files=files, headers=user_headers
        )
        assert resp.status_code == status.HTTP_201_CREATED
        tid = resp.json()["id"]

        bad = params.copy()
        bad["artist_id"] = 999999
        resp2 = await async_client.post(
            "/track/single/", params=bad, files=files, headers=user_headers
        )
        assert resp2.status_code == status.HTTP_403_FORBIDDEN

        resp3 = await async_client.post(
            "/track/single/", params=params, headers=user_headers
        )
        assert resp3.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        await async_client.delete("/track/", params={"id": tid}, headers=user_headers)
        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_user(async_client, user_headers)
