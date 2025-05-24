import pytest
from fastapi import status
from httpx import AsyncClient
import uuid
from datetime import date


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

    async def _create_playlist(
        self,
        client: AsyncClient,
        author_id: int,
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
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create playlist during setup: {resp.text}"
        )
        return resp.json()["id"]

    async def _delete_playlist(self, client: AsyncClient, playlist_id: int):
        resp = await client.delete("/playlist/", params={"id": playlist_id})
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        ], f"Failed to delete playlist {playlist_id}: {resp.status_code} - {resp.text}"

    async def _create_single(
        self,
        client: AsyncClient,
        artist_id: int,
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
        )
        assert resp.status_code == status.HTTP_201_CREATED, (
            f"Failed to create single during setup: {resp.text}"
        )
        return resp.json()["id"]

    async def _delete_track(self, client: AsyncClient, track_id: int):
        await client.delete("/track/", params={"id": track_id})

    async def test_create_playlist_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(async_client, "PlaylistAuthor")
        playlist_name_prefix = "MyNewPlaylist"

        playlist_data = {
            "author_id": author_id,
            "name": f"Playlist {playlist_name_prefix}_{uuid.uuid4().hex[:8]}",
        }
        resp = await async_client.post(
            "/playlist/",
            params=playlist_data,
            files={"image_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        new_playlist = resp.json()
        assert new_playlist["name"].startswith("Playlist MyNewPlaylist")
        assert new_playlist["author_id"] == author_id

        await self._delete_playlist(async_client, new_playlist["id"])
        await self._delete_user(async_client, author_id)

    async def test_create_playlist_with_image_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
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
        )
        assert resp.status_code == status.HTTP_201_CREATED
        new_playlist_id = resp.json()["id"]

        img_resp = await async_client.get(
            "/playlist/image/", params={"id": new_playlist_id}
        )
        assert img_resp.status_code == status.HTTP_200_OK
        assert img_resp.headers["content-type"] == "image/png"
        assert img_resp.content == b"testplaylistimagedata"

        await self._delete_playlist(async_client, new_playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_create_playlist_user_not_found(self, async_client: AsyncClient):
        playlist_data = {
            "author_id": 999999,
            "name": "PlaylistForNonExistentUser",
        }
        resp = await async_client.post(
            "/playlist/",
            params=playlist_data,
            files={"image_file": ("", "", "")},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "User '999999' not found" in resp.json()["detail"]

    async def test_get_playlist_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "GetPlaylistAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, "GetSinglePlaylist"
        )

        resp = await async_client.get("/playlist/", params={"id": playlist_id})
        assert resp.status_code == status.HTTP_200_OK
        retrieved_playlist = resp.json()
        assert retrieved_playlist["id"] == playlist_id
        assert retrieved_playlist["author_id"] == author_id

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_get_playlist_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/playlist/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_playlists_by_author_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "GetPlaylistsByAuthor"
        )
        playlist1_id = await self._create_playlist(
            async_client, author_id, "AuthPlaylist1"
        )
        playlist2_id = await self._create_playlist(
            async_client, author_id, "AuthPlaylist2"
        )

        resp = await async_client.get("/playlists/", params={"author_id": author_id})
        assert resp.status_code == status.HTTP_200_OK
        playlists = resp.json()
        assert len(playlists) >= 2
        assert any(p["id"] == playlist1_id for p in playlists)
        assert any(p["id"] == playlist2_id for p in playlists)

        await self._delete_playlist(async_client, playlist1_id)
        await self._delete_playlist(async_client, playlist2_id)
        await self._delete_user(async_client, author_id)

    async def test_get_playlists_by_author_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/playlists/", params={"author_id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_playlists_filtered_by_name(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "FilterPlaylistAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, "UniqueFilterName"
        )
        await self._create_playlist(async_client, author_id, "AnotherPlaylist")

        resp = await async_client.get(
            "/playlists/",
            params={
                "name": f"Playlist UniqueFilterName_{playlist_id}"[
                    : -len(str(playlist_id))
                ],
                "author_id": author_id,
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        playlists = resp.json()
        assert len(playlists) >= 1
        assert any(p["id"] == playlist_id for p in playlists)

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_get_playlist_image_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "PlaylistImgAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, "PlaylistCover", has_image=True
        )

        resp = await async_client.get("/playlist/image/", params={"id": playlist_id})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.headers["content-type"] == "image/png"
        assert resp.content == b"fakeplaylistimagedata"

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_get_playlist_image_not_found(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "PlaylistNoImgAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, "PlaylistNoCover", has_image=False
        )

        resp = await async_client.get("/playlist/image/", params={"id": playlist_id})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_get_playlist_image_playlist_not_found(
        self, async_client: AsyncClient
    ):
        resp = await async_client.get("/playlist/image/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_playlist_metadata_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "UpdatePlaylistAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, "OldPlaylistName"
        )

        update_params = {
            "id": playlist_id,
            "name": "Updated Playlist Name",
            "author_id": author_id,
        }
        resp = await async_client.put("/playlist/", params=update_params)
        assert resp.status_code == status.HTTP_200_OK
        updated_playlist = resp.json()
        assert updated_playlist["id"] == playlist_id
        assert updated_playlist["name"] == "Updated Playlist Name"

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_update_playlist_metadata_playlist_not_found(
        self, async_client: AsyncClient
    ):
        author_id = await self._create_user_and_get_id(
            async_client, "UpdatePlaylistAuthorNF"
        )
        update_params = {
            "id": 999999,
            "name": "NonExistentPlaylist",
            "author_id": author_id,
        }
        resp = await async_client.put("/playlist/", params=update_params)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_user(async_client, author_id)

    async def test_update_playlist_image_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "UpdatePlaylistImgAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, "OldPlaylistImg", has_image=True
        )

        new_files = {
            "image_file": ("new_cover.jpg", b"newplaylistimagedata", "image/png")
        }
        resp = await async_client.put(
            "/playlist/image/", params={"id": playlist_id}, files=new_files
        )
        assert resp.status_code == status.HTTP_200_OK

        img_resp = await async_client.get(
            "/playlist/image/", params={"id": playlist_id}
        )
        assert img_resp.status_code == status.HTTP_200_OK
        assert img_resp.headers["content-type"] == "image/png"
        assert img_resp.content == b"newplaylistimagedata"

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_update_playlist_image_playlist_not_found(
        self, async_client: AsyncClient
    ):
        new_files = {"image_file": ("any.jpg", b"anydata", "image/png")}
        resp = await async_client.put(
            "/playlist/image/", params={"id": 999999}, files=new_files
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_playlist_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "DeletePlaylistAuthor"
        )
        playlist_id = await self._create_playlist(async_client, author_id, "ToDelete")

        resp = await async_client.delete("/playlist/", params={"id": playlist_id})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        check_resp = await async_client.get("/playlist/", params={"id": playlist_id})
        assert check_resp.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_user(async_client, author_id)

    async def test_delete_playlist_not_found(self, async_client: AsyncClient):
        resp = await async_client.delete("/playlist/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_playlist_image_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "DelPlaylistImgAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, "PlaylistWithImageToDelete", has_image=True
        )

        img_resp_before = await async_client.get(
            "/playlist/image/", params={"id": playlist_id}
        )
        assert img_resp_before.status_code == status.HTTP_200_OK

        resp_del_img = await async_client.delete(
            "/playlist/image/", params={"id": playlist_id}
        )
        assert resp_del_img.status_code == status.HTTP_204_NO_CONTENT

        img_resp_after = await async_client.get(
            "/playlist/image/", params={"id": playlist_id}
        )
        assert img_resp_after.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_delete_playlist_image_not_found(self, async_client: AsyncClient):
        resp = await async_client.delete("/playlist/image/", params={"id": 999999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_track_to_playlist_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(async_client, "TrackAuthor")
        playlist_id = await self._create_playlist(
            async_client, author_id, "TrackPlaylist"
        )
        track_id = await self._create_single(async_client, author_id, "cho")

        track_data = {"playlist_id": playlist_id, "track_id": track_id}
        resp = await async_client.post("/playlist/track/", params=track_data)
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["playlist_id"] == playlist_id
        assert resp.json()["track_id"] == track_id

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_add_track_to_playlist_playlist_not_found(
        self, async_client: AsyncClient
    ):
        author_id = await self._create_user_and_get_id(async_client, "TrackAuthor")
        track_id = await self._create_single(async_client, author_id, "cho")
        track_data = {"playlist_id": 999999, "track_id": track_id}
        resp = await async_client.post("/playlist/track/", params=track_data)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "Playlist '999999' not found" in resp.json()["detail"]

        await self._delete_user(async_client, author_id)

    async def test_add_track_to_playlist_track_not_found(
        self, async_client: AsyncClient
    ):
        author_id = await self._create_user_and_get_id(async_client, "TrackAuthorNF")
        playlist_id = await self._create_playlist(
            async_client, author_id, "TrackPlaylistNF"
        )

        track_data = {"playlist_id": playlist_id, "track_id": 999999}
        resp = await async_client.post("/playlist/track/", params=track_data)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "Track '999999' not found" in resp.json()["detail"]

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_add_track_to_playlist_already_exist(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(async_client, "TrackAuthorExist")
        playlist_id = await self._create_playlist(
            async_client, author_id, "TrackPlaylistExist"
        )
        track_id = await self._create_single(async_client, author_id, "cho")

        track_data = {"playlist_id": playlist_id, "track_id": track_id}
        resp1 = await async_client.post("/playlist/track/", params=track_data)
        assert resp1.status_code == status.HTTP_201_CREATED

        resp2 = await async_client.post("/playlist/track/", params=track_data)
        assert resp2.status_code == status.HTTP_400_BAD_REQUEST

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_remove_track_from_playlist_success(self, async_client: AsyncClient):
        author_id = await self._create_user_and_get_id(
            async_client, "RemoveTrackAuthor"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, "RemoveTrackPlaylist"
        )
        track_id = await self._create_single(async_client, author_id, "cho")

        track_data = {"playlist_id": playlist_id, "track_id": track_id}
        resp_add = await async_client.post("/playlist/track/", params=track_data)
        assert resp_add.status_code == status.HTTP_201_CREATED

        resp_remove = await async_client.delete("/playlist/track/", params=track_data)
        assert resp_remove.status_code == status.HTTP_204_NO_CONTENT

        resp_remove_again = await async_client.delete(
            "/playlist/track/", params=track_data
        )
        assert resp_remove_again.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_remove_track_from_playlist_not_found(
        self, async_client: AsyncClient
    ):
        author_id = await self._create_user_and_get_id(
            async_client, "RemoveTrackAuthorNF"
        )
        playlist_id = await self._create_playlist(
            async_client, author_id, "RemoveTrackPlaylistNF"
        )
        fake_track_id = await self._create_single(async_client, author_id, "sho")

        track_data = {"playlist_id": playlist_id, "track_id": fake_track_id}
        resp = await async_client.delete("/playlist/track/", params=track_data)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        await self._delete_playlist(async_client, playlist_id)
        await self._delete_user(async_client, author_id)

    async def test_remove_track_from_playlist_playlist_not_found(
        self, async_client: AsyncClient
    ):
        author_id = await self._create_user_and_get_id(async_client, "TrackAuthor")
        fake_track_id = await self._create_single(async_client, author_id, "cho")
        track_data = {"playlist_id": 999999, "track_id": fake_track_id}
        resp = await async_client.delete("/playlist/track/", params=track_data)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "Playlist '999999' not found" in resp.json()["detail"]

        await self._delete_user(async_client, author_id)
