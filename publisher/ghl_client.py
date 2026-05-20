"""GHL REST client for the Social Planner workflow.

Talks to https://services.leadconnectorhq.com using a Private Integration Token.
Bypasses the broken read endpoints of ghl-mcp-server entirely.
"""
from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import requests


GHL_API_BASE = "https://services.leadconnectorhq.com"
GHL_API_VERSION = "2021-07-28"


class GHLError(RuntimeError):
    """Wraps non-2xx responses with the API's own error body."""

    def __init__(self, status: int, body: Any, url: str):
        self.status = status
        self.body = body
        self.url = url
        super().__init__(f"GHL {status} on {url}: {body}")


@dataclass
class SocialAccount:
    id: str
    platform: str
    name: str
    is_expired: bool
    type: str
    profile_id: Optional[str] = None

    @classmethod
    def from_api(cls, d: dict) -> "SocialAccount":
        return cls(
            id=d["id"],
            platform=d.get("platform", ""),
            name=d.get("name", ""),
            is_expired=bool(d.get("isExpired", False)),
            type=d.get("type", ""),
            profile_id=d.get("profileId"),
        )


@dataclass
class MediaUpload:
    file_id: str
    url: str


class GHLClient:
    """Minimal client for Social Planner + Media Library operations."""

    def __init__(
        self,
        token: str,
        location_id: str,
        user_id: Optional[str] = None,
        base_url: str = GHL_API_BASE,
        api_version: str = GHL_API_VERSION,
        timeout: int = 30,
    ):
        if not token:
            raise ValueError("token is required (Private Integration Token)")
        if not location_id:
            raise ValueError("location_id is required")
        self.token = token
        self.location_id = location_id
        self.user_id = user_id
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.timeout = timeout
        self._session = requests.Session()

    # ---- low-level helpers -------------------------------------------------

    def _headers(self, *, json_body: bool = False) -> dict:
        h = {
            "Authorization": f"Bearer {self.token}",
            "Version": self.api_version,
            "Accept": "application/json",
        }
        if json_body:
            h["Content-Type"] = "application/json"
        return h

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        resp = self._session.request(method, url, timeout=self.timeout, **kwargs)
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise GHLError(resp.status_code, body, url)
        if not resp.content:
            return None
        ctype = resp.headers.get("content-type", "")
        return resp.json() if "json" in ctype else resp.text

    # ---- discovery (for `setup`) ------------------------------------------

    def get_location(self) -> dict:
        return self._request(
            "GET",
            f"/locations/{self.location_id}",
            headers=self._headers(),
        )

    def list_users(self) -> list[dict]:
        """List users with access to this location. Used in setup to pick author."""
        data = self._request(
            "GET",
            f"/users/",
            headers=self._headers(),
            params={"locationId": self.location_id},
        )
        if isinstance(data, dict):
            return data.get("users", [])
        return data or []

    # ---- social accounts --------------------------------------------------

    def list_accounts(self) -> list[SocialAccount]:
        """List all social accounts connected to this location."""
        data = self._request(
            "GET",
            f"/social-media-posting/{self.location_id}/accounts",
            headers=self._headers(),
            params={"fetchAll": "true"},
        )
        results = (data or {}).get("results", {})
        return [SocialAccount.from_api(a) for a in results.get("accounts", [])]

    # ---- media upload (direct, no third-party host) -----------------------

    def upload_media(self, file_path: str | Path, name: Optional[str] = None) -> MediaUpload:
        """Upload a local file to the GHL media library. Returns CDN URL + fileId."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(p)
        mime, _ = mimetypes.guess_type(p.name)
        mime = mime or "application/octet-stream"
        with p.open("rb") as fh:
            files = {"file": (name or p.name, fh, mime)}
            data = {"locationId": self.location_id, "name": name or p.name}
            resp = self._session.post(
                f"{self.base_url}/medias/upload-file",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Version": self.api_version,
                    "Accept": "application/json",
                },
                files=files,
                data=data,
                timeout=self.timeout * 3,
            )
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise GHLError(resp.status_code, body, resp.url)
        body = resp.json()
        return MediaUpload(
            file_id=body.get("fileId") or body.get("id") or "",
            url=body.get("url") or body.get("link") or "",
        )

    # ---- posts ------------------------------------------------------------

    def create_post(
        self,
        *,
        account_ids: list[str],
        caption: str,
        media: list[dict],
        schedule_iso: str,
        post_type: str = "post",
        status: str = "scheduled",
        follow_up_comment: Optional[str] = None,
        tags: Optional[list[str]] = None,
        category_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> dict:
        """Create a social post. `media` is a list of {url, type, caption?} dicts."""
        author = user_id or self.user_id
        if not author:
            raise ValueError("user_id required (pass via constructor or as argument)")
        if not account_ids:
            raise ValueError("at least one account_id required")
        body = {
            "accountIds": account_ids,
            "summary": caption,
            "media": media,
            "scheduleDate": schedule_iso,
            "status": status,
            "type": post_type,
            "userId": author,
        }
        if follow_up_comment:
            body["followUpComment"] = follow_up_comment
        if tags:
            body["tags"] = tags
        if category_id:
            body["categoryId"] = category_id
        return self._request(
            "POST",
            f"/social-media-posting/{self.location_id}/posts",
            headers=self._headers(json_body=True),
            json=body,
        )

    def get_post(self, post_id: str) -> dict:
        return self._request(
            "GET",
            f"/social-media-posting/{self.location_id}/posts/{post_id}",
            headers=self._headers(),
        )

    def list_posts(
        self,
        *,
        from_iso: str,
        to_iso: str,
        status_filter: str = "all",
        post_type: str = "post",
        limit: int = 50,
        skip: int = 0,
    ) -> list[dict]:
        """List posts in a date window. status_filter: all|scheduled|draft|published|failed."""
        body = {
            "type": status_filter,
            "postType": post_type,
            "limit": limit,
            "skip": skip,
            "fromDate": from_iso,
            "toDate": to_iso,
        }
        data = self._request(
            "POST",
            f"/social-media-posting/statistics/{self.location_id}",
            headers=self._headers(json_body=True),
            json=body,
        )
        return (data or {}).get("posts", [])
