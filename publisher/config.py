"""Per-client config loading.

Each client has a TOML file in clients/<slug>.toml describing their location,
accounts, brand, and defaults. Their PIT lives in .env as GHL_PIT_<SLUG>
(uppercase, hyphens -> underscores).
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import tomllib  # py311+
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from dotenv import load_dotenv


HERE = Path(__file__).resolve().parent
CLIENTS_DIR = HERE / "clients"
ENV_FILE = HERE.parent / ".env"


def slug_to_env_var(slug: str) -> str:
    return "GHL_PIT_" + slug.upper().replace("-", "_")


@dataclass
class ClientConfig:
    slug: str
    location_id: str
    user_id: str
    default_timezone: str = "UTC"
    accounts: dict[str, str] = field(default_factory=dict)  # platform -> account_id
    brand: dict[str, str] = field(default_factory=dict)
    notes: dict[str, str] = field(default_factory=dict)

    @property
    def env_var(self) -> str:
        return slug_to_env_var(self.slug)

    def account_ids_for(self, platforms: list[str]) -> list[str]:
        """Map platform names (facebook, instagram, ...) -> account_ids, skipping unknown."""
        out = []
        missing = []
        for plat in platforms:
            key = plat.lower().strip()
            if key in self.accounts and self.accounts[key]:
                out.append(self.accounts[key])
            else:
                missing.append(plat)
        if missing:
            raise KeyError(
                f"Client '{self.slug}' has no account_id for: {missing}. "
                f"Available: {list(self.accounts)}"
            )
        return out


def load_client(slug: str, clients_dir: Path = CLIENTS_DIR) -> ClientConfig:
    path = clients_dir / f"{slug}.toml"
    if not path.exists():
        raise FileNotFoundError(
            f"No config for client '{slug}'. Expected: {path}\n"
            f"Run: python -m publisher.cli setup --client {slug} --token <PIT>"
        )
    with path.open("rb") as fh:
        raw = tomllib.load(fh)
    loc = raw.get("location", {})
    return ClientConfig(
        slug=slug,
        location_id=loc.get("id", ""),
        user_id=loc.get("user_id", ""),
        default_timezone=loc.get("default_timezone", "UTC"),
        accounts={k: v for k, v in raw.get("accounts", {}).items() if v},
        brand=raw.get("brand", {}),
        notes=raw.get("notes", {}),
    )


def load_token(slug: str) -> str:
    """Pull the Private Integration Token for this client from .env."""
    load_dotenv(ENV_FILE)
    var = slug_to_env_var(slug)
    token = os.environ.get(var, "").strip()
    if not token:
        raise SystemExit(
            f"Missing token: env var {var} is empty.\n"
            f"Add it to {ENV_FILE}:\n  {var}=<your-private-integration-token>\n"
            f"(See INSTALL.md for how to create a PIT in GHL.)"
        )
    return token


def write_client_toml(slug: str, data: dict, clients_dir: Path = CLIENTS_DIR) -> Path:
    """Serialize a client config dict to TOML. Used by `setup`."""
    clients_dir.mkdir(parents=True, exist_ok=True)
    path = clients_dir / f"{slug}.toml"
    lines: list[str] = []

    loc = data.get("location", {})
    lines.append("[location]")
    lines.append(f'id = "{loc.get("id", "")}"')
    lines.append(f'user_id = "{loc.get("user_id", "")}"')
    lines.append(f'default_timezone = "{loc.get("default_timezone", "UTC")}"')
    if loc.get("name"):
        lines.append(f'name = "{loc["name"]}"')
    lines.append("")

    accounts = data.get("accounts", {})
    if accounts:
        lines.append("[accounts]")
        for plat, aid in accounts.items():
            comment = ""
            note = (data.get("account_notes") or {}).get(plat)
            if note:
                comment = f"  # {note}"
            lines.append(f'{plat} = "{aid}"{comment}')
        lines.append("")

    brand = data.get("brand", {})
    if brand:
        lines.append("[brand]")
        for k, v in brand.items():
            lines.append(f'{k} = "{v}"')
        lines.append("")

    notes = data.get("notes", {})
    if notes:
        lines.append("[notes]")
        for k, v in notes.items():
            lines.append(f'{k} = "{v}"')
        lines.append("")

    path.write_text("\n".join(lines))
    return path
