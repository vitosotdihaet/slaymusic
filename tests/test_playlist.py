import pytest
from fastapi import status
from httpx import AsyncClient
import uuid
from datetime import date


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
        response = await client.post("/user/register/", params=register_data)
        if response.status_code != status.HTTP_201_CREATED:
            response = await client.post(
                "/user/login/",
                params={"username": username, "password": "testpass"},
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
            params=user_data,
            files={"cover_file": ("", "", "")},
        )
        assert resp_reg.status_code == status.HTTP_201_CREATED, (
            f"Failed to register user: {resp_reg.text}"
        )

        headers = {"Authorization": f"Bearer {resp_reg.json()['token']}"}

        resp_get_user = await async_client.get("/user/", headers=headers)
        assert resp_get_user.status_code == status.HTTP_200_OK
        user_id = resp_get_user.json()["id"]

        return user_id, headers

    async def _create_playlist(
        self,
        client: AsyncClient,
        author_id: int,
        headers: dict,
        playlist_name_prefix: str,
        has_image: bool = False,
    ) -> int:
        unique_suffix = f"{playlist_name_prefix.lower()}_{uuid.uuid4().hex[:8]}"
        playlist_data = {
            "author_id": author_id,
            "name": f"Playlist {unique_suffix}",
        }
        files = {}
        if has_image:
            files = {
                "image_file": (
                    "playlist_cover.png",
                    b"fakeplaylistimagedata",
                    "image/png",
                )
            }
        else:
            files = {"image_file": ("", "", "")}

        resp = await client.post(
            "/playlist/",
            params=playlist_data,
            files=files,
            headers=headers,
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create playlist during setup: {resp.text}"
        )
        return resp.json()["id"]

    async def _delete_playlist(
        self, client: AsyncClient, playlist_id: int, headers: dict
    ):
        resp = await client.delete(
            "/playlist/", params={"id": playlist_id}, headers=headers
        )
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ], f"Failed to delete playlist {playlist_id}: {resp.status_code} - {resp.text}"

    async def _create_single(
        self,
        client: AsyncClient,
        artist_id: int,
        headers: dict,
        track_name_prefix: str,
        has_cover: bool = False,
    ) -> int:
        unique_suffix = f"{track_name_prefix.lower()}_{uuid.uuid4().hex[:8]}"
        track_data = {
            "name": f"Single {unique_suffix}",
            "artist_id": artist_id,
            "release_date": date.today().isoformat(),
        }
        files = {
            "track_file": ("single.mp3", b"fakesingledata", "audio/mpeg"),
        }
        if has_cover:
            files["cover_file"] = (
                "single_cover.png",
                b"fakesinglecoverdata",
                "image/png",
            )
        else:
            files["cover_file"] = ("", "", "")

        resp = await client.post(
            "/track/single/",
            params=track_data,
            files=files,
            headers=headers,
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create single during setup: {resp.text}"
        )
        return resp.json()["id"]

    async def _delete_track(self, client: AsyncClient, track_id: int, headers: dict):
        resp = await client.delete("/track/", params={"id": track_id}, headers=headers)
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ], f"Failed to delete track {track_id}: {resp.status_code} - {resp.text}"

    async def _add_track_to_playlist(
        self, client: AsyncClient, playlist_id: int, track_id: int, headers: dict
    ):
        track_data = {"playlist_id": playlist_id, "track_id": track_id}
        resp = await client.post("/playlist/track/", params=track_data, headers=headers)
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to add track to playlist: {resp.text}"
        )

    async def test_create_playlist_success(self, async_client: AsyncClient):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "PlaylistAuthor"
        )
        playlist_name_prefix = "MyNewPlaylist"

        playlist_data = {
            "author_id": author_id,
            "name": f"Playlist {playlist_name_prefix}_{uuid.uuid4().hex[:8]}",
        }
        resp = await async_client.post(
            "/playlist/",
            params=playlist_data,
            files={"image_file": ("", "", "")},
            headers=headers,
        )
        assert resp.status_code == status.HTTP_201_CREATED
        new_playlist = resp.json()
        assert new_playlist["name"].startswith("Playlist MyNewPlaylist")
        assert new_playlist["author_id"] == author_id

        await self._delete_playlist(async_client, new_playlist["id"], headers)
        await self._delete_user(async_client, headers)

    async def test_create_playlist_with_image_success(self, async_client: AsyncClient):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "PlaylistAuthorImg"
        )
        playlist_name_prefix = "PlaylistWithImage"

        playlist_data = {
            "author_id": author_id,
            "name": f"Playlist {playlist_name_prefix}_{uuid.uuid4().hex[:8]}",
        }
        files = {"image_file": ("cover.png", b"testplaylistimagedata", "image/png")}
        resp = await async_client.post(
            "/playlist/",
            params=playlist_data,
            files=files,
            headers=headers,
        )
        assert resp.status_code == status.HTTP_201_CREATED
        new_playlist_id = resp.json()["id"]

        img_resp = await async_client.get(
            "/playlist/image/", params={"id": new_playlist_id}
        )
        assert img_resp.status_code == status.HTTP_200_OK
        assert img_resp.headers["content-type"] == "image/png"
        assert img_resp.content == b"testplaylistimagedata"

        await self._delete_playlist(async_client, new_playlist_id, headers)
        await self._delete_user(async_client, headers)

    async def test_get_playlist_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/playlist/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_playlists_by_author_success(self, async_client: AsyncClient):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "GetPlaylistsByAuthor"
        )
        playlist1_id = await self._create_playlist(
            async_client, author_id, headers, "AuthPlaylist1"
        )
        playlist2_id = await self._create_playlist(
            async_client, author_id, headers, "AuthPlaylist2"
        )

        resp = await async_client.get(
            "/playlists/", params={"author_id": author_id}, headers=headers
        )
        assert resp.status_code == status.HTTP_200_OK
        playlists = resp.json()
        assert len(playlists) >= 2
        assert any(p["id"] == playlist1_id for p in playlists)
        assert any(p["id"] == playlist2_id for p in playlists)

        await self._delete_playlist(async_client, playlist1_id, headers)
        await self._delete_playlist(async_client, playlist2_id, headers)
        await self._delete_user(async_client, headers)

    async def test_get_playlists_filtered_by_name(self, async_client: AsyncClient):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "FilterPlaylistAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, headers, "UniqueFilterName"
        )
        await self._create_playlist(async_client, author_id, headers, "AnotherPlaylist")

        resp = await async_client.get(
            "/playlists/",
            params={
                "name": f"Playlist UniqueFilterName_{playlist_id}"[
                    : -len(str(playlist_id))
                ],
                "author_id": author_id,
            },
            headers=headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        playlists = resp.json()
        assert len(playlists) >= 1
        assert any(p["id"] == playlist_id for p in playlists)

        await self._delete_playlist(async_client, playlist_id, headers)
        await self._delete_user(async_client, headers)

    async def test_update_playlist_metadata_success(self, async_client: AsyncClient):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "UpdatePlaylistAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, headers, "OldPlaylistName"
        )

        update_params = {
            "id": playlist_id,
            "name": "Updated Playlist Name",
            "author_id": author_id,
        }
        resp = await async_client.put(
            "/playlist/", params=update_params, headers=headers
        )
        assert resp.status_code == status.HTTP_200_OK
        updated_playlist = resp.json()
        assert updated_playlist["id"] == playlist_id
        assert updated_playlist["name"] == "Updated Playlist Name"

        await self._delete_playlist(async_client, playlist_id, headers)
        await self._delete_user(async_client, headers)

    async def test_delete_playlist_success(self, async_client: AsyncClient):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "DeletePlaylistAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, headers, "ToDelete"
        )

        resp = await async_client.delete(
            "/playlist/", params={"id": playlist_id}, headers=headers
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        check_resp = await async_client.get("/playlist/", params={"id": playlist_id})
        assert check_resp.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_user(async_client, headers)

    async def test_add_track_to_playlist_success(self, async_client: AsyncClient):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "TrackAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, headers, "TrackPlaylist"
        )
        track_id = await self._create_single(async_client, author_id, headers, "cho")

        track_data = {"playlist_id": playlist_id, "track_id": track_id}
        resp = await async_client.post(
            "/playlist/track/", params=track_data, headers=headers
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["playlist_id"] == playlist_id
        assert resp.json()["track_id"] == track_id

        await self._delete_playlist(async_client, playlist_id, headers)
        await self._delete_track(async_client, track_id, headers)
        await self._delete_user(async_client, headers)

    async def test_add_track_to_playlist_playlist_not_found(
        self, async_client: AsyncClient
    ):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "TrackAuthorNotFound"
        )
        track_id = await self._create_single(async_client, author_id, headers, "cho")
        track_data = {"playlist_id": 999999, "track_id": track_id}
        resp = await async_client.post(
            "/playlist/track/", params=track_data, headers=headers
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "Playlist '999999' not found" in resp.json()["detail"]

        await self._delete_track(async_client, track_id, headers)
        await self._delete_user(async_client, headers)

    async def test_add_track_to_playlist_already_exist(self, async_client: AsyncClient):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "TrackAuthorExist"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, headers, "TrackPlaylistExist"
        )
        track_id = await self._create_single(async_client, author_id, headers, "cho")

        track_data = {"playlist_id": playlist_id, "track_id": track_id}
        resp1 = await async_client.post(
            "/playlist/track/", params=track_data, headers=headers
        )
        assert resp1.status_code == status.HTTP_201_CREATED

        resp2 = await async_client.post(
            "/playlist/track/", params=track_data, headers=headers
        )
        assert resp2.status_code == status.HTTP_400_BAD_REQUEST

        await self._delete_playlist(async_client, playlist_id, headers)
        await self._delete_track(async_client, track_id, headers)
        await self._delete_user(async_client, headers)

    async def test_get_tracks_by_playlist_success(self, async_client: AsyncClient):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "TracksGetSuccessUser"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, headers, "TracksGetSuccessPlaylist"
        )
        track1_id = await self._create_single(
            async_client, author_id, headers, "Track1ForGet"
        )
        track2_id = await self._create_single(
            async_client, author_id, headers, "Track2ForGet"
        )

        await self._add_track_to_playlist(async_client, playlist_id, track1_id, headers)
        await self._add_track_to_playlist(async_client, playlist_id, track2_id, headers)

        resp = await async_client.get(
            "playlist/tracks/", params={"id": playlist_id}, headers=headers
        )

        assert resp.status_code == status.HTTP_200_OK
        tracks = resp.json()
        assert len(tracks) == 2
        track_ids = {t["id"] for t in tracks}
        assert track1_id in track_ids
        assert track2_id in track_ids

        await self._delete_playlist(async_client, playlist_id, headers)
        await self._delete_track(async_client, track1_id, headers)
        await self._delete_track(async_client, track2_id, headers)
        await self._delete_user(async_client, headers)

    async def test_get_tracks_by_playlist_with_pagination(
        self, async_client: AsyncClient
    ):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "TracksGetPaginationUser"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, headers, "TracksGetPaginationPlaylist"
        )

        track_ids = []
        for i in range(5):
            track_id = await self._create_single(
                async_client, author_id, headers, f"Track{i + 1}ForPagination"
            )
            await self._add_track_to_playlist(
                async_client, playlist_id, track_id, headers
            )
            track_ids.append(track_id)

        resp_page1 = await async_client.get(
            "playlist/tracks/",
            params={"id": playlist_id, "limit": 2, "skip": 0},
            headers=headers,
        )
        assert resp_page1.status_code == status.HTTP_200_OK
        tracks_page1 = resp_page1.json()
        assert len(tracks_page1) == 2
        assert {t["id"] for t in tracks_page1} == {track_ids[0], track_ids[1]}

        resp_page2 = await async_client.get(
            "playlist/tracks/",
            params={"id": playlist_id, "limit": 2, "skip": 1},
            headers=headers,
        )
        assert resp_page2.status_code == status.HTTP_200_OK
        tracks_page2 = resp_page2.json()
        assert len(tracks_page2) == 2
        assert {t["id"] for t in tracks_page2} == {track_ids[1], track_ids[2]}

        await self._delete_playlist(async_client, playlist_id, headers)
        for track_id in track_ids:
            await self._delete_track(async_client, track_id, headers)
        await self._delete_user(async_client, headers)

    async def test_get_tracks_by_playlist_empty_playlist(
        self, async_client: AsyncClient
    ):
        author_id, headers = await self._create_user_and_get_auth_headers(
            async_client, "EmptyPlaylistUser"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, headers, "EmptyPlaylist"
        )

        resp = await async_client.get(
            "playlist/tracks/", params={"id": playlist_id}, headers=headers
        )
        assert resp.status_code == status.HTTP_200_OK
        tracks = resp.json()
        assert len(tracks) == 0

        await self._delete_playlist(async_client, playlist_id, headers)
        await self._delete_user(async_client, headers)
