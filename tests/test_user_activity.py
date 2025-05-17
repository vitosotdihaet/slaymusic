import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserActivityEndpoints:
    async def test_add_user_activity(self, async_client: AsyncClient):
        t = {"user_id": 1337, "track_id": 69, "event": "play"}
        response = await async_client.post("/user_activity/", params=t)
        assert response.status_code == status.HTTP_201_CREATED

        t["event"] = "keknul"
        response = await async_client.post("/user_activity/", params=t)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = await async_client.post("/user_activity/")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        await async_client.post(
            "/user_activity/delete", json={"user_ids": [t["user_id"]]}
        )

    async def test_get_user_activity(self, async_client: AsyncClient):
        t = {"user_id": 228, "track_id": 420, "event": "skip"}
        create_response = await async_client.post("/user_activity/", params=t)
        id = create_response.json().get("id")

        response = await async_client.get(f"/user_activity/{id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == id
        assert t == {
            "user_id": data["user_id"],
            "track_id": data["track_id"],
            "event": data["event"],
        }

        response = await async_client.get("/user_activity/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        await async_client.post(
            "/user_activity/delete", json={"user_ids": [t["user_id"]]}
        )

    async def test_list_user_activities(self, async_client: AsyncClient):
        await async_client.post(
            "/user_activity/", params={"user_id": 1, "track_id": 101, "event": "play"}
        )
        await async_client.post(
            "/user_activity/", params={"user_id": 2, "track_id": 102, "event": "skip"}
        )

        response = await async_client.post("/user_activity/list")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2

        # Test filtering by user_ids
        response = await async_client.post(
            "/user_activity/list", json={"user_ids": [1]}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(activity["user_id"] == 1 for activity in data)

        # Test filtering by track_ids
        response = await async_client.post(
            "/user_activity/list", json={"track_ids": [102]}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(activity["track_id"] == 102 for activity in data)

        # Test pagination
        response = await async_client.post("/user_activity/list", params={"limit": 1})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1

        # Test combined filters
        response = await async_client.post(
            "/user_activity/list",
            params={"track_ids": [101], "limit": 1},
            json={"user_ids": [1, 2]},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] in [1, 2]
        assert data[0]["track_id"] == 101

        await async_client.post("/user_activity/delete", json={"user_ids": [1, 2]})

    async def test_delete_user_activity(self, async_client: AsyncClient):
        create_response = await async_client.post(
            "/user_activity/",
            params={
                "user_id": 52,
                "track_id": 42,
                "event": "skip",
            },
        )
        activity_id = create_response.json().get("id")

        response = await async_client.post(
            "/user_activity/delete", json={"ids": [activity_id]}
        )
        assert response.status_code == status.HTTP_200_OK

        response = await async_client.get(f"/user_activity/{activity_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = await async_client.post(
            "/user_activity/delete", json={"ids": [9999999]}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
