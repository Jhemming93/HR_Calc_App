"""Verified, player-submitted offers. No Marketplace listing API is assumed."""

import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

API = "https://webapi.highrise.game"
LIFETIME = timedelta(days=7)


class ItemLookupError(Exception):
    pass


async def get_item(item_id: str) -> dict:
    """Retrieve public catalog metadata by exact Highrise item ID."""
    if not item_id or len(item_id) > 100 or not all(c.isalnum() or c in "_-" for c in item_id):
        raise ItemLookupError("Use an item ID from the Highrise item link.")
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(f"{API}/items/{item_id}")
            if response.status_code == 404:
                raise ItemLookupError("Highrise could not find that item ID.")
            response.raise_for_status()
            item = response.json().get("item")
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
        raise ItemLookupError("Highrise item lookup is unavailable. Try again later.") from exc
    if not isinstance(item, dict) or item.get("item_id") != item_id:
        raise ItemLookupError("Highrise returned an unexpected item response.")
    return item


async def search_items(query: str) -> list[dict]:
    if len(query.strip()) < 2 or len(query) > 80:
        raise ItemLookupError("Search for at least two characters (up to 80).")
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(f"{API}/items/search", params={"query": query, "limit": 5})
            response.raise_for_status()
            items = response.json().get("items")
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
        raise ItemLookupError("Highrise item search is unavailable. Try again later.") from exc
    if not isinstance(items, list):
        raise ItemLookupError("Highrise returned an unexpected search response.")
    return [item for item in items if isinstance(item, dict)][:5]


class OfferStore:
    def __init__(self, path: str | None = None):
        self.path = Path(path or os.getenv("GOLD_LAB_DB", "data/offers.sqlite3"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL, item_name TEXT NOT NULL,
                seller_id TEXT NOT NULL, seller_name TEXT NOT NULL,
                price INTEGER NOT NULL CHECK(price > 0),
                created_at TEXT NOT NULL, expires_at TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS offers_item_price ON offers(item_id, price)")

    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def add(self, item: dict, seller_id: str, seller_name: str, price: int) -> int:
        if not 1 <= price <= 2_000_000_000:
            raise ValueError("Price must be between 1 and 2,000,000,000g.")
        now = datetime.now(timezone.utc)
        with self.connect() as db:
            self._prune(db, now)
            count = db.execute("SELECT COUNT(*) FROM offers WHERE seller_id=?", (seller_id,)).fetchone()[0]
            if count >= 20:
                raise ValueError("Limit of 20 active offers. Remove one before adding another.")
            cur = db.execute(
                "INSERT INTO offers(item_id,item_name,seller_id,seller_name,price,created_at,expires_at) VALUES(?,?,?,?,?,?,?)",
                (item["item_id"], item["item_name"], seller_id, seller_name, price,
                 now.isoformat(), (now + LIFETIME).isoformat()),
            )
            return cur.lastrowid

    @staticmethod
    def _prune(db, now):
        db.execute("DELETE FROM offers WHERE expires_at <= ?", (now.isoformat(),))

    def find(self, item_id: str, max_price: int | None = None) -> list[dict]:
        now = datetime.now(timezone.utc)
        with self.connect() as db:
            self._prune(db, now)
            if max_price is None:
                rows = db.execute("SELECT * FROM offers WHERE item_id=? ORDER BY price, id LIMIT 5", (item_id,))
            else:
                rows = db.execute("SELECT * FROM offers WHERE item_id=? AND price<=? ORDER BY price, id LIMIT 5", (item_id, max_price))
            return [dict(row) for row in rows]

    def mine(self, seller_id: str) -> list[dict]:
        now = datetime.now(timezone.utc)
        with self.connect() as db:
            self._prune(db, now)
            return [dict(row) for row in db.execute(
                "SELECT * FROM offers WHERE seller_id=? ORDER BY id DESC LIMIT 5", (seller_id,))]

    def remove(self, offer_id: int, seller_id: str) -> bool:
        with self.connect() as db:
            return db.execute("DELETE FROM offers WHERE id=? AND seller_id=?", (offer_id, seller_id)).rowcount > 0
