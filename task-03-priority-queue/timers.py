"""Вариант 6: таймеры с переносом и отменой.

Команды:
    SET <id> <at>   - назначить таймеру id момент at; прежнее назначение
                      того же id заменяется, сразу таймер не срабатывает;
    CANCEL <id>     - отменить активный таймер; отсутствующий id игнорируется;
    ADVANCE <to>    - продвинуть модельное время до to и выдать сработавшие
                      таймеры (включая границу to) по времени, при равенстве -
                      по порядку назначений.

Назначения лежат в min-куче, активные таймеры - в обычном словаре.
При переносе/отмене старая запись остаётся в куче (ленивое удаление) и
отсеивается при извлечении по уникальному номеру назначения seq.
"""

from dataclasses import dataclass

from binary_heap import BinaryHeap


@dataclass
class Assignment:
    timer_id: str
    at: int
    seq: int


class TimerService:
    def __init__(self):
        # min-куча: раньше срабатывает меньший at, при равенстве - меньшее seq
        self._heap = BinaryHeap(min_heap=True, key=lambda a: (a.at, a.seq))
        self._active = {}   # id -> актуальное назначение
        self._time = 0      # текущее модельное время
        self._next_seq = 0

    def set(self, timer_id, at):
        if at < self._time:
            raise ValueError("at не может быть меньше текущего времени")
        assignment = Assignment(timer_id, at, self._next_seq)
        self._next_seq += 1
        # старая запись для этого id (если была) остаётся в куче как устаревшая
        self._heap.push(assignment)
        self._active[timer_id] = assignment

    def cancel(self, timer_id):
        # отсутствующий id просто игнорируем
        self._active.pop(timer_id, None)

    def advance(self, to):
        if to < self._time:
            raise ValueError("время не может идти назад")
        self._time = to
        fired = []
        # вынимаем всё, что должно сработать не позже to (граница включается)
        while not self._heap.is_empty() and self._heap.peek().at <= to:
            assignment = self._heap.pop()
            # устаревшую запись (перенос или отмена) просто выбрасываем
            if self._active.get(assignment.timer_id) is assignment:
                del self._active[assignment.timer_id]
                fired.append((assignment.timer_id, assignment.at))
        return fired

    @property
    def time(self):
        return self._time
