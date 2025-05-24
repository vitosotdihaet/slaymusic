import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTrackQueueEndpoints:
    async def get_auth_headers(self, client: AsyncClient):
        register_data = {
            "name": "testicle",
            "username": "testuser",
            "password": "testpass",
        }
        response = await client.post("/accounts/register", json=register_data)
        if response.status_code != status.HTTP_201_CREATED:
            response = await client.post(
                "/accounts/login",
                json={"username": "testuser", "password": "testpass"},
            )

        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    async def test_queue_lifecycle(self, async_client: AsyncClient):
        headers = await self.get_auth_headers(async_client)
        test_track_ids = [101, 102, 103, 104]

        list_response = await async_client.get("/track_queue/", headers=headers)
        if list_response.status_code == status.HTTP_200_OK:
            await async_client.delete("/track_queue/", headers=headers)

        await async_client.post(
            "/track_queue/right", params={"id": test_track_ids[0]}, headers=headers
        )
        await async_client.post(
            "/track_queue/right", params={"id": test_track_ids[1]}, headers=headers
        )
        await async_client.post(
            "/track_queue/left", params={"id": test_track_ids[2]}, headers=headers
        )

        list_response = await async_client.get("/track_queue/", headers=headers)
        assert list_response.status_code == status.HTTP_200_OK
        assert list_response.json()["track_ids"] == [
            test_track_ids[2],
            test_track_ids[0],
            test_track_ids[1],
        ]

        insert_response = await async_client.patch(
            "/track_queue/insert",
            params={"track_id": test_track_ids[3], "queue_id": 1},
            headers=headers,
        )
        assert insert_response.status_code == status.HTTP_200_OK

        list_response = await async_client.get("/track_queue/", headers=headers)
        assert list_response.json()["track_ids"] == [103, 104, 101, 102]

        move_response = await async_client.patch(
            "/track_queue/move",
            params={"src_id": 0, "dest_id": 3},
            headers=headers,
        )
        assert move_response.status_code == status.HTTP_200_OK

        list_response = await async_client.get("/track_queue/", headers=headers)
        assert list_response.json()["track_ids"] == [104, 101, 102, 103]

        move_response = await async_client.patch(
            "/track_queue/move",
            params={"src_id": 2, "dest_id": 100},
            headers=headers,
        )
        assert move_response.status_code == status.HTTP_200_OK

        list_response = await async_client.get("/track_queue/", headers=headers)
        assert list_response.json()["track_ids"] == [104, 101, 103, 102]

        move_response = await async_client.patch(
            "/track_queue/move",
            params={"src_id": 3, "dest_id": 0},
            headers=headers,
        )
        assert move_response.status_code == status.HTTP_200_OK

        list_response = await async_client.get("/track_queue/", headers=headers)
        assert list_response.json()["track_ids"] == [102, 104, 101, 103]

        move_response = await async_client.patch(
            "/track_queue/move",
            params={"src_id": 100, "dest_id": 50},
            headers=headers,
        )
        assert move_response.status_code == status.HTTP_200_OK

        list_response = await async_client.get("/track_queue/", headers=headers)
        assert list_response.json()["track_ids"] == [102, 104, 101, 103]

        remove_response = await async_client.patch(
            "/track_queue/remove", params={"id": 1}, headers=headers
        )
        assert remove_response.status_code == status.HTTP_200_OK

        list_response = await async_client.get("/track_queue/", headers=headers)
        assert list_response.json()["track_ids"] == [102, 101, 103]

        delete_response = await async_client.delete("/track_queue/", headers=headers)
        assert delete_response.status_code == status.HTTP_200_OK

        list_response = await async_client.get("/track_queue/", headers=headers)
        assert list_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_queue_operations_errors(self, async_client: AsyncClient):
        headers = await self.get_auth_headers(async_client)

        response = await async_client.post(
            "/track_queue/right", params={"id": -1}, headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = await async_client.patch(
            "/track_queue/insert",
            params={"track_id": 1, "queue_id": 999},
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = await async_client.patch(
            "/track_queue/move",
            params={"src_id": 999, "dest_id": 0},
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/track_queue/", headers=headers)
        response = await async_client.patch(
            "/track_queue/remove", params={"id": 0}, headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_queue_pagination(self, async_client: AsyncClient):
        headers = await self.get_auth_headers(async_client)

        track_ids = list(range(1, 21))
        for track_id in track_ids:
            await async_client.post(
                "/track_queue/right", params={"id": track_id}, headers=headers
            )

        response = await async_client.get(
            "/track_queue/", params={"limit": 5}, headers=headers
        )
        data = response.json()
        assert len(data["track_ids"]) == 5
        assert data["track_ids"] == track_ids[:5]

        response = await async_client.get(
            "/track_queue/", params={"offset": 10, "limit": 5}, headers=headers
        )
        data = response.json()
        assert len(data["track_ids"]) == 5
        assert data["track_ids"] == track_ids[10:15]

        response = await async_client.get(
            "/track_queue/", params={"offset": 100, "limit": 10}, headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        await async_client.delete("/track_queue/", headers=headers)
