import pytest
from fastapi import status
from httpx import AsyncClient
import uuid


@pytest.mark.asyncio
class TestUserEndpoints:
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

    async def _create_and_get_user_id(
        self, async_client: AsyncClient, username_prefix: str, has_image: bool = False
    ):
        username = f"testuser{username_prefix}_{uuid.uuid4().hex[:8]}"
        user_data = {
            "name": f"TestName{username_prefix}",
            "username": username,
            "password": "testpass",
        }
        files = (
            {"cover_file": ("profile.png", b"fakeimagedata", "image/png")}
            if has_image
            else {"cover_file": ("", "", "")}
        )

        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files=files,
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to register user: {resp_reg.text}"
        )

        login_params = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        resp_login = await async_client.post("/user/login/", params=login_params)
        assert resp_login.status_code == status.HTTP_200_OK

        headers = await self._get_auth_headers(async_client, username)
        resp_get_user = await async_client.get("/user/", headers=headers)
        assert resp_get_user.status_code == status.HTTP_200_OK
        return resp_get_user.json()["id"], headers

    async def test_register_user_success(self, async_client: AsyncClient):
        username = f"Success_{uuid.uuid4().hex[:8]}"
        user_data = {
            "name": "TestUserSuccess",
            "username": username,
            "password": "testpass",
        }
        resp = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert "token" in resp.json()

        headers = {"Authorization": f"Bearer {resp.json()['token']}"}
        await self._delete_user(async_client, headers)

    async def test_register_user_with_image_success(self, async_client: AsyncClient):
        username = f"WithImage_{uuid.uuid4().hex[:8]}"
        user_data = {
            "name": "TestUserWithImage",
            "username": username,
            "password": "testpass",
        }
        files = {"cover_file": ("profile.png", b"fakeimagedata", "image/png")}
        resp = await async_client.post(
            "/user/register/",
            params=user_data,
            files=files,
        )
        assert resp.status_code == status.HTTP_201_CREATED

        headers = {"Authorization": f"Bearer {resp.json()['token']}"}

        resp_get_user = await async_client.get("/user/", headers=headers)
        assert resp_get_user.status_code == status.HTTP_200_OK
        user_id = resp_get_user.json()["id"]

        img_resp = await async_client.get("/user/image/", params={"id": user_id})
        assert img_resp.status_code == status.HTTP_200_OK
        assert img_resp.headers["content-type"] == "image/png"
        assert img_resp.content == b"fakeimagedata"

        await self._delete_user(async_client, headers)

    async def test_register_user_already_exists(self, async_client: AsyncClient):
        username = f"Exists_{uuid.uuid4().hex[:8]}"
        user_data = {
            "name": "TestUserExists",
            "username": username,
            "password": "testpass",
        }
        resp_initial_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_initial_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to create initial user for already exists test: {resp_initial_reg.text}"
        )

        headers_to_delete = {
            "Authorization": f"Bearer {resp_initial_reg.json()['token']}"
        }

        resp = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "User already exist" in resp.json()["detail"]

        await self._delete_user(async_client, headers_to_delete)

    async def test_get_user_success(self, async_client: AsyncClient):
        user_id, headers = await self._create_and_get_user_id(async_client, "GetUser")

        resp = await async_client.get("/user/", params={"id": user_id}, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == user_id
        assert resp.json()["username"].startswith("testuserGetUser")

        await self._delete_user(async_client, headers)

    async def test_get_user_not_login(self, async_client: AsyncClient):
        resp = await async_client.get("/user/", params={"id": 999999})
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_artists_list_with_name_filter(self, async_client: AsyncClient):
        user_id, headers = await self._create_and_get_user_id(
            async_client, "FilteredArtist"
        )

        resp_get_user = await async_client.get("/user/", headers=headers)
        assert resp_get_user.status_code == status.HTTP_200_OK
        user_name = resp_get_user.json()["name"]

        resp = await async_client.get(
            "/users/artist/",
            params={"name": user_name},
            headers=headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        artists = resp.json()
        assert len(artists) >= 1
        assert any(a["id"] == user_id for a in artists)

        await self._delete_user(async_client, headers)

    async def test_get_user_image_success(self, async_client: AsyncClient):
        user_id, headers = await self._create_and_get_user_id(
            async_client, "UserImg", has_image=True
        )

        resp_img = await async_client.get("/user/image/", params={"id": user_id})
        assert resp_img.status_code == status.HTTP_200_OK
        assert resp_img.headers["content-type"] == "image/png"
        assert resp_img.content == b"fakeimagedata"

        await self._delete_user(async_client, headers)

    async def test_login_user_success(self, async_client: AsyncClient):
        username = f"LoginSuccess_{uuid.uuid4().hex[:8]}"
        user_data = {
            "name": "TestLoginSuccess",
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

        login_params = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        resp = await async_client.post("/user/login/", params=login_params)
        assert resp.status_code == status.HTTP_200_OK
        assert "token" in resp.json()
        assert resp.json()["next"] == "/home"

        headers = {"Authorization": f"Bearer {resp.json()['token']}"}
        await self._delete_user(async_client, headers)

    async def test_login_user_invalid_credentials(self, async_client: AsyncClient):
        username = f"LoginFail_{uuid.uuid4().hex[:8]}"
        user_data = {
            "name": "TestLoginFail",
            "username": username,
            "password": "testpass",
        }
        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to register user for invalid credentials test: {resp_reg.text}"
        )

        login_params = {"username": user_data["username"], "password": "wrongpassword"}
        resp = await async_client.post("/user/login/", params=login_params)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid credentials" in resp.json()["detail"]

        headers = {"Authorization": f"Bearer {resp_reg.json()['token']}"}
        await self._delete_user(async_client, headers)

    async def test_update_user_metadata_success(self, async_client: AsyncClient):
        headers = await self._get_auth_headers(async_client, "UpdateUser")

        update_params = {
            "name": "UpdatedName",
            "description": "New description",
            "username": f"updateduser_{uuid.uuid4().hex[:8]}",
        }

        resp = await async_client.put("/user/", params=update_params, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["name"] == "UpdatedName"
        assert resp.json()["description"] == "New description"
        assert resp.json()["username"] == update_params["username"]

        await self._delete_user(async_client, headers)

    async def test_update_user_image_success(self, async_client: AsyncClient):
        user_id, headers = await self._create_and_get_user_id(async_client, "UpdateImg")

        new_files = {"cover_file": ("new_profile.jpg", b"newimagedata", "image/jpeg")}
        resp = await async_client.put(
            "/user/image/",
            params={"id": user_id},
            files=new_files,
            headers=headers,
        )
        assert resp.status_code == status.HTTP_200_OK

        img_resp = await async_client.get("/user/image/", params={"id": user_id})
        assert img_resp.status_code == status.HTTP_200_OK
        assert img_resp.headers["content-type"] == "image/png"
        assert img_resp.content == b"newimagedata"

        await self._delete_user(async_client, headers)

    async def test_delete_user_success(self, async_client: AsyncClient):
        user_id, headers = await self._create_and_get_user_id(
            async_client, "DeleteUser"
        )

        resp = await async_client.delete("/user/", headers=headers)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        check_resp = await async_client.get(
            "/user/", params={"id": user_id}, headers=headers
        )
        assert check_resp.status_code == status.HTTP_404_NOT_FOUND
