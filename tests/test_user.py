import pytest
from fastapi import status
from httpx import AsyncClient
import uuid


@pytest.mark.asyncio
class TestUserEndpoints:
    def _create_user_data(self, username_prefix: str):
        unique_suffix = f"{username_prefix.lower()}_{uuid.uuid4().hex[:8]}"
        return {
            "name": f"TestUser{username_prefix}",
            "username": f"testuser{unique_suffix}",
            "password": "testpassword",
            "description": f"Description for {username_prefix}",
        }

    async def _create_user(self, client: AsyncClient, username_prefix: str) -> int:
        user_data = self._create_user_data(username_prefix)
        resp = await client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create user (status: {resp.status_code}): {resp.text}"
        )

        resp_get_user = await client.get(
            "/users/artist/", params={"name": user_data["name"]}
        )
        assert resp_get_user.status_code == status.HTTP_200_OK, (
            f"Failed to retrieve user/artist: {resp_get_user.text}"
        )
        users = resp_get_user.json()
        assert len(users) > 0, (
            f"User with username {user_data['username']} not found after creation."
        )
        return users[0]["id"]

    async def _delete_user(self, client: AsyncClient, user_id: int):
        resp = await client.delete("/user/", params={"id": user_id})
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ], f"Failed to delete user {user_id}: {resp.status_code} - {resp.text}"

    async def test_register_user_success(self, async_client: AsyncClient):
        username_prefix = "Success"
        user_data = self._create_user_data(username_prefix)
        resp = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert "token" in resp.json()

        resp_get_user = await async_client.get(
            "/users/artist/", params={"name": user_data["name"]}
        )
        assert resp_get_user.status_code == status.HTTP_200_OK
        user_id = resp_get_user.json()[0]["id"]
        await self._delete_user(async_client, user_id)

    async def test_register_user_with_image_success(self, async_client: AsyncClient):
        username_prefix = "WithImage"
        user_data = self._create_user_data(username_prefix)
        files = {"cover_file": ("profile.png", b"fakeimagedata", "image/png")}
        resp = await async_client.post(
            "/user/register/",
            params=user_data,
            files=files,
        )
        assert resp.status_code == status.HTTP_201_CREATED

        resp_get_user = await async_client.get(
            "/users/artist/", params={"name": user_data["name"]}
        )
        assert resp_get_user.status_code == status.HTTP_200_OK
        user_id = resp_get_user.json()[0]["id"]

        img_resp = await async_client.get("/user/image/", params={"id": user_id})
        assert img_resp.status_code == status.HTTP_200_OK
        assert img_resp.headers["content-type"] == "image/png"
        assert img_resp.content == b"fakeimagedata"

        await self._delete_user(async_client, user_id)

    async def test_register_user_already_exists(self, async_client: AsyncClient):
        username_prefix = "Exists"
        user_data = self._create_user_data(username_prefix)
        resp_initial_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_initial_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to create initial user for already exists test: {resp_initial_reg.text}"
        )

        user_id = (
            await async_client.get("/users/artist/", params={"name": user_data["name"]})
        ).json()[0]["id"]

        resp = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "User already exist" in resp.json()["detail"]

        await self._delete_user(async_client, user_id)

    async def test_register_user_missing_fields(self, async_client: AsyncClient):
        user_data = self._create_user_data("Missing")
        del user_data["username"]

        resp = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_user_success(self, async_client: AsyncClient):
        user_id = await self._create_user(async_client, "GetUser")

        resp = await async_client.get("/user/", params={"id": user_id})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == user_id
        assert resp.json()["username"].startswith("testusergetuser")

        await self._delete_user(async_client, user_id)

    async def test_get_user_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/user/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_artist_success(self, async_client: AsyncClient):
        user_id = await self._create_user(async_client, "GetOneArtist")

        resp = await async_client.get("/user/artist/", params={"id": user_id})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == user_id
        assert "name" in resp.json()

        await self._delete_user(async_client, user_id)

    async def test_get_artist_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/user/artist/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_artists_list_success(self, async_client: AsyncClient):
        user_id_1 = await self._create_user(async_client, "ArtistList1")
        user_id_2 = await self._create_user(async_client, "ArtistList2")

        resp = await async_client.get("users/artist/")
        assert resp.status_code == status.HTTP_200_OK
        artists = resp.json()
        assert any(a["id"] == user_id_1 for a in artists)
        assert any(a["id"] == user_id_2 for a in artists)

        await self._delete_user(async_client, user_id_1)
        await self._delete_user(async_client, user_id_2)

    async def test_get_artists_list_empty(self, async_client: AsyncClient):
        resp = await async_client.get(
            "users/artist/",
            params={"name": "NoSuchArtistXYZ"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    async def test_get_artists_list_with_name_filter(self, async_client: AsyncClient):
        user_id = await self._create_user(async_client, "FilteredArtist")

        user_data = self._create_user_data("FilteredArtist")
        resp = await async_client.get(
            "users/artist/",
            params={"name": user_data["name"]},
        )
        assert resp.status_code == status.HTTP_200_OK
        artists = resp.json()
        assert len(artists) >= 1
        assert any(a["id"] == user_id for a in artists)

        await self._delete_user(async_client, user_id)

    async def test_get_user_image_success(self, async_client: AsyncClient):
        username_prefix = "UserImg"
        user_data = self._create_user_data(username_prefix)
        files = {"cover_file": ("user_img.png", b"testimagedata", "image/png")}
        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files=files,
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED

        user_id = (
            await async_client.get(
                "/users/artist/", params={"name": user_data["name"], "threshold": 1}
            )
        ).json()[0]["id"]

        resp_img = await async_client.get("/user/image/", params={"id": user_id})
        assert resp_img.status_code == status.HTTP_200_OK
        assert resp_img.headers["content-type"] == "image/png"
        assert resp_img.content == b"testimagedata"

        await self._delete_user(async_client, user_id)

    async def test_get_user_image_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/user/image/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_login_user_success(self, async_client: AsyncClient):
        username_prefix = "LoginSuccess"
        user_data = self._create_user_data(username_prefix)
        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to register user: {resp_reg.text}"
        )

        user_id = (
            await async_client.get("/users/artist/", params={"name": user_data["name"]})
        ).json()[0]["id"]

        login_params = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        resp = await async_client.post("/user/login/", params=login_params)
        assert resp.status_code == status.HTTP_200_OK
        assert "token" in resp.json()
        assert resp.json()["next"] == "/home"

        await self._delete_user(async_client, user_id)

    async def test_login_user_invalid_credentials(self, async_client: AsyncClient):
        username_prefix = "LoginFail"
        user_data = self._create_user_data(username_prefix)
        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to register user for invalid credentials test: {resp_reg.text}"
        )

        user_id = (
            await async_client.get("/users/artist/", params={"name": user_data["name"]})
        ).json()[0]["id"]

        login_params = {"username": user_data["username"], "password": "wrongpassword"}
        resp = await async_client.post("/user/login/", params=login_params)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid credentials" in resp.json()["detail"]

        await self._delete_user(async_client, user_id)

    async def test_login_user_not_found(self, async_client: AsyncClient):
        login_params = {"username": "nonexistentuser", "password": "anypassword"}
        resp = await async_client.post("/user/login/", params=login_params)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "User 'nonexistentuser' not found" in resp.json()["detail"]

    async def test_update_user_metadata_success(self, async_client: AsyncClient):
        username_prefix = "UpdateUser"
        user_data = self._create_user_data(username_prefix)
        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to register user for update test: {resp_reg.text}"
        )

        user_id = (
            await async_client.get("/users/artist/", params={"name": user_data["name"]})
        ).json()[0]["id"]

        update_params = {
            "id": user_id,
            "name": "UpdatedName",
            "description": "New description",
            "username": f"updateduser_{uuid.uuid4().hex[:8]}",
            "role": "admin",
        }
        resp = await async_client.put("/user/", params=update_params)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["name"] == "UpdatedName"
        assert resp.json()["description"] == "New description"
        assert resp.json()["username"] == update_params["username"]
        assert resp.json()["role"] == "admin"

        await self._delete_user(async_client, user_id)

    async def test_update_user_metadata_not_found(self, async_client: AsyncClient):
        update_params = {
            "id": 999999,
            "name": "NonExistent",
        }
        resp = await async_client.put("/user/", params=update_params)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_user_image_success(self, async_client: AsyncClient):
        username_prefix = "UpdateImg"
        user_data = self._create_user_data(username_prefix)
        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to register user for image update test: {resp_reg.text}"
        )

        user_id = (
            await async_client.get("/users/artist/", params={"name": user_data["name"]})
        ).json()[0]["id"]

        new_files = {"cover_file": ("new_profile.jpg", b"newimagedata", "image/jpeg")}
        resp = await async_client.put(
            "/user/image/", params={"id": user_id}, files=new_files
        )
        assert resp.status_code == status.HTTP_200_OK

        img_resp = await async_client.get("/user/image/", params={"id": user_id})
        assert img_resp.status_code == status.HTTP_200_OK
        assert img_resp.headers["content-type"] == "image/png"
        assert img_resp.content == b"newimagedata"

        await self._delete_user(async_client, user_id)

    async def test_update_user_image_not_found(self, async_client: AsyncClient):
        new_files = {"cover_file": ("any.jpg", b"anydata", "image/jpeg")}
        resp = await async_client.put(
            "/user/image/", params={"id": 999999}, files=new_files
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_user_success(self, async_client: AsyncClient):
        username_prefix = "DeleteUser"
        user_data = self._create_user_data(username_prefix)
        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to register user for delete test: {resp_reg.text}"
        )

        user_id = (
            await async_client.get("/users/artist/", params={"name": user_data["name"]})
        ).json()[0]["id"]

        resp = await async_client.delete("/user/", params={"id": user_id})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        check_resp = await async_client.get("/user/", params={"id": user_id})
        assert check_resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_user_not_found(self, async_client: AsyncClient):
        resp = await async_client.delete("/user/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_user_image_success(self, async_client: AsyncClient):
        username_prefix = "DelUserImg"
        user_data = self._create_user_data(username_prefix)

        files = {"cover_file": ("del_img.png", b"imagefordelete", "image/png")}
        resp_reg = await async_client.post(
            "/user/register/",
            params=user_data,
            files=files,
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED

        user_id = (
            await async_client.get(
                "/users/artist/",
                params={"name": user_data["name"], "threshold": 1},
            )
        ).json()[0]["id"]

        img_resp_before = await async_client.get("/user/image/", params={"id": user_id})
        assert img_resp_before.status_code == status.HTTP_200_OK

        resp_del_img = await async_client.delete("/user/image/", params={"id": user_id})
        assert resp_del_img.status_code == status.HTTP_204_NO_CONTENT

        img_resp_after = await async_client.get("/user/image/", params={"id": user_id})
        assert img_resp_after.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_user(async_client, user_id)

    async def test_delete_user_image_not_found(self, async_client: AsyncClient):
        resp = await async_client.delete("/user/image/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND
