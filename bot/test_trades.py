import tempfile
import unittest
from pathlib import Path

from trades import OfferStore


class OfferStoreTests(unittest.TestCase):
    def test_filter_owner_and_order(self):
        with tempfile.TemporaryDirectory() as directory:
            store = OfferStore(str(Path(directory) / "offers.sqlite3"))
            item = {"item_id": "abc", "item_name": "Moon Hat"}
            costly = store.add(item, "user1", "Seller", 1200)
            cheap = store.add(item, "user2", "Buyer", 900)
            store.add({"item_id": "xyz", "item_name": "Other"}, "user1", "Seller", 100)
            self.assertEqual([offer["id"] for offer in store.find("abc", 1000)], [cheap])
            self.assertEqual([offer["id"] for offer in store.find("abc")], [cheap, costly])
            self.assertFalse(store.remove(costly, "user2"))
            self.assertTrue(store.remove(costly, "user1"))
            self.assertEqual([offer["id"] for offer in store.find("abc")], [cheap])

    def test_expired_offers_are_not_returned(self):
        with tempfile.TemporaryDirectory() as directory:
            store = OfferStore(str(Path(directory) / "offers.sqlite3"))
            item = {"item_id": "abc", "item_name": "Moon Hat"}
            store.add(item, "user1", "Seller", 1200)
            with store.connect() as db:
                db.execute("UPDATE offers SET expires_at='2020-01-01T00:00:00+00:00'")
            self.assertEqual(store.find("abc"), [])


if __name__ == "__main__":
    unittest.main()
