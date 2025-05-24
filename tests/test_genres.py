import pytest
from fastapi import status
from httpx import AsyncClient
import uuid


@pytest.mark.asyncio
class TestGenreEndpoints:
    async def _get_auth_headers(self, client: AsyncClient, username: str | None = None):
        if username is None:
            username = f"testuser_{uuid.uuid4().hex[:8]}"
        register_data = {
            "name": "testicle",
            "username": username,
            "password": "testpass",
        }
        response = await client.post("/user/register/", params=register_data)
        if response.status_code != status.HTTP_201_CREATED:
            response = await client.post(
                "/user/login/",
                params={"username": username, "password": "testpass"},
            )

        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    async def _upgrade_user(self, client: AsyncClient, headers):
        resp = await client.put("/user/", params={"role": "admin"}, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        return resp

    async def _delete_user(self, client: AsyncClient, headers):
        resp = await client.delete("/user/", headers=headers)
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ], f"Failed to delete user: {resp.status_code} - {resp.text}"

    async def test_create_genre_success(self, async_client: AsyncClient):
        headers = await self._get_auth_headers(async_client)
        resp = await self._upgrade_user(async_client, headers)
        data = resp.json()
        username = data["username"]

        headers = await self._get_auth_headers(async_client, username)
        params = {"name": "RockTest"}
        response = await async_client.post("/genre/", params=params, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "RockTest"
        gid = data["id"]

        await async_client.delete("/genre/", params={"id": gid}, headers=headers)
        await self._delete_user(async_client, headers)

    async def test_create_genre_duplicate(self, async_client: AsyncClient):
        headers = await self._get_auth_headers(async_client)
        resp = await self._upgrade_user(async_client, headers)
        data = resp.json()
        username = data["username"]

        auth_headers = await self._get_auth_headers(async_client, username)
        params = {"name": "JazzTest"}
        first = await async_client.post("/genre/", params=params, headers=auth_headers)
        assert first.status_code == status.HTTP_201_CREATED
        gid = first.json()["id"]

        duplicate = await async_client.post(
            "/genre/", params=params, headers=auth_headers
        )
        assert duplicate.status_code == status.HTTP_400_BAD_REQUEST

        await async_client.delete("/genre/", params={"id": gid}, headers=auth_headers)
        await self._delete_user(async_client, headers)

    async def test_get_genre_success(self, async_client: AsyncClient):
        headers = await self._get_auth_headers(async_client)
        resp = await self._upgrade_user(async_client, headers)
        data = resp.json()
        username = data["username"]

        auth_headers = await self._get_auth_headers(async_client, username)
        create = await async_client.post(
            "/genre/", params={"name": "PopTest"}, headers=auth_headers
        )
        assert create.status_code == status.HTTP_201_CREATED
        gid = create.json()["id"]

        response = await async_client.get(
            "/genre/", params={"id": gid}, headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        await async_client.delete("/genre/", params={"id": gid}, headers=auth_headers)
        await self._delete_user(async_client, headers)

    async def test_get_genre_not_found(self, async_client: AsyncClient):
        headers = await self._get_auth_headers(async_client)
        resp = await self._upgrade_user(async_client, headers)
        data = resp.json()
        username = data["username"]

        auth_headers = await self._get_auth_headers(async_client, username)
        response = await async_client.get(
            "/genre/", params={"id": 999999}, headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        await self._delete_user(async_client, headers)

    async def test_update_genre_success(self, async_client: AsyncClient):
        headers = await self._get_auth_headers(async_client)
        resp = await self._upgrade_user(async_client, headers)
        data = resp.json()
        username = data["username"]

        auth_headers = await self._get_auth_headers(async_client, username)
        create = await async_client.post(
            "/genre/", params={"name": "UpdateTestOld"}, headers=auth_headers
        )
        assert create.status_code == status.HTTP_201_CREATED
        gid = create.json()["id"]

        upd = await async_client.put(
            "/genre/", params={"id": gid, "name": "UpdateTestNew"}, headers=auth_headers
        )
        assert upd.status_code == status.HTTP_200_OK
        assert upd.json()["name"] == "UpdateTestNew"

        await async_client.delete("/genre/", params={"id": gid}, headers=auth_headers)
        await self._delete_user(async_client, headers)

    async def test_delete_genre_success_and_not_found(self, async_client: AsyncClient):
        headers = await self._get_auth_headers(async_client)
        resp = await self._upgrade_user(async_client, headers)
        data = resp.json()
        username = data["username"]

        auth_headers = await self._get_auth_headers(async_client, username)
        create = await async_client.post(
            "/genre/", params={"name": "DeleteTest"}, headers=auth_headers
        )
        assert create.status_code == status.HTTP_201_CREATED
        gid = create.json()["id"]

        resp_del = await async_client.delete(
            "/genre/", params={"id": gid}, headers=auth_headers
        )
        assert resp_del.status_code == status.HTTP_204_NO_CONTENT

        check = await async_client.get(
            "/genre/", params={"id": gid}, headers=auth_headers
        )
        assert check.status_code == status.HTTP_404_NOT_FOUND

        extra = await async_client.delete(
            "/genre/", params={"id": gid}, headers=auth_headers
        )
        assert extra.status_code == status.HTTP_404_NOT_FOUND
        await self._delete_user(async_client, headers)
