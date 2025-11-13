#!/usr/bin/env python3
import unittest
import xmlrunner
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from lru import LRUCache


class TestLRUCacheProvider(unittest.TestCase):
    def test_has_nonexistent_key(self):
        lru_cache = LRUCache(item_limit=10)
        lru_cache.set("foo", "bar")
        self.assertFalse(lru_cache.has("bar"))
        self.assertFalse(lru_cache.has(""))

    def test_has_existing_key(self):
        lru_cache = LRUCache(item_limit=10)
        lru_cache.set("foo", "bar")
        self.assertTrue(lru_cache.has("foo"))

    def test_has_expired_key(self):
        lru_cache = LRUCache(item_limit=1)
        lru_cache.set("foo", "bar")
        lru_cache.set("baz", "bar")
        self.assertFalse(lru_cache.has("foo"))
        self.assertTrue(lru_cache.has("baz"))

    def test_has_remove_least_recently_used_key_when_lru_was_inserted_last(self):
        lru_cache = LRUCache(item_limit=2)
        lru_cache.set("foo", "bar")
        lru_cache.set("bar", "bar")
        lru_cache.has("foo")
        lru_cache.set("baz", "bar")
        self.assertTrue(lru_cache.has("foo"))
        self.assertFalse(lru_cache.has("bar"))
        self.assertTrue(lru_cache.has("baz"))

    def test_has_remove_least_recently_used_key_when_lru_was_inserted_first(self):
        lru_cache = LRUCache(item_limit=2)
        lru_cache.set("foo", "bar")
        lru_cache.set("bar", "bar")
        lru_cache.has("foo")
        lru_cache.has("bar")
        lru_cache.set("baz", "bar")
        self.assertFalse(lru_cache.has("foo"))
        self.assertTrue(lru_cache.has("bar"))
        self.assertTrue(lru_cache.has("baz"))

    def test_has_recreated_key_after_expiration(self):
        lru_cache = LRUCache(item_limit=1)
        lru_cache.set("foo", "bar")
        lru_cache.set("baz", "bar")
        lru_cache.set("foo", "bar")
        self.assertTrue(lru_cache.has("foo"))

    def test_has_many_existing_keys(self):
        lru_cache = LRUCache(item_limit=10)
        lru_cache.set("foo", "bar")
        lru_cache.set("baz", "bar")
        self.assertTrue(lru_cache.has("foo"))
        self.assertTrue(lru_cache.has("baz"))

    def test_get_nonexistent_key(self):
        lru_cache = LRUCache(item_limit=10)
        lru_cache.set("foo", "bar")
        self.assertIsNone(lru_cache.get("bar"))
        self.assertIsNone(lru_cache.get(""))

    def test_get_existing_key(self):
        lru_cache = LRUCache(item_limit=10)
        lru_cache.set("foo", "bar")
        self.assertEqual(lru_cache.get("foo"), "bar")

    def test_get_expired_key(self):
        lru_cache = LRUCache(item_limit=1)
        lru_cache.set("foo", "bar")
        lru_cache.set("baz", "bar")
        self.assertIsNone(lru_cache.get("foo"))
        self.assertEqual(lru_cache.get("baz"), "bar")

    def test_get_remove_least_recently_used_key_when_lru_was_inserted_last_get(self):
        lru_cache = LRUCache(item_limit=2)
        lru_cache.set("foo", "bar")
        lru_cache.set("bar", "bar")
        lru_cache.get("foo")
        lru_cache.set("baz", "bar")
        self.assertEqual(lru_cache.get("foo"), "bar")
        self.assertIsNone(lru_cache.get("bar"))
        self.assertEqual(lru_cache.get("baz"), "bar")

    def test_get_remove_least_recently_used_key_when_lru_was_inserted_last_has(self):
        lru_cache = LRUCache(item_limit=2)
        lru_cache.set("foo", "bar")
        lru_cache.set("bar", "bar")
        lru_cache.has("foo")
        lru_cache.set("baz", "bar")
        self.assertEqual(lru_cache.get("foo"), "bar")
        self.assertIsNone(lru_cache.get("bar"))
        self.assertEqual(lru_cache.get("baz"), "bar")

    def test_get_remove_least_recently_used_key_when_lru_was_inserted_last_set(self):
        lru_cache = LRUCache(item_limit=2)
        lru_cache.set("foo", "bar")
        lru_cache.set("bar", "bar")
        lru_cache.set("foo", "bar")
        lru_cache.set("baz", "bar")
        self.assertEqual(lru_cache.get("foo"), "bar")
        self.assertIsNone(lru_cache.get("bar"))
        self.assertEqual(lru_cache.get("baz"), "bar")

    def test_get_remove_least_recently_used_key_when_lru_was_inserted_first(self):
        lru_cache = LRUCache(item_limit=2)
        lru_cache.set("foo", "bar")
        lru_cache.set("bar", "bar")
        lru_cache.get("foo")
        lru_cache.get("bar")
        lru_cache.set("baz", "bar")
        self.assertIsNone(lru_cache.get("foo"))
        self.assertEqual(lru_cache.get("bar"), "bar")
        self.assertEqual(lru_cache.get("baz"), "bar")

    def test_get_recreated_key_after_expiration(self):
        lru_cache = LRUCache(item_limit=1)
        lru_cache.set("foo", "bar")
        lru_cache.set("baz", "bar")
        lru_cache.set("foo", "bar")
        self.assertEqual(lru_cache.get("foo"), "bar")
        self.assertIsNone(lru_cache.get("baz"))

    def test_get_many_existing_keys(self):
        lru_cache = LRUCache(item_limit=10)
        lru_cache.set("foo", "foo")
        lru_cache.set("baz", "baz")
        self.assertEqual(lru_cache.get("foo"), "foo")
        self.assertEqual(lru_cache.get("baz"), "baz")


if __name__ == "__main__":
    if os.getenv('CI'):
        os.makedirs('test-reports', exist_ok=True)
        xml_output = 'test-reports/lru.xml'
        with open(xml_output, 'wb') as output:
            unittest.main(
                testRunner=xmlrunner.XMLTestRunner(output=output, verbosity=2) ,exit=False, failfast=False, buffer=False, catchbreak=False
            )
        sys.exit(0)
    else:
        unittest.main()
        sys.exit(0)