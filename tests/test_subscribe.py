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
            "name": "testname",
            "username": username,
            "password": "testpass",
        }
        response = await client.post("/user/register/", json=register_data)
        if response.status_code != status.HTTP_201_CREATED:
            response = await client.post(
                "/user/login/",
                json={"username": username, "password": "testpass"},
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

    async def test_subscribe_to_user_success(self, async_client: AsyncClient):
        (
            subscriber_id,
            subscriber_headers,
        ) = await self._create_user_and_get_auth_headers(async_client, "Subscriber1")
        artist_id, artist_headers = await self._create_user_and_get_auth_headers(
            async_client, "Artist1"
        )

        subscribe_params = {"artist_id": artist_id}
        resp = await async_client.post(
            "/user/subscribe", params=subscribe_params, headers=subscriber_headers
        )
        assert resp.status_code == status.HTTP_201_CREATED

        subscribers_resp = await async_client.get(
            "/user/subscribers",
            params={"id": artist_id},
            headers=artist_headers,
        )
        assert subscribers_resp.status_code == status.HTTP_200_OK
        subscribers_list = subscribers_resp.json()
        assert any(s["id"] == subscriber_id for s in subscribers_list)

        subscriptions_resp = await async_client.get(
            "/user/subscriptions",
            params={"id": subscriber_id},
            headers=subscriber_headers,
        )
        assert subscriptions_resp.status_code == status.HTTP_200_OK
        subscriptions_list = subscriptions_resp.json()
        assert any(a["id"] == artist_id for a in subscriptions_list)

        await self._delete_user(async_client, subscriber_headers)
        await self._delete_user(async_client, artist_headers)

    async def test_subscribe_to_self_forbidden(self, async_client: AsyncClient):
        user_id, user_headers = await self._create_user_and_get_auth_headers(
            async_client, "SelfSubscribe"
        )

        subscribe_params = {"artist_id": user_id}
        resp = await async_client.post(
            "/user/subscribe", params=subscribe_params, headers=user_headers
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert "Cannot subscribe to self" in resp.json()["detail"]

        await self._delete_user(async_client, user_headers)

    async def test_subscribe_already_exist(self, async_client: AsyncClient):
        (
            subscriber_id,
            subscriber_headers,
        ) = await self._create_user_and_get_auth_headers(async_client, "SubExist1")
        artist_id, artist_headers = await self._create_user_and_get_auth_headers(
            async_client, "ArtExist1"
        )

        subscribe_params = {"artist_id": artist_id}

        resp1 = await async_client.post(
            "/user/subscribe", params=subscribe_params, headers=subscriber_headers
        )
        assert resp1.status_code == status.HTTP_201_CREATED

        resp2 = await async_client.post(
            "/user/subscribe", params=subscribe_params, headers=subscriber_headers
        )
        assert resp2.status_code == status.HTTP_400_BAD_REQUEST

        await self._delete_user(async_client, subscriber_headers)
        await self._delete_user(async_client, artist_headers)

    async def test_subscribe_user_not_found(self, async_client: AsyncClient):
        (
            subscriber_id,
            subscriber_headers,
        ) = await self._create_user_and_get_auth_headers(async_client, "SubNotFound")

        subscribe_params = {"artist_id": 999999}
        resp = await async_client.post(
            "/user/subscribe", params=subscribe_params, headers=subscriber_headers
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "User '999999' not found" in resp.json()["detail"]

        await self._delete_user(async_client, subscriber_headers)

    async def test_unsubscribe_success(self, async_client: AsyncClient):
        (
            subscriber_id,
            subscriber_headers,
        ) = await self._create_user_and_get_auth_headers(async_client, "UnsubSuc1")
        artist_id, artist_headers = await self._create_user_and_get_auth_headers(
            async_client, "UnsubSucArt1"
        )

        subscribe_params = {"artist_id": artist_id}

        resp_sub = await async_client.post(
            "/user/subscribe", params=subscribe_params, headers=subscriber_headers
        )
        assert resp_sub.status_code == status.HTTP_201_CREATED

        resp_unsub = await async_client.post(
            "/user/unsubscribe",
            params=subscribe_params,
            headers=subscriber_headers,
        )
        assert resp_unsub.status_code == status.HTTP_204_NO_CONTENT

        subscriptions_resp = await async_client.get(
            "/user/subscriptions",
            params={"id": subscriber_id},
            headers=subscriber_headers,
        )
        assert subscriptions_resp.status_code == status.HTTP_200_OK
        subscriptions_list = subscriptions_resp.json()
        assert not any(a["id"] == artist_id for a in subscriptions_list)

        await self._delete_user(async_client, subscriber_headers)
        await self._delete_user(async_client, artist_headers)

    async def test_get_subscriptions_success(self, async_client: AsyncClient):
        (
            subscriber_id,
            subscriber_headers,
        ) = await self._create_user_and_get_auth_headers(async_client, "GetSubs")
        artist1_id, artist1_headers = await self._create_user_and_get_auth_headers(
            async_client, "GetSubsArt1"
        )
        artist2_id, artist2_headers = await self._create_user_and_get_auth_headers(
            async_client, "GetSubsArt2"
        )

        await async_client.post(
            "/user/subscribe",
            params={"artist_id": artist1_id},
            headers=subscriber_headers,
        )
        await async_client.post(
            "/user/subscribe",
            params={"artist_id": artist2_id},
            headers=subscriber_headers,
        )

        resp = await async_client.get(
            "/user/subscriptions",
            params={"id": subscriber_id},
            headers=subscriber_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        subscriptions = resp.json()
        assert len(subscriptions) >= 2
        assert any(s["id"] == artist1_id for s in subscriptions)
        assert any(s["id"] == artist2_id for s in subscriptions)

        await self._delete_user(async_client, subscriber_headers)
        await self._delete_user(async_client, artist1_headers)
        await self._delete_user(async_client, artist2_headers)

    async def test_get_subscriber_count_success(self, async_client: AsyncClient):
        artist_id, artist_headers = await self._create_user_and_get_auth_headers(
            async_client, "CountArtist"
        )
        (
            subscriber1_id,
            subscriber1_headers,
        ) = await self._create_user_and_get_auth_headers(async_client, "CountSub1")
        (
            subscriber2_id,
            subscriber2_headers,
        ) = await self._create_user_and_get_auth_headers(async_client, "CountSub2")

        await async_client.post(
            "/user/subscribe",
            params={"artist_id": artist_id},
            headers=subscriber1_headers,
        )
        await async_client.post(
            "/user/subscribe",
            params={"artist_id": artist_id},
            headers=subscriber2_headers,
        )

        resp = await async_client.get(
            "/user/subscriber-count",
            params={"id": artist_id},
            headers=artist_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["count"] == 2

        await self._delete_user(async_client, artist_headers)
        await self._delete_user(async_client, subscriber1_headers)
        await self._delete_user(async_client, subscriber2_headers)
