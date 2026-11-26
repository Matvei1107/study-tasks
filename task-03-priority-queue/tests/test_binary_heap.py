"""Тесты бинарной кучи: порядок, heapify, replace_top, инвариант."""

import random
import unittest

from binary_heap import BinaryHeap


def pop_all(heap):
    result = []
    while not heap.is_empty():
        result.append(heap.pop())
    return result


class TestBinaryHeap(unittest.TestCase):
    def test_min_heap_order(self):
        heap = BinaryHeap(min_heap=True)
        for value in [5, 1, 4, 2, 3]:
            heap.push(value)
        self.assertEqual(pop_all(heap), [1, 2, 3, 4, 5])

    def test_max_heap_order(self):
        heap = BinaryHeap(min_heap=False)
        for value in [5, 1, 4, 2, 3]:
            heap.push(value)
        self.assertEqual(pop_all(heap), [5, 4, 3, 2, 1])

    def test_peek_does_not_remove(self):
        heap = BinaryHeap([3, 1, 2])
        self.assertEqual(heap.peek(), 1)
        self.assertEqual(heap.size(), 3)

    def test_size_and_empty(self):
        heap = BinaryHeap()
        self.assertTrue(heap.is_empty())
        self.assertEqual(heap.size(), 0)
        heap.push(10)
        self.assertFalse(heap.is_empty())
        self.assertEqual(heap.size(), 1)

    def test_pop_empty_raises(self):
        with self.assertRaises(IndexError):
            BinaryHeap().pop()

    def test_peek_empty_raises(self):
        with self.assertRaises(IndexError):
            BinaryHeap().peek()

    def test_replace_top_min(self):
        heap = BinaryHeap([1, 3, 2, 5, 4])
        old = heap.replace_top(6)
        self.assertEqual(old, 1)
        self.assertEqual(heap.peek(), 2)
        self.assertEqual(pop_all(heap), [2, 3, 4, 5, 6])

    def test_replace_top_max(self):
        heap = BinaryHeap([5, 3, 4, 1, 2], min_heap=False)
        old = heap.replace_top(0)
        self.assertEqual(old, 5)
        self.assertEqual(heap.peek(), 4)
        self.assertEqual(pop_all(heap), [4, 3, 2, 1, 0])

    def test_replace_top_empty_raises(self):
        with self.assertRaises(IndexError):
            BinaryHeap().replace_top(1)

    def test_heapify_builds_valid_heap(self):
        items = [9, 4, 7, 1, 8, 2, 6, 3, 5, 0]
        heap = BinaryHeap(items, min_heap=True)
        self.assertTrue(heap.check_invariant())
        self.assertEqual(pop_all(heap), sorted(items))

    def test_heapify_keeps_same_elements(self):
        items = [5, 5, 1, 3, 3, 3, 2]
        heap = BinaryHeap(items)
        self.assertEqual(sorted(pop_all(heap)), sorted(items))

    def test_heapify_empty_and_single(self):
        empty = BinaryHeap([])
        self.assertTrue(empty.check_invariant())
        self.assertEqual(empty.size(), 0)
        single = BinaryHeap([42])
        self.assertTrue(single.check_invariant())
        self.assertEqual(single.peek(), 42)

    def test_invariant_after_operations(self):
        rng = random.Random(123)
        heap = BinaryHeap()
        for _ in range(200):
            if heap.is_empty() or rng.random() < 0.6:
                heap.push(rng.randint(-50, 50))
            else:
                heap.pop()
            self.assertTrue(heap.check_invariant())

    def test_custom_key_with_max_heap(self):
        # сортируем строки по длине по убыванию
        heap = BinaryHeap(min_heap=False, key=len)
        for word in ["a", "ccc", "bb", "dddd"]:
            heap.push(word)
        self.assertEqual(pop_all(heap), ["dddd", "ccc", "bb", "a"])

    def test_key_tuple_orders_ties(self):
        # min-куча по (время, номер) - как в варианте 6
        heap = BinaryHeap(min_heap=True, key=lambda x: (x[0], x[1]))
        for item in [(5, 1), (3, 0), (5, 0), (3, 5)]:
            heap.push(item)
        self.assertEqual(pop_all(heap), [(3, 0), (3, 5), (5, 0), (5, 1)])

    def test_duplicates(self):
        heap = BinaryHeap([2, 2, 2, 2], min_heap=True)
        self.assertEqual(heap.size(), 4)
        self.assertEqual(pop_all(heap), [2, 2, 2, 2])


if __name__ == "__main__":
    unittest.main()
