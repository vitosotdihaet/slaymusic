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

    async def _create_user_and_get_id(
        self, client: AsyncClient, username_prefix: str
    ) -> int:
        user_data = self._create_user_data(username_prefix)
        resp = await client.post(
            "/user/register/",
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create user during setup: {resp.text}"
        )

        resp_get_user = await client.get(
            "/users/artist/", params={"name": user_data["name"]}
        )
        assert resp_get_user.status_code == status.HTTP_200_OK, (
            f"Failed to retrieve user by username after creation: {resp_get_user.text}"
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

    async def test_subscribe_to_user_success(self, async_client: AsyncClient):
        subscriber_id = await self._create_user_and_get_id(async_client, "Subscriber1")
        artist_id = await self._create_user_and_get_id(async_client, "Artist1")

        subscribe_params = {"subscriber_id": subscriber_id, "artist_id": artist_id}
        resp = await async_client.post("/user/subscribe", params=subscribe_params)
        assert resp.status_code == status.HTTP_201_CREATED

        subscribers_resp = await async_client.get(
            "/user/subscribers", params={"id": artist_id}
        )
        assert subscribers_resp.status_code == status.HTTP_200_OK
        subscribers_list = subscribers_resp.json()
        assert any(s["id"] == subscriber_id for s in subscribers_list)

        subscriptions_resp = await async_client.get(
            "/user/subscriptions", params={"id": subscriber_id}
        )
        assert subscriptions_resp.status_code == status.HTTP_200_OK
        subscriptions_list = subscriptions_resp.json()
        assert any(a["id"] == artist_id for a in subscriptions_list)

        await self._delete_user(async_client, subscriber_id)
        await self._delete_user(async_client, artist_id)

    async def test_subscribe_to_self_forbidden(self, async_client: AsyncClient):
        user_id = await self._create_user_and_get_id(async_client, "SelfSubscribe")

        subscribe_params = {"subscriber_id": user_id, "artist_id": user_id}
        resp = await async_client.post("/user/subscribe", params=subscribe_params)
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert "Cannot subscribe to self" in resp.json()["detail"]

        await self._delete_user(async_client, user_id)

    async def test_subscribe_already_exist(self, async_client: AsyncClient):
        subscriber_id = await self._create_user_and_get_id(async_client, "SubExist1")
        artist_id = await self._create_user_and_get_id(async_client, "ArtExist1")

        subscribe_params = {"subscriber_id": subscriber_id, "artist_id": artist_id}

        resp1 = await async_client.post("/user/subscribe", params=subscribe_params)
        assert resp1.status_code == status.HTTP_201_CREATED

        resp2 = await async_client.post("/user/subscribe", params=subscribe_params)
        assert resp2.status_code == status.HTTP_400_BAD_REQUEST

        await self._delete_user(async_client, subscriber_id)
        await self._delete_user(async_client, artist_id)

    async def test_subscribe_user_not_found(self, async_client: AsyncClient):
        artist_id = await self._create_user_and_get_id(async_client, "ArtistNF")
        subscribe_params = {"subscriber_id": 999999, "artist_id": artist_id}
        resp = await async_client.post("/user/subscribe", params=subscribe_params)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "User '999999' not found" in resp.json()["detail"]

        await self._delete_user(async_client, artist_id)

    async def test_subscribe_artist_not_found(self, async_client: AsyncClient):
        subscriber_id = await self._create_user_and_get_id(async_client, "SubNF")
        subscribe_params = {"subscriber_id": subscriber_id, "artist_id": 999999}
        resp = await async_client.post("/user/subscribe", params=subscribe_params)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "User '999999' not found" in resp.json()["detail"]

        await self._delete_user(async_client, subscriber_id)

    async def test_unsubscribe_success(self, async_client: AsyncClient):
        subscriber_id = await self._create_user_and_get_id(async_client, "UnsubSuc1")
        artist_id = await self._create_user_and_get_id(async_client, "UnsubSucArt1")

        subscribe_params = {"subscriber_id": subscriber_id, "artist_id": artist_id}

        resp_sub = await async_client.post("/user/subscribe", params=subscribe_params)
        assert resp_sub.status_code == status.HTTP_201_CREATED

        resp_unsub = await async_client.post(
            "/user/unsubscribe", params=subscribe_params
        )
        assert resp_unsub.status_code == status.HTTP_204_NO_CONTENT

        subscriptions_resp = await async_client.get(
            "/user/subscriptions", params={"id": subscriber_id}
        )
        assert subscriptions_resp.status_code == status.HTTP_200_OK
        subscriptions_list = subscriptions_resp.json()
        assert not any(a["id"] == artist_id for a in subscriptions_list)

        await self._delete_user(async_client, subscriber_id)
        await self._delete_user(async_client, artist_id)

    async def test_unsubscribe_not_found(self, async_client: AsyncClient):
        subscriber_id = await self._create_user_and_get_id(async_client, "UnsubNF")
        artist_id = await self._create_user_and_get_id(async_client, "UnsubNFArt")

        subscribe_params = {"subscriber_id": subscriber_id, "artist_id": artist_id}
        resp = await async_client.post("/user/unsubscribe", params=subscribe_params)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_user(async_client, subscriber_id)
        await self._delete_user(async_client, artist_id)

    async def test_get_subscriptions_success(self, async_client: AsyncClient):
        subscriber_id = await self._create_user_and_get_id(async_client, "GetSubs")
        artist1_id = await self._create_user_and_get_id(async_client, "GetSubsArt1")
        artist2_id = await self._create_user_and_get_id(async_client, "GetSubsArt2")

        await async_client.post(
            "/user/subscribe",
            params={"subscriber_id": subscriber_id, "artist_id": artist1_id},
        )
        await async_client.post(
            "/user/subscribe",
            params={"subscriber_id": subscriber_id, "artist_id": artist2_id},
        )

        resp = await async_client.get(
            "/user/subscriptions", params={"id": subscriber_id}
        )
        assert resp.status_code == status.HTTP_200_OK
        subscriptions = resp.json()
        assert len(subscriptions) >= 2
        assert any(s["id"] == artist1_id for s in subscriptions)
        assert any(s["id"] == artist2_id for s in subscriptions)

        await self._delete_user(async_client, subscriber_id)
        await self._delete_user(async_client, artist1_id)
        await self._delete_user(async_client, artist2_id)

    async def test_get_subscriptions_user_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/user/subscriptions", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_subscribers_success(self, async_client: AsyncClient):
        artist_id = await self._create_user_and_get_id(async_client, "GetSubscribers")
        subscriber1_id = await self._create_user_and_get_id(
            async_client, "GetSubscribers1"
        )
        subscriber2_id = await self._create_user_and_get_id(
            async_client, "GetSubscribers2"
        )

        await async_client.post(
            "/user/subscribe",
            params={"subscriber_id": subscriber1_id, "artist_id": artist_id},
        )
        await async_client.post(
            "/user/subscribe",
            params={"subscriber_id": subscriber2_id, "artist_id": artist_id},
        )

        resp = await async_client.get("/user/subscribers", params={"id": artist_id})
        assert resp.status_code == status.HTTP_200_OK
        subscribers = resp.json()
        assert len(subscribers) >= 2
        assert any(s["id"] == subscriber1_id for s in subscribers)
        assert any(s["id"] == subscriber2_id for s in subscribers)

        await self._delete_user(async_client, artist_id)
        await self._delete_user(async_client, subscriber1_id)
        await self._delete_user(async_client, subscriber2_id)

    async def test_get_subscribers_user_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/user/subscribers", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_subscriber_count_success(self, async_client: AsyncClient):
        artist_id = await self._create_user_and_get_id(async_client, "CountArtist")
        subscriber1_id = await self._create_user_and_get_id(async_client, "CountSub1")
        subscriber2_id = await self._create_user_and_get_id(async_client, "CountSub2")

        await async_client.post(
            "/user/subscribe",
            params={"subscriber_id": subscriber1_id, "artist_id": artist_id},
        )
        await async_client.post(
            "/user/subscribe",
            params={"subscriber_id": subscriber2_id, "artist_id": artist_id},
        )

        resp = await async_client.get(
            "/user/subscriber-count", params={"id": artist_id}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["count"] == 2

        await self._delete_user(async_client, artist_id)
        await self._delete_user(async_client, subscriber1_id)
        await self._delete_user(async_client, subscriber2_id)

    async def test_get_subscriber_count_user_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/user/subscriber-count", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND
