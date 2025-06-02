import pytest
from fastapi import status
from httpx import AsyncClient
import uuid
from datetime import date
import os


@pytest.mark.asyncio
class TestTrackEndpoints:
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
        response = await client.post("/user/register/", json=register_data)
        if response.status_code != status.HTTP_201_CREATED:
            response = await client.post(
                "/user/login/",
                json={"username": username, "password": password},
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
            json=user_data,
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

    async def _delete_genre(self, client: AsyncClient, genre_id: int, headers: dict):
        resp = await client.delete("/genre/", params={"id": genre_id}, headers=headers)
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ], f"Failed to delete genre {genre_id}: {resp.status_code} - {resp.text}"

    async def _create_album(
        self, client: AsyncClient, artist_id: int, headers: dict, album_name: str
    ) -> int:
        album_data = {
            "name": album_name,
            "artist_id": artist_id,
            "release_date": date.today().isoformat(),
        }
        files = {"cover_file": ("", "", "")}
        resp = await client.post(
            "/album/", params=album_data, files=files, headers=headers
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create album: {resp.text}"
        )
        return resp.json()["id"]

    async def _delete_album(self, client: AsyncClient, album_id: int, headers: dict):
        resp = await client.delete("/album/", params={"id": album_id}, headers=headers)
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ], f"Failed to delete album {album_id}: {resp.status_code} - {resp.text}"

    async def _create_single(
        self,
        client: AsyncClient,
        artist_id: int,
        genre_id: int,
        headers: dict,
        track_name_prefix: str,
        has_cover: bool = False,
    ) -> int:
        unique_suffix = f"{track_name_prefix.lower()}_{uuid.uuid4().hex[:8]}"
        track_data = {
            "name": f"Single {unique_suffix}",
            "artist_id": artist_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {
            "track_file": ("single.mp3", b"fakesingledata", "audio/mpeg"),
        }
        if has_cover:
            files["cover_file"] = (
                "single_cover.png",
                b"fakesinglecoverdata",
                "image/png",
            )
        else:
            files["cover_file"] = ("", "", "")

        resp = await client.post(
            "/track/single/",
            params=track_data,
            files=files,
            headers=headers,
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create single during setup: {resp.text}"
        )
        return resp.json()["id"]

    async def _create_album_track(
        self,
        client: AsyncClient,
        artist_id: int,
        album_id: int,
        genre_id: int,
        headers: dict,
        track_name_prefix: str,
    ) -> int:
        unique_suffix = f"{track_name_prefix.lower()}_{uuid.uuid4().hex[:8]}"
        track_data = {
            "name": f"Album Track {unique_suffix}",
            "artist_id": artist_id,
            "album_id": album_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("album_track.mp3", b"fakealbumtrackdata", "audio/mpeg")}
        resp = await client.post(
            "/track/", params=track_data, files=files, headers=headers
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create album track: {resp.text}"
        )
        return resp.json()["id"]

    async def _delete_track(self, client: AsyncClient, track_id: int, headers: dict):
        resp = await client.delete("/track/", params={"id": track_id}, headers=headers)
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ], f"Failed to delete track {track_id}: {resp.status_code} - {resp.text}"

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

        await self._delete_track(async_client, tid, user_headers)
        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_user(async_client, user_headers)

    async def test_create_track_to_album_success_and_not_found(
        self, async_client: AsyncClient
    ):
        genre_id, genre_headers = await self._create_genre(
            async_client, "AlbumTrackGenre"
        )
        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "AlbumTrackUser"
        )
        album_id = await self._create_album(
            async_client, user_id, user_headers, "AlbumForTrack"
        )

        params = {
            "name": "MyAlbumTrack",
            "artist_id": user_id,
            "album_id": album_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("t.mp3", b"FAKE", "audio/mpeg")}

        resp = await async_client.post(
            "/track/", params=params, files=files, headers=user_headers
        )
        assert resp.status_code == status.HTTP_201_CREATED
        tid = resp.json()["id"]

        bad = params.copy()
        bad["album_id"] = 999999
        resp2 = await async_client.post(
            "/track/", params=bad, files=files, headers=user_headers
        )
        assert resp2.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_track(async_client, tid, user_headers)
        await self._delete_album(async_client, album_id, user_headers)
        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_user(async_client, user_headers)

    async def test_stream_track_variations(self, async_client: AsyncClient):
        genre_id, genre_headers = await self._create_genre(async_client, "StreamGenre")
        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "StreamUser"
        )

        params = {
            "name": "StreamSingle",
            "artist_id": user_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("s.mp3", b"1234567890", "audio/mpeg")}

        create = await async_client.post(
            "/track/single/", params=params, files=files, headers=user_headers
        )
        assert create.status_code == status.HTTP_201_CREATED
        tid = create.json()["id"]

        url = "/track/stream/"
        assert (await async_client.get(url, params={"id": tid})).status_code == 206
        assert (
            await async_client.get(
                url, params={"id": tid}, headers={"Range": "bytes=2-5"}
            )
        ).status_code == 206
        assert (
            await async_client.get(
                url, params={"id": tid}, headers={"Range": "items=0-1"}
            )
        ).status_code == 400
        assert (
            await async_client.get(
                url, params={"id": tid}, headers={"Range": "bytes=999-1000"}
            )
        ).status_code == status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
        assert (
            await async_client.get(url, params={"id": 555555})
        ).status_code == status.HTTP_404_NOT_FOUND

        await self._delete_track(async_client, tid, user_headers)
        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_user(async_client, user_headers)

    async def test_get_track_and_list(self, async_client: AsyncClient):
        genre_id, genre_headers = await self._create_genre(
            async_client, "ListTrackGenre"
        )
        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "ListTrackUser"
        )

        single_params = {
            "name": "ListSingle",
            "artist_id": user_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("ls.mp3", b"ABC", "audio/mpeg")}
        cr = await async_client.post(
            "/track/single/", params=single_params, files=files, headers=user_headers
        )
        tid = cr.json()["id"]

        assert (
            await async_client.get("/track/", params={"id": tid})
        ).status_code == status.HTTP_200_OK
        assert (
            await async_client.get("/tracks/", params={"name": "ListSingle"})
        ).status_code == status.HTTP_200_OK
        assert (
            await async_client.get("/tracks/", params={"name": "NoSuchTrackXYZ"})
        ).status_code == status.HTTP_200_OK

        await self._delete_track(async_client, tid, user_headers)
        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_user(async_client, user_headers)

    async def test_track_image_endpoints(self, async_client: AsyncClient):
        genre_id, genre_headers = await self._create_genre(
            async_client, "ImgTrackGenre"
        )
        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "ImgTrackUser"
        )

        params = {
            "name": "ImgTrack",
            "artist_id": user_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {
            "track_file": ("ti.mp3", b"", "audio/mpeg"),
            "cover_file": ("c.png", b"\x89PNG", "image/png"),
        }
        cr = await async_client.post(
            "/track/single/", params=params, files=files, headers=user_headers
        )
        tid = cr.json()["id"]

        assert (
            await async_client.get("/track/image/", params={"id": tid})
        ).status_code == status.HTTP_200_OK
        assert (
            await async_client.delete(
                "/track/image/", params={"id": tid}, headers=user_headers
            )
        ).status_code == status.HTTP_204_NO_CONTENT
        assert (
            await async_client.get("/track/image/", params={"id": tid})
        ).status_code == status.HTTP_404_NOT_FOUND
        assert (
            await async_client.delete(
                "/track/image/", params={"id": 999999}, headers=user_headers
            )
        ).status_code == status.HTTP_404_NOT_FOUND

        await self._delete_track(async_client, tid, user_headers)
        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_user(async_client, user_headers)

    async def test_update_track_metadata_cover_and_file(
        self, async_client: AsyncClient
    ):
        genre_id, genre_headers = await self._create_genre(
            async_client, "UpdTrackGenre"
        )
        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "UpdTrackUser"
        )

        params = {
            "name": "UpdTrack",
            "artist_id": user_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("up.mp3", b"OLD", "audio/mpeg")}
        cr = await async_client.post(
            "/track/single/", params=params, files=files, headers=user_headers
        )
        assert cr.status_code == status.HTTP_201_CREATED
        tid = cr.json()["id"]

        upd_params = {
            "id": tid,
            "name": "UpdTrackNew",
            "artist_id": user_id,
            "genre_id": genre_id,
            "album_id": cr.json().get("album_id"),
            "release_date": date.today().isoformat(),
        }
        assert (
            await async_client.put("/track/", params=upd_params, headers=user_headers)
        ).status_code == status.HTTP_200_OK
        assert (
            await async_client.put(
                "/track/image/",
                params={"id": tid},
                files={"cover_file": ("new.png", b"\x89PNG", "image/png")},
                headers=user_headers,
            )
        ).status_code == status.HTTP_200_OK
        assert (
            await async_client.put(
                "/track/file/",
                params={"id": tid},
                files={"track_file": ("nf.mp3", b"NEW", "audio/mpeg")},
                headers=user_headers,
            )
        ).status_code == status.HTTP_200_OK

        await self._delete_track(async_client, tid, user_headers)
        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_user(async_client, user_headers)

    async def test_get_tracks_with_filters(self, async_client: AsyncClient):
        genre_id, genre_headers = await self._create_genre(async_client, "FilterGenre")
        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "FilterUser"
        )
        album_id = await self._create_album(
            async_client, user_id, user_headers, "FilterAlbum"
        )

        params = {
            "name": "FilterTrack",
            "artist_id": user_id,
            "album_id": album_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("f.mp3", b"123", "audio/mpeg")}
        cr = await async_client.post(
            "/track/", params=params, files=files, headers=user_headers
        )
        tid = cr.json()["id"]

        r1 = await async_client.get("/tracks/", params={"genre_id": genre_id})
        assert r1.status_code == status.HTTP_200_OK
        assert any(t["id"] == tid for t in r1.json())

        r2 = await async_client.get("/tracks/", params={"artist_id": user_id})
        assert r2.status_code == status.HTTP_200_OK
        assert any(t["id"] == tid for t in r2.json())

        r3 = await async_client.get("/tracks/", params={"album_id": album_id})
        assert r3.status_code == status.HTTP_200_OK
        assert any(t["id"] == tid for t in r3.json())

        await self._delete_track(async_client, tid, user_headers)
        await self._delete_genre(async_client, genre_id, genre_headers)
        await self._delete_album(async_client, album_id, user_headers)
        await self._delete_user(async_client, user_headers)

    async def test_update_track_not_found(self, async_client: AsyncClient):
        params = {
            "id": 999999,
            "name": "GhostTrack",
            "artist_id": 1,
            "album_id": 1,
            "genre_id": 1,
            "release_date": date.today().isoformat(),
        }
        headers = await self._get_auth_headers(async_client)
        resp = await async_client.put("/track/", params=params, headers=headers)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        await self._delete_user(async_client, headers)
