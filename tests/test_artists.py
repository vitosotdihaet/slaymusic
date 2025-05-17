import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestArtistEndpoints:
    async def test_create_artist_without_image_success(self, async_client: AsyncClient):
        params = {"name": "ArtistNoImgTest", "description": "Just a test"}
        response = await async_client.post("/artist/", params=params)
        assert response.status_code == status.HTTP_201_CREATED
        aid = response.json()["id"]

        await async_client.delete("/artist/", params={"id": aid})

    async def test_create_artist_with_image_success(self, async_client: AsyncClient):
        params = {"name": "ArtistWithImgTest", "description": "Has cover"}
        files = {"cover_file": ("cover.png", b"fakepngbytes", "image/png")}
        response = await async_client.post("/artist/", params=params, files=files)
        assert response.status_code == status.HTTP_201_CREATED
        aid = response.json()["id"]

        await async_client.delete("/artist/", params={"id": aid})

    async def test_create_artist_validation_error(self, async_client: AsyncClient):
        response = await async_client.post("/artist/", params={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_artist_success(self, async_client: AsyncClient):
        create = await async_client.post(
            "/artist/", params={"name": "GetArtistTest", "description": "Fetch me"}
        )
        aid = create.json()["id"]

        response = await async_client.get("/artist/", params={"id": aid})
        assert response.status_code == status.HTTP_200_OK

        await async_client.delete("/artist/", params={"id": aid})

    async def test_get_artist_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/artist/", params={"id": 999999})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_artists_list_and_empty(self, async_client: AsyncClient):
        create = await async_client.post(
            "/artist/", params={"name": "ListArtistTest", "description": "List me"}
        )
        aid = create.json()["id"]

        resp = await async_client.get("/artists/", params={"name": "ListArtistTest"})
        assert resp.status_code == status.HTTP_200_OK

        resp_empty = await async_client.get(
            "/artists/", params={"name": "NoSuchArtistXYZ"}
        )
        assert resp_empty.status_code == status.HTTP_200_OK
        assert resp_empty.json() == []

        await async_client.delete("/artist/", params={"id": aid})

    async def test_get_image_success_and_not_found(self, async_client: AsyncClient):
        files = {"cover_file": ("cover2.png", b"\x89PNG\r\n", "image/png")}
        create = await async_client.post(
            "/artist/",
            params={"name": "ImgFetchTest", "description": "Image"},
            files=files,
        )
        aid = create.json()["id"]

        resp = await async_client.get("/artist/image/", params={"id": aid})
        assert resp.status_code == status.HTTP_200_OK

        resp_nf = await async_client.get("/artist/image/", params={"id": 123456})
        assert resp_nf.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/artist/", params={"id": aid})

    async def test_update_metadata_success_and_not_found(
        self, async_client: AsyncClient
    ):
        create = await async_client.post(
            "/artist/", params={"name": "MetaOld", "description": "Old"}
        )
        aid = create.json()["id"]

        upd = await async_client.put(
            "/artist/", params={"id": aid, "name": "MetaNew", "description": "New"}
        )
        assert upd.status_code == status.HTTP_200_OK

        nf = await async_client.put(
            "/artist/", params={"id": 555555, "name": "X", "description": "Y"}
        )
        assert nf.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/artist/", params={"id": aid})

    async def test_update_image_success_and_not_found(self, async_client: AsyncClient):
        create = await async_client.post(
            "/artist/", params={"name": "ImgUpdTest", "description": "Will get img"}
        )
        aid = create.json()["id"]

        files = {"cover_file": ("new.png", b"\x89PNGDATA", "image/png")}
        upd = await async_client.put("/artist/image/", params={"id": aid}, files=files)
        assert upd.status_code == status.HTTP_200_OK

        fetch = await async_client.get("/artist/image/", params={"id": aid})
        assert fetch.status_code == status.HTTP_200_OK

        nf = await async_client.put(
            "/artist/image/", params={"id": 999999}, files=files
        )
        assert nf.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/artist/", params={"id": aid})

    async def test_delete_artist_success_and_not_found(self, async_client: AsyncClient):
        create = await async_client.post(
            "/artist/", params={"name": "DelArtistTest", "description": "To delete"}
        )
        aid = create.json()["id"]

        resp = await async_client.delete("/artist/", params={"id": aid})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        chk = await async_client.get("/artist/", params={"id": aid})
        assert chk.status_code == status.HTTP_404_NOT_FOUND

        resp2 = await async_client.delete("/artist/", params={"id": 777777})
        assert resp2.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_artist_image_success_and_not_found(
        self, async_client: AsyncClient
    ):
        files = {"cover_file": ("to_del.png", b"\x89PNG", "image/png")}
        create = await async_client.post(
            "/artist/",
            params={"name": "DelImgTest", "description": "Img delete"},
            files=files,
        )
        aid = create.json()["id"]

        resp = await async_client.delete("/artist/image/", params={"id": aid})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        fetch = await async_client.get("/artist/image/", params={"id": aid})
        assert fetch.status_code == status.HTTP_404_NOT_FOUND

        resp2 = await async_client.delete("/artist/image/", params={"id": 888888})
        assert resp2.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/artist/", params={"id": aid})
