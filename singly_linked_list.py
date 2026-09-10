"""ЛР2. Односвязный список без tail и встроенного контейнера."""

import operator


class Node:
    def __init__(self, data, next_node=None):
        self.data = data
        self.next = next_node


class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    def prepend(self, data):
        """Вставка в начало: O(1)."""
        self.head = Node(data, self.head)
        self._size += 1

    def append(self, data):
        """Вставка в конец без tail: O(n)."""
        node = Node(data)
        if self.head is None:
            self.head = node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = node
        self._size += 1

    def find(self, data):
        """Первый узел с заданным значением либо None: O(n)."""
        current = self.head
        while current is not None:
            if current.data == data:
                return current
            current = current.next
        return None

    def delete(self, data):
        """Удаляет первое совпадение. Отсутствие значения допустимо. O(n)."""
        previous = None
        current = self.head
        while current is not None:
            if current.data == data:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                current.next = None
                self._size -= 1
                return
            previous, current = current, current.next

    def get(self, index):
        """Доступ по индексу для золотого эксперимента: O(n)."""
        index = operator.index(index)
        if not 0 <= index < self._size:
            raise IndexError("Index out of bounds")
        current = self.head
        for _ in range(index):
            current = current.next
        return current.data

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
        return " -> ".join(str(value) for value in self) + " -> None"
