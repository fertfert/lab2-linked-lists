"""ЛР2. Двусвязный список с head и tail."""

import operator


class DNode:
    def __init__(self, data, prev=None, next=None):
        self.data = data
        self.prev = prev
        self.next = next


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def prepend(self, data):
        """O(1)."""
        node = DNode(data, None, self.head)
        if self.head is None:
            self.tail = node
        else:
            self.head.prev = node
        self.head = node
        self._size += 1

    def append(self, data):
        """O(1), поскольку хранится tail."""
        node = DNode(data, self.tail, None)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1

    def find(self, data):
        """Возвращает первый узел либо None. O(n)."""
        current = self.head
        while current is not None:
            if current.data == data:
                return current
            current = current.next
        return None

    def delete(self, data):
        """Удаляет первое совпадение: O(n) с учётом поиска."""
        node = self.find(data)
        if node is None:
            return
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev
        node.prev = node.next = None
        self._size -= 1

    def get(self, index):
        """Проход от ближайшего конца. Худший случай O(n)."""
        index = operator.index(index)
        if not 0 <= index < self._size:
            raise IndexError("Index out of bounds")
        if index < self._size // 2:
            current = self.head
            for _ in range(index):
                current = current.next
        else:
            current = self.tail
            for _ in range(self._size - 1 - index):
                current = current.prev
        return current.data

    def reverse(self):
        """Разворот на месте: O(n) времени, O(1) дополнительной памяти."""
        current = self.head
        while current is not None:
            current.prev, current.next = current.next, current.prev
            current = current.prev
        self.head, self.tail = self.tail, self.head

    def __len__(self):
        return self._size

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def __str__(self):
        if self.head is None:
            return "None"
        return " <-> ".join(str(value) for value in self) + " <-> None"
