import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestGenreEndpoints:
    async def test_create_genre_success(self, async_client: AsyncClient):
        params = {"name": "RockTest"}
        response = await async_client.post("/genre/", params=params)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "RockTest"
        gid = data["id"]

        await async_client.delete("/genre/", params={"id": gid})

    async def test_create_genre_duplicate(self, async_client: AsyncClient):
        params = {"name": "JazzTest"}
        first = await async_client.post("/genre/", params=params)
        assert first.status_code == status.HTTP_201_CREATED
        gid = first.json()["id"]

        duplicate = await async_client.post("/genre/", params=params)
        assert duplicate.status_code == status.HTTP_400_BAD_REQUEST

        await async_client.delete("/genre/", params={"id": gid})

    async def test_create_genre_validation_error(self, async_client: AsyncClient):
        response = await async_client.post("/genre/", params={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_genre_success(self, async_client: AsyncClient):
        create = await async_client.post("/genre/", params={"name": "PopTest"})
        assert create.status_code == status.HTTP_201_CREATED
        gid = create.json()["id"]

        response = await async_client.get("/genre/", params={"id": gid})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": gid, "name": "PopTest"}

        await async_client.delete("/genre/", params={"id": gid})

    async def test_get_genre_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/genre/", params={"id": 999999})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_genres_list_and_empty(self, async_client: AsyncClient):
        create = await async_client.post("/genre/", params={"name": "UniqueListTest"})
        assert create.status_code == status.HTTP_201_CREATED
        gid = create.json()["id"]

        resp_list = await async_client.get(
            "/genres/", params={"name": "UniqueListTest"}
        )
        assert resp_list.status_code == status.HTTP_200_OK
        data = resp_list.json()
        assert any(g["name"] == "UniqueListTest" for g in data)

        resp_empty = await async_client.get(
            "/genres/", params={"name": "NoSuchGenreXYZ"}
        )
        assert resp_empty.status_code == status.HTTP_200_OK
        assert resp_empty.json() == []

        await async_client.delete("/genre/", params={"id": gid})

    async def test_update_genre_success(self, async_client: AsyncClient):
        create = await async_client.post("/genre/", params={"name": "UpdateTestOld"})
        assert create.status_code == status.HTTP_201_CREATED
        gid = create.json()["id"]

        upd = await async_client.put(
            "/genre/", params={"id": gid, "name": "UpdateTestNew"}
        )
        assert upd.status_code == status.HTTP_200_OK
        assert upd.json()["name"] == "UpdateTestNew"

        await async_client.delete("/genre/", params={"id": gid})

    async def test_update_genre_not_found(self, async_client: AsyncClient):
        upd = await async_client.put(
            "/genre/", params={"id": 123456, "name": "DoesNotExist"}
        )
        assert upd.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_genre_success_and_not_found(self, async_client: AsyncClient):
        create = await async_client.post("/genre/", params={"name": "DeleteTest"})
        assert create.status_code == status.HTTP_201_CREATED
        gid = create.json()["id"]

        resp_del = await async_client.delete("/genre/", params={"id": gid})
        assert resp_del.status_code == status.HTTP_204_NO_CONTENT

        check = await async_client.get("/genre/", params={"id": gid})
        assert check.status_code == status.HTTP_404_NOT_FOUND

        extra = await async_client.delete("/genre/", params={"id": gid})
        assert extra.status_code == status.HTTP_404_NOT_FOUND
