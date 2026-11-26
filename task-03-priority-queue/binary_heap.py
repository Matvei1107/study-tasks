"""Своя бинарная куча на массиве (без heapq и готовых куч).

Поддерживает:
- направление min-heap / max-heap;
- произвольный ключ (key), по которому сравниваются элементы.

Основные операции: push, pop, size, peek, replace_top, heapify.
Внутри данные лежат в списке, индекс 0 - вершина кучи.
"""


class BinaryHeap:
    def __init__(self, items=None, min_heap=True, key=None):
        self._data = list(items) if items is not None else []
        self._min_heap = min_heap
        self._key = key if key is not None else (lambda x: x)
        if self._data:
            self.heapify()

    # --- сравнение элементов ---
    def _before(self, a, b):
        """True, если a должен стоять в куче выше b."""
        ka = self._key(a)
        kb = self._key(b)
        if self._min_heap:
            return ka < kb
        return ka > kb

    @staticmethod
    def _parent(i):
        return (i - 1) // 2

    @staticmethod
    def _left(i):
        return 2 * i + 1

    @staticmethod
    def _right(i):
        return 2 * i + 2

    def _sift_up(self, i):
        # элемент поднимается, пока он "выше" родителя
        while i > 0:
            p = self._parent(i)
            if self._before(self._data[i], self._data[p]):
                self._data[i], self._data[p] = self._data[p], self._data[i]
                i = p
            else:
                break

    def _sift_down(self, i):
        # элемент опускается к "лучшему" из детей, пока нужно
        n = len(self._data)
        while True:
            left = self._left(i)
            right = self._right(i)
            best = i
            if left < n and self._before(self._data[left], self._data[best]):
                best = left
            if right < n and self._before(self._data[right], self._data[best]):
                best = right
            if best == i:
                break
            self._data[i], self._data[best] = self._data[best], self._data[i]
            i = best

    # --- пользовательские операции ---
    def push(self, item):
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        if not self._data:
            raise IndexError("pop из пустой кучи")
        top = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._sift_down(0)
        return top

    def peek(self):
        if not self._data:
            raise IndexError("peek у пустой кучи")
        return self._data[0]

    def replace_top(self, item):
        """Заменить вершину новым элементом и восстановить кучу за O(log n)."""
        if not self._data:
            raise IndexError("replace_top у пустой кучи")
        top = self._data[0]
        self._data[0] = item
        self._sift_down(0)
        return top

    def heapify(self):
        """Построить кучу на месте за O(n): просеиваем вниз от середины к началу."""
        n = len(self._data)
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(i)

    def size(self):
        return len(self._data)

    def is_empty(self):
        return not self._data

    def check_invariant(self):
        """Проверка свойства кучи: любой родитель не хуже своих детей."""
        n = len(self._data)
        for i in range(n):
            left = self._left(i)
            right = self._right(i)
            if left < n and self._before(self._data[left], self._data[i]):
                return False
            if right < n and self._before(self._data[right], self._data[i]):
                return False
        return True
