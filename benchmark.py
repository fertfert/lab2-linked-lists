"""Сравнение операций на структурах из n элементов; результаты в results/."""

import argparse
import csv
import gc
import platform
import statistics
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynamic_array import DynamicArray
from singly_linked_list import SinglyLinkedList
from doubly_linked_list import DoublyLinkedList

OUT = Path(__file__).resolve().parent / "results"


def prepare(cls, n):
    structure = cls()
    if cls is SinglyLinkedList:
        # O(n) подготовка вместо O(n²) последовательных append без tail.
        for value in range(n - 1, -1, -1):
            structure.prepend(value)
    else:
        for value in range(n):
            structure.append(value)
    return structure


def run(sizes, repeats=5):
    OUT.mkdir(exist_ok=True)
    rows = []
    classes = (DynamicArray, SinglyLinkedList, DoublyLinkedList)
    for n in sizes:
        for cls in classes:
            for operation in ("prepend", "get_middle"):
                batch = 50 if operation == "prepend" else 200
                for repeat in range(repeats):
                    structure = prepare(cls, n)
                    if operation == "prepend":
                        if cls is DynamicArray:
                            def perform():
                                for value in range(batch):
                                    structure.insert(0, -value - 1)
                        else:
                            def perform():
                                for value in range(batch):
                                    structure.prepend(-value - 1)
                    else:
                        middle = n // 2
                        assert structure.get(middle) == middle
                        def perform():
                            for _ in range(batch):
                                structure.get(middle)
                    gc.collect()
                    start = time.perf_counter()
                    perform()
                    elapsed = time.perf_counter() - start
                    if operation == "prepend":
                        assert len(structure) == n + batch
                        assert structure.get(0) == -batch
                        assert structure.get(batch) == 0
                    rows.append((n, cls.__name__, operation, repeat + 1, batch, elapsed, elapsed / batch))
                print(f"n={n:6d} {cls.__name__:18s} {operation:10s}: "
                      f"{statistics.median(row[6] for row in rows[-repeats:]):.9f} s/op", flush=True)
    with (OUT / "measurements.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("n", "structure", "operation", "repeat", "batch_size", "batch_seconds", "seconds_per_operation"))
        writer.writerows(rows)
    for operation, title in (("prepend", "Вставка в начало"), ("get_middle", "Доступ к середине")):
        fig, ax = plt.subplots(figsize=(9, 5))
        for cls in classes:
            values = [statistics.median(row[6] for row in rows if row[0] == n and row[1] == cls.__name__ and row[2] == operation) for n in sizes]
            ax.plot(sizes, values, "o-", label=cls.__name__)
        ax.set(xlabel="Исходный размер структуры n", ylabel="Время операции, с (лог. шкала)",
               title=f"{title}: медиана {repeats} серий", yscale="log")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(OUT / f"{operation}.png", dpi=160)
        plt.close(fig)
    (OUT / "environment.txt").write_text(
        f"Python {platform.python_version()}\n{platform.platform()}\n"
        f"Clock: time.perf_counter\nRepeats: {repeats}\nSizes: {sizes}\n"
        "Prepend batch: 50 (size increases from n to n+50)\nGet batch: 200\n"
        "Preparation and correctness checks excluded; GC collected before timing, enabled during timing\n",
        encoding="utf-8")
    write_report(rows, sizes, repeats)


def write_report(rows, sizes, repeats):
    table = []
    for n in sizes:
        for operation in ("prepend", "get_middle"):
            values = [statistics.median(row[6] for row in rows if row[0] == n and row[1] == name and row[2] == operation) * 1e6
                      for name in ("DynamicArray", "SinglyLinkedList", "DoublyLinkedList")]
            table.append(f"| {n} | {operation} | " + " | ".join(f"{value:.3f}" for value in values) + " |")
    report = """# Отчёт по лабораторной работе №2

## Цель и реализация

Реализованы односвязный список без tail и двусвязный список с head и tail. Узлы содержат значение и ссылки. При удалении первого или последнего узла корректируются границы списка; удаляется первое совпадение. Разворот двусвязного списка переставляет ссылки каждого узла и меняет head с tail, сохраняя сами узлы.

В односвязный список добавлен get(index), необходимый для золотого эксперимента. В двусвязном get проход начинается от ближайшего конца. Массив перенесён из ЛР1, поэтому репозиторий запускается независимо.

## Методика измерений

Измеряются операции на заранее заполненной структуре размера n, а не время её построения. Во всех структурах перед замером одинаковая последовательность 0, 1, …, n−1. Подготовка, сборка мусора перед серией и проверки корректности находятся вне таймера. Сборщик мусора во время замера включён.

Для prepend выполняется серия из 50 вставок: размер меняется от n до n+50. Для get(n//2) выполняется 200 обращений к одной позиции. Время серии делится на количество операций, затем берётся медиана REPEATS повторов. CSV содержит исходные времена серий и нормированные значения. Использован time.perf_counter(); сведения о среде сохранены в results/environment.txt.

Такой эксперимент оценивает стоимость одной операции при размере около n. Он отличается от заполнения пустой структуры n вставками: полная серия prepend занимает O(n) у списка и O(n²) у массива. Подготовка большого односвязного списка через prepend занимает O(n), вместо O(n²) при append без tail.

## Результаты

Медиана времени одной операции, микросекунды:

| n | Операция | DynamicArray | SinglyLinkedList | DoublyLinkedList |
|---:|---|---:|---:|---:|
TABLE

![Вставка в начало](results/prepend.png)

![Доступ к середине](results/get_middle.png)

На вертикальных осях логарифмическая шкала. Замеры зависят от интерпретатора, оборудования и фоновой нагрузки. Небольшие различия между списками не меняют асимптотическую сложность. Графики показывают время одной операции, не суммарное время n операций.

## Сравнительная таблица

| Операция | DynamicArray | Односвязный без tail | Двусвязный с tail |
|---|---|---|---|
| Доступ по индексу | O(1) | O(n) | O(n), от ближайшего конца |
| Вставка в начало | O(n) | O(1) | O(1) |
| Вставка в конец | O(1) амортизированно | O(n) | O(1) |
| Удаление произвольного элемента после его обнаружения | O(n), сдвиг | O(n) для поиска предыдущего; O(1), если он известен | O(1), перестановка ссылок |
| Удаление по значению | O(n), поиск и сдвиг; в API remove принимает индекс | O(n) | O(n) |
| Поиск по значению | O(n) | O(n) | O(n) |
| Разворот | Не реализован | Не реализован | O(n), дополнительная память O(1) |
| Память, схема без накладных расходов Python | capacity ссылок на данные | n × (данные + next) | n × (данные + prev + next) |

У массива резерв capacity может превышать n. В ctypes хранятся ссылки на объекты, а не сами произвольные Python-объекты. Реальные узлы Python имеют дополнительные накладные расходы, поэтому таблица памяти — схема, а не замер байтов. Для односвязного списка с tail вставка в конец могла бы стать O(1), но по бронзовому заданию tail не используется. Публичный delete(data) двусвязного списка имеет O(n), поскольку сначала ищет значение; отдельного публичного delete_node в задании нет.

## Проверка

Пройдены 11 тестовых методов: 5 для списков и 6 для перенесённых массивов. Проверены примеры раздатки, пустой список, единственный элемент, дубликаты, удаление головы и хвоста, отсутствие значения, индексы, двойной разворот и сохранение узлов. В 3000 случайных операциях со списками после каждого изменения проверяются размер, порядок и обе стороны связей. Ограниченные проходы обнаруживают циклы без зависания тестов.

## Выводы

Вставка в начало списка меняет постоянное число ссылок, а массив сдвигает существующие элементы. Для доступа к середине массив сразу обращается к ячейке, а список проходит по ссылкам. Эксперимент иллюстрирует выбор структуры под операции: списки подходят для частых вставок в начало, массив удобнее для произвольного доступа. Двусвязность даёт обратный проход и простое отсоединение известного узла ценой дополнительной ссылки.
""".replace("TABLE", "\n".join(table)).replace("REPEATS", str(repeats))
    (OUT.parent / "REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[1000, 5000, 10000, 20000, 50000, 100000])
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if args.repeats < 1 or any(n < 1 for n in args.sizes):
        parser.error("sizes and repeats must be positive")
    run(sorted(set(args.sizes)), args.repeats)
