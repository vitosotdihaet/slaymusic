import pytest
from fastapi import status
from httpx import AsyncClient
from datetime import date


@pytest.mark.asyncio
class TestTrackEndpoints:
    async def _create_user_as_artist(self, client: AsyncClient, username: str) -> int:
        user_params = {
            "name": username,
            "username": username,
            "password": "testpassword",
            "description": "ART",
        }
        resp = await client.post(
            "/user/register/",
            params=user_params,
            files={"cover_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create user: {resp.text}"
        )

        resp_get_artist = await client.get(
            "/users/artist/", params={"username": username}
        )
        assert resp_get_artist.status_code == status.HTTP_200_OK, (
            f"Failed to retrieve artist: {resp_get_artist.text}"
        )
        artists = resp_get_artist.json()
        assert len(artists) > 0, (
            f"Artist with username {username} not found after creation."
        )
        return artists[0]["id"]

    async def _delete_user(self, client: AsyncClient, user_id: int):
        await client.delete("/user/", params={"id": user_id})

    async def _create_genre(self, client: AsyncClient, name="TestGenre") -> int:
        resp = await client.post("/genre/", params={"name": name})
        assert resp.status_code == status.HTTP_201_CREATED
        return resp.json()["id"]

    async def _delete_genre(self, client: AsyncClient, genre_id: int):
        await client.delete("/genre/", params={"id": genre_id})

    async def _create_album(
        self, client: AsyncClient, artist_id: int, name="TestAlbum"
    ) -> int:
        params = {
            "name": name,
            "artist_id": artist_id,
            "release_date": date.today().isoformat(),
        }
        resp = await client.post("/album/", params=params)
        assert resp.status_code == status.HTTP_201_CREATED
        return resp.json()["id"]

    async def _delete_album(self, client: AsyncClient, album_id: int):
        await client.delete("/album/", params={"id": album_id})

    async def test_create_single_success_and_errors(self, async_client: AsyncClient):
        genre_id = await self._create_genre(async_client, "SingleGenre")
        user_id = await self._create_user_as_artist(async_client, "SingleUser")

        params = {
            "name": "MySingle",
            "artist_id": user_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("track.mp3", b"FAKEMP3DATA", "audio/mpeg")}

        resp = await async_client.post("/track/single/", params=params, files=files)
        assert resp.status_code == status.HTTP_201_CREATED
        tid = resp.json()["id"]

        bad = params.copy()
        bad["artist_id"] = 999999
        resp2 = await async_client.post("/track/single/", params=bad, files=files)
        assert resp2.status_code == status.HTTP_400_BAD_REQUEST

        resp3 = await async_client.post("/track/single/", params=params)
        assert resp3.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        await async_client.delete("/track/", params={"id": tid})
        await self._delete_genre(async_client, genre_id)
        await self._delete_user(async_client, user_id)

    async def test_create_track_to_album_success_and_not_found(
        self, async_client: AsyncClient
    ):
        genre_id = await self._create_genre(async_client, "AlbumTrackGenre")
        user_id = await self._create_user_as_artist(async_client, "AlbumTrackUser")
        album_id = await self._create_album(async_client, user_id, "AlbumForTrack")

        params = {
            "name": "MyAlbumTrack",
            "artist_id": user_id,
            "album_id": album_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("t.mp3", b"FAKE", "audio/mpeg")}
        resp = await async_client.post("/track/", params=params, files=files)
        assert resp.status_code == status.HTTP_201_CREATED
        tid = resp.json()["id"]

        bad = params.copy()
        bad["album_id"] = 999999
        resp2 = await async_client.post("/track/", params=bad, files=files)
        assert resp2.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/track/", params={"id": tid})
        await self._delete_album(async_client, album_id)
        await self._delete_genre(async_client, genre_id)
        await self._delete_user(async_client, user_id)

    async def test_stream_track_variations(self, async_client: AsyncClient):
        genre_id = await self._create_genre(async_client, "StreamGenre")
        user_id = await self._create_user_as_artist(async_client, "StreamUser")
        params = {
            "name": "StreamSingle",
            "artist_id": user_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("s.mp3", b"1234567890", "audio/mpeg")}
        create = await async_client.post("/track/single/", params=params, files=files)
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

        await async_client.delete("/track/", params={"id": tid})
        await self._delete_genre(async_client, genre_id)
        await self._delete_user(async_client, user_id)

    async def test_get_track_and_list(self, async_client: AsyncClient):
        genre_id = await self._create_genre(async_client, "ListTrackGenre")
        user_id = await self._create_user_as_artist(async_client, "ListTrackUser")
        single_params = {
            "name": "ListSingle",
            "artist_id": user_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("ls.mp3", b"ABC", "audio/mpeg")}
        cr = await async_client.post(
            "/track/single/", params=single_params, files=files
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

        await async_client.delete("/track/", params={"id": tid})
        await self._delete_genre(async_client, genre_id)
        await self._delete_user(async_client, user_id)

    async def test_track_image_endpoints(self, async_client: AsyncClient):
        genre_id = await self._create_genre(async_client, "ImgTrackGenre")
        user_id = await self._create_user_as_artist(async_client, "ImgTrackUser")
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
        cr = await async_client.post("/track/single/", params=params, files=files)
        tid = cr.json()["id"]

        assert (
            await async_client.get("/track/image/", params={"id": tid})
        ).status_code == status.HTTP_200_OK
        assert (
            await async_client.delete("/track/image/", params={"id": tid})
        ).status_code == status.HTTP_204_NO_CONTENT
        assert (
            await async_client.get("/track/image/", params={"id": tid})
        ).status_code == status.HTTP_404_NOT_FOUND
        assert (
            await async_client.delete("/track/image/", params={"id": 999999})
        ).status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/track/", params={"id": tid})
        await self._delete_genre(async_client, genre_id)
        await self._delete_user(async_client, user_id)

    async def test_update_track_metadata_cover_and_file(
        self, async_client: AsyncClient
    ):
        genre_id = await self._create_genre(async_client, "UpdTrackGenre")
        user_id = await self._create_user_as_artist(async_client, "UpdTrackUser")
        params = {
            "name": "UpdTrack",
            "artist_id": user_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("up.mp3", b"OLD", "audio/mpeg")}
        cr = await async_client.post("/track/single/", params=params, files=files)
        assert cr.status_code == status.HTTP_201_CREATED
        tid = cr.json()["id"]

        upd_params = {
            "id": tid,
            "name": "UpdTrackNew",
            "artist_id": user_id,
            "genre_id": genre_id,
            "album_id": cr.json().get("album_id", 0),
            "release_date": date.today().isoformat(),
        }
        assert (
            await async_client.put("/track/", params=upd_params)
        ).status_code == status.HTTP_200_OK
        assert (
            await async_client.put(
                "/track/image/",
                params={"id": tid},
                files={"cover_file": ("new.png", b"\x89PNG", "image/png")},
            )
        ).status_code == status.HTTP_200_OK
        assert (
            await async_client.put(
                "/track/file/",
                params={"id": tid},
                files={"track_file": ("nf.mp3", b"NEW", "audio/mpeg")},
            )
        ).status_code == status.HTTP_200_OK

        await async_client.delete("/track/", params={"id": tid})
        await self._delete_genre(async_client, genre_id)
        await self._delete_user(async_client, user_id)

    async def test_create_track_missing_fields_and_invalid_types(
        self, async_client: AsyncClient
    ):
        genre_id = await self._create_genre(async_client, "InvalidDataGenre")
        user_id = await self._create_user_as_artist(async_client, "InvalidDataUser")

        params = {
            "name": "BadTrack",
            "artist_id": user_id,
            "album_id": 0,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        resp = await async_client.post("/track/", params=params)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        params["artist_id"] = "abc"
        resp = await async_client.post("/track/", params=params)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        await self._delete_genre(async_client, genre_id)
        await self._delete_user(async_client, user_id)

    async def test_get_tracks_with_filters(self, async_client: AsyncClient):
        genre_id = await self._create_genre(async_client, "FilterGenre")
        user_id = await self._create_user_as_artist(async_client, "FilterUser")
        album_id = await self._create_album(async_client, user_id, "FilterAlbum")

        params = {
            "name": "FilterTrack",
            "artist_id": user_id,
            "album_id": album_id,
            "genre_id": genre_id,
            "release_date": date.today().isoformat(),
        }
        files = {"track_file": ("f.mp3", b"123", "audio/mpeg")}
        cr = await async_client.post("/track/", params=params, files=files)
        tid = cr.json()["id"]

        r1 = await async_client.get("/tracks/", params={"genre_id": genre_id})
        assert r1.status_code == status.HTTP_200_OK
        assert any(t["id"] == tid for t in r1.json())

        r2 = await async_client.get("/tracks/", params={"artist_id": user_id})
        assert r2.status_code == status.HTTP_200_OK

        r3 = await async_client.get("/tracks/", params={"album_id": album_id})
        assert r3.status_code == status.HTTP_200_OK

        await async_client.delete("/track/", params={"id": tid})
        await self._delete_genre(async_client, genre_id)
        await self._delete_album(async_client, album_id)
        await self._delete_user(async_client, user_id)

    async def test_update_track_not_found(self, async_client: AsyncClient):
        params = {
            "id": 999999,
            "name": "GhostTrack",
            "artist_id": 1,
            "album_id": 1,
            "genre_id": 1,
            "release_date": date.today().isoformat(),
        }
        resp = await async_client.put("/track/", params=params)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
