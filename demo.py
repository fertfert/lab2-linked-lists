"""Примеры операций из раздатки. Запуск: python demo.py."""

from singly_linked_list import SinglyLinkedList
from doubly_linked_list import DoublyLinkedList


def main():
    for cls in (SinglyLinkedList, DoublyLinkedList):
        linked = cls()
        print(cls.__name__)
        linked.prepend(10)
        linked.prepend(20)
        linked.append(30)
        print("After prepend/append:", linked)
        print("Length:", len(linked), "get(1):", linked.get(1))
        print("find(10):", linked.find(10).data, "find(99):", linked.find(99))
        if isinstance(linked, DoublyLinkedList):
            linked.reverse()
            print("After reverse:", linked)
        for value in (10, 20, 30):
            linked.delete(value)
            print("After delete", value, ":", linked)


if __name__ == "__main__":
    main()
