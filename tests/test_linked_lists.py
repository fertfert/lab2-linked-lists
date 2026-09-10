import random
import unittest

from singly_linked_list import SinglyLinkedList
from doubly_linked_list import DoublyLinkedList


class LinkedListTests(unittest.TestCase):
    def assert_structure(self, linked, values):
        self.assertEqual(len(linked), len(values))
        current, previous = linked.head, None
        # Ограниченный проход обнаруживает циклы без зависания теста.
        for value in values:
            self.assertIsNotNone(current)
            self.assertEqual(current.data, value)
            if isinstance(linked, DoublyLinkedList):
                self.assertIs(current.prev, previous)
            previous, current = current, current.next
        self.assertIsNone(current)
        if isinstance(linked, DoublyLinkedList):
            self.assertIs(linked.tail, previous)
            current, following = linked.tail, None
            for value in reversed(values):
                self.assertIsNotNone(current)
                self.assertEqual(current.data, value)
                self.assertIs(current.next, following)
                following, current = current, current.prev
            self.assertIsNone(current)
            self.assertIs(linked.head, following)

    def test_handout(self):
        for cls, arrow in ((SinglyLinkedList, " -> "), (DoublyLinkedList, " <-> ")):
            linked = cls()
            linked.prepend(10)
            linked.prepend(20)
            linked.append(30)
            self.assertEqual(str(linked), arrow.join(("20", "10", "30", "None")))
            self.assert_structure(linked, [20, 10, 30])
            self.assertEqual(linked.find(10).data, 10)
            self.assertIsNone(linked.find(99))
            for value, expected in ((10, [20, 30]), (20, [30]), (30, [])):
                linked.delete(value)
                self.assert_structure(linked, expected)
            self.assertEqual(str(linked), "None")
        linked = DoublyLinkedList()
        linked.prepend(10)
        linked.prepend(20)
        linked.append(30)
        linked.reverse()
        self.assertEqual(str(linked), "30 <-> 10 <-> 20 <-> None")
        self.assert_structure(linked, [30, 10, 20])
        self.assertEqual([linked.get(i) for i in range(3)], [30, 10, 20])
        with self.assertRaises(IndexError):
            linked.get(3)

    def test_empty_singleton_and_bounds(self):
        for cls in (SinglyLinkedList, DoublyLinkedList):
            linked = cls()
            linked.delete(99)
            self.assertIsNone(linked.find(99))
            if isinstance(linked, DoublyLinkedList):
                linked.reverse()
            self.assert_structure(linked, [])
            linked.append(None)
            self.assertIsNone(linked.get(0))
            if isinstance(linked, DoublyLinkedList):
                linked.reverse()
            for index in (-1, 1, 100):
                with self.assertRaises(IndexError):
                    linked.get(index)
            with self.assertRaises(TypeError):
                linked.get(0.5)
            linked.delete(None)
            self.assert_structure(linked, [])
            linked.prepend(7)
            self.assert_structure(linked, [7])

    def test_duplicates_and_tail(self):
        for cls in (SinglyLinkedList, DoublyLinkedList):
            linked = cls()
            for value in (1, 2, 1, 3):
                linked.append(value)
            first = linked.find(1)
            self.assertIs(first, linked.head)
            linked.delete(1)
            self.assertIsNone(first.next)
            self.assert_structure(linked, [2, 1, 3])
            linked.delete(3)
            linked.append(4)
            linked.delete(99)
            self.assert_structure(linked, [2, 1, 4])

    def test_reverse_preserves_nodes(self):
        linked = DoublyLinkedList()
        for i in range(5):
            linked.append(i)
        nodes = [linked.find(i) for i in range(5)]
        linked.reverse()
        self.assert_structure(linked, [4, 3, 2, 1, 0])
        for i, node in enumerate(nodes):
            self.assertIs(linked.find(i), node)
        linked.reverse()
        self.assert_structure(linked, list(range(5)))

    def test_randomized(self):
        for cls in (SinglyLinkedList, DoublyLinkedList):
            rng = random.Random(2026)
            linked, reference = cls(), []
            for _ in range(1500):
                operation, value = rng.randrange(5), rng.randrange(10)
                if operation == 0:
                    linked.prepend(value)
                    reference.insert(0, value)
                elif operation == 1:
                    linked.append(value)
                    reference.append(value)
                elif operation == 2:
                    linked.delete(value)
                    if value in reference:
                        reference.remove(value)
                elif operation == 3 and isinstance(linked, DoublyLinkedList):
                    linked.reverse()
                    reference.reverse()
                else:
                    node = linked.find(value)
                    self.assertEqual(node is not None, value in reference)
                    if node is not None:
                        self.assertEqual(node.data, value)
                self.assert_structure(linked, reference)
                if reference:
                    index = rng.randrange(len(reference))
                    self.assertEqual(linked.get(index), reference[index])


if __name__ == "__main__":
    unittest.main()
