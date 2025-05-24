import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAlbumEndpoints:
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

    async def test_create_album_without_image_success(self, async_client: AsyncClient):
        user_id = await self._create_user_as_artist(async_client, "NoImgAlbumUser")
        params = {
            "name": "NoImgAlbum",
            "artist_id": user_id,
            "release_date": "2025-01-01",
        }
        resp = await async_client.post("/album/", params=params)
        assert resp.status_code == status.HTTP_201_CREATED
        aid = resp.json()["id"]

        await async_client.delete("/album/", params={"id": aid})
        await async_client.delete("/user/", params={"id": user_id})

    async def test_create_album_with_image_success(self, async_client: AsyncClient):
        user_id = await self._create_user_as_artist(async_client, "ImgAlbumUser")
        params = {
            "name": "ImgAlbum",
            "artist_id": user_id,
            "release_date": "2025-02-02",
        }
        files = {"cover_file": ("cover.png", b"fake", "image/png")}
        resp = await async_client.post("/album/", params=params, files=files)
        assert resp.status_code == status.HTTP_201_CREATED
        aid = resp.json()["id"]

        await async_client.delete("/album/", params={"id": aid})
        await async_client.delete("/user/", params={"id": user_id})

    async def test_create_album_validation_error(self, async_client: AsyncClient):
        resp = await async_client.post("/album/", params={})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_album_success(self, async_client: AsyncClient):
        user_id = await self._create_user_as_artist(async_client, "GetAlbUser")
        create = await async_client.post(
            "/album/",
            params={
                "name": "GetAlbum",
                "artist_id": user_id,
                "release_date": "2025-03-03",
            },
        )
        aid = create.json()["id"]

        resp = await async_client.get("/album/", params={"id": aid})
        assert resp.status_code == status.HTTP_200_OK

        await async_client.delete("/album/", params={"id": aid})
        await async_client.delete("/user/", params={"id": user_id})

    async def test_get_album_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/album/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_albums_list_and_empty(self, async_client: AsyncClient):
        user_id = await self._create_user_as_artist(async_client, "ListAlbUser")
        create = await async_client.post(
            "/album/",
            params={
                "name": "ListAlbum",
                "artist_id": user_id,
                "release_date": "2025-04-04",
            },
        )
        aid = create.json()["id"]

        resp = await async_client.get("/albums/", params={"name": "ListAlbum"})
        assert resp.status_code == status.HTTP_200_OK

        resp_empty = await async_client.get(
            "/albums/", params={"name": "NoSuchAlbumXYZ"}
        )
        assert resp_empty.status_code == status.HTTP_200_OK

        await async_client.delete("/album/", params={"id": aid})
        await async_client.delete("/user/", params={"id": user_id})

    async def test_get_album_image_success_and_not_found(
        self, async_client: AsyncClient
    ):
        user_id = await self._create_user_as_artist(async_client, "ImgFetchAlbUser")
        files = {"cover_file": ("c.png", b"\x89PNG", "image/png")}
        create = await async_client.post(
            "/album/",
            params={
                "name": "ImgFetchAlbum",
                "artist_id": user_id,
                "release_date": "2025-05-05",
            },
            files=files,
        )
        aid = create.json()["id"]

        resp = await async_client.get("/album/image/", params={"id": aid})
        assert resp.status_code == status.HTTP_200_OK

        resp_nf = await async_client.get("/album/image/", params={"id": 123456})
        assert resp_nf.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/album/", params={"id": aid})
        await async_client.delete("/user/", params={"id": user_id})

    async def test_update_metadata_success_and_not_found(
        self, async_client: AsyncClient
    ):
        user_id = await self._create_user_as_artist(async_client, "MetaAlbUser")
        create = await async_client.post(
            "/album/",
            params={
                "name": "MetaAlbumOld",
                "artist_id": user_id,
                "release_date": "2025-06-06",
            },
        )
        aid = create.json()["id"]

        upd = await async_client.put(
            "/album/",
            params={
                "id": aid,
                "name": "MetaAlbumNew",
                "artist_id": user_id,
                "release_date": "2025-07-07",
            },
        )
        assert upd.status_code == status.HTTP_200_OK

        nf = await async_client.put(
            "/album/",
            params={
                "id": 555555,
                "name": "X",
                "artist_id": user_id,
                "release_date": "2025-08-08",
            },
        )
        assert nf.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/album/", params={"id": aid})
        await async_client.delete("/user/", params={"id": user_id})

    async def test_update_image_success_and_not_found(self, async_client: AsyncClient):
        user_id = await self._create_user_as_artist(async_client, "UpdImgAlbUser")
        create = await async_client.post(
            "/album/",
            params={
                "name": "UpdImgAlbum",
                "artist_id": user_id,
                "release_date": "2025-09-09",
            },
        )
        aid = create.json()["id"]

        files = {"cover_file": ("new.png", b"\x89PNGDATA", "image/png")}
        upd = await async_client.put("/album/image/", params={"id": aid}, files=files)
        assert upd.status_code == status.HTTP_200_OK

        fetch = await async_client.get("/album/image/", params={"id": aid})
        assert fetch.status_code == status.HTTP_200_OK

        nf = await async_client.put("/album/image/", params={"id": 999999}, files=files)
        assert nf.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/album/", params={"id": aid})
        await async_client.delete("/user/", params={"id": user_id})

    async def test_delete_album_success_and_not_found(self, async_client: AsyncClient):
        user_id = await self._create_user_as_artist(async_client, "DelAlbUser")
        create = await async_client.post(
            "/album/",
            params={
                "name": "DelAlbum",
                "artist_id": user_id,
                "release_date": "2025-10-10",
            },
        )
        aid = create.json()["id"]

        resp = await async_client.delete("/album/", params={"id": aid})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        chk = await async_client.get("/album/", params={"id": aid})
        assert chk.status_code == status.HTTP_404_NOT_FOUND

        resp2 = await async_client.delete("/album/", params={"id": 777777})
        assert resp2.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/user/", params={"id": user_id})

    async def test_delete_album_image_success_and_not_found(
        self, async_client: AsyncClient
    ):
        user_id = await self._create_user_as_artist(async_client, "DelImgAlbUser")
        files = {"cover_file": ("to_del.png", b"\x89PNG", "image/png")}
        create = await async_client.post(
            "/album/",
            params={
                "name": "DelImgAlbum",
                "artist_id": user_id,
                "release_date": "2025-11-11",
            },
            files=files,
        )
        aid = create.json()["id"]

        resp = await async_client.delete("/album/image/", params={"id": aid})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        fetch = await async_client.get("/album/image/", params={"id": aid})
        assert fetch.status_code == status.HTTP_404_NOT_FOUND

        resp2 = await async_client.delete("/album/image/", params={"id": 888888})
        assert resp2.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/album/", params={"id": aid})
        await async_client.delete("/user/", params={"id": user_id})

    async def test_create_album_with_nonexistent_artist(
        self, async_client: AsyncClient
    ):
        params = {
            "name": "InvalidArtistAlbum",
            "artist_id": 999999,
            "release_date": "2025-01-01",
        }
        resp = await async_client.post("/album/", params=params)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_albums_with_date_filter(self, async_client: AsyncClient):
        user_id = await self._create_user_as_artist(async_client, "FilterDateUser")
        params = {
            "name": "FilterAlbum",
            "artist_id": user_id,
            "release_date": "2025-05-05",
        }
        create_resp = await async_client.post("/album/", params=params)
        aid = create_resp.json()["id"]

        resp = await async_client.get(
            "/albums/",
            params={"search_start": "2025-01-01", "search_end": "2025-12-31"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert any(album["id"] == aid for album in resp.json())

        await async_client.delete("/album/", params={"id": aid})
        await async_client.delete("/user/", params={"id": user_id})
