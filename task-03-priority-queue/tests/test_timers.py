"""Тесты логики варианта 6 и сверка с эталоном."""

import random
import unittest

from main import run
from timers import TimerService


class ReferenceTimers:
    """Эталон: словарь активных назначений, фильтрация и сортировка при ADVANCE."""

    def __init__(self):
        self._active = {}   # id -> (at, seq)
        self._time = 0
        self._next_seq = 0

    def set(self, timer_id, at):
        self._active[timer_id] = (at, self._next_seq)
        self._next_seq += 1

    def cancel(self, timer_id):
        self._active.pop(timer_id, None)

    def advance(self, to):
        self._time = to
        due = [(at, seq, timer_id) for timer_id, (at, seq) in self._active.items() if at <= to]
        due.sort()
        fired = [(timer_id, at) for at, seq, timer_id in due]
        for timer_id, _ in fired:
            del self._active[timer_id]
        return fired


class TestTimerService(unittest.TestCase):
    def test_happy_path(self):
        service = TimerService()
        service.set("a", 5)
        service.set("b", 3)
        self.assertEqual(service.advance(3), [("b", 3)])
        self.assertEqual(service.advance(5), [("a", 5)])

    def test_set_does_not_fire_immediately(self):
        service = TimerService()
        service.set("a", 0)   # назначение в текущий момент
        self.assertEqual(service.active_count(), 1)
        self.assertEqual(service.advance(0), [("a", 0)])

    def test_advance_boundary_inclusive(self):
        service = TimerService()
        service.set("a", 7)
        self.assertEqual(service.advance(6), [])
        self.assertEqual(service.advance(7), [("a", 7)])

    def test_reschedule_earlier(self):
        service = TimerService()
        service.set("a", 10)
        service.set("a", 4)
        self.assertEqual(service.advance(4), [("a", 4)])
        # устаревшее назначение на 10 со временем отсеялось
        service.advance(10)
        self.assertEqual(service.heap_size(), 0)

    def test_reschedule_later(self):
        service = TimerService()
        service.set("a", 4)
        service.set("a", 10)
        self.assertEqual(service.advance(5), [])   # старое назначение устарело
        self.assertEqual(service.advance(10), [("a", 10)])

    def test_cancel(self):
        service = TimerService()
        service.set("a", 5)
        service.set("b", 6)
        service.cancel("a")
        self.assertEqual(service.advance(6), [("b", 6)])

    def test_cancel_missing_id_ignored(self):
        service = TimerService()
        service.set("a", 5)
        service.cancel("nope")   # не должно падать
        self.assertEqual(service.advance(5), [("a", 5)])

    def test_reuse_id_after_cancel(self):
        service = TimerService()
        service.set("a", 5)
        service.cancel("a")
        service.set("a", 7)
        self.assertEqual(service.advance(7), [("a", 7)])

    def test_reuse_id_after_fire(self):
        service = TimerService()
        service.set("a", 5)
        self.assertEqual(service.advance(5), [("a", 5)])
        service.set("a", 9)
        self.assertEqual(service.advance(9), [("a", 9)])

    def test_equal_times_order_by_assignment(self):
        service = TimerService()
        service.set("x", 5)
        service.set("y", 5)
        service.set("z", 4)
        self.assertEqual(service.advance(5), [("z", 4), ("x", 5), ("y", 5)])

    def test_equal_times_after_reschedule(self):
        service = TimerService()
        service.set("x", 5)
        service.set("y", 5)
        service.set("x", 5)   # x переназначен позже, значит сработает после y
        self.assertEqual(service.advance(5), [("y", 5), ("x", 5)])

    def test_advance_without_events(self):
        service = TimerService()
        service.set("a", 100)
        self.assertEqual(service.advance(10), [])
        self.assertEqual(service.advance(50), [])
        self.assertEqual(service.time, 50)

    def test_advance_to_current_time(self):
        service = TimerService()
        service.set("a", 3)
        self.assertEqual(service.advance(3), [("a", 3)])
        self.assertEqual(service.advance(3), [])

    def test_time_does_not_go_back(self):
        service = TimerService()
        service.advance(10)
        with self.assertRaises(ValueError):
            service.advance(9)

    def test_set_in_the_past_raises(self):
        service = TimerService()
        service.advance(10)
        with self.assertRaises(ValueError):
            service.set("a", 9)


class TestHeapSizeAccounting(unittest.TestCase):
    def test_stale_assignments_stay_in_heap(self):
        service = TimerService()
        service.set("a", 5)
        service.set("a", 6)
        service.set("a", 7)
        service.cancel("a")
        # три назначения лежат в куче, активных нет
        self.assertEqual(service.heap_size(), 3)
        self.assertEqual(service.active_count(), 0)
        self.assertEqual(service.stale_count(), 3)

    def test_heap_shrinks_only_on_advance(self):
        service = TimerService()
        service.set("a", 3)
        service.set("b", 3)
        service.set("c", 3)
        service.cancel("b")
        self.assertEqual(service.heap_size(), 3)
        self.assertEqual(service.active_count(), 2)
        self.assertEqual(service.advance(3), [("a", 3), ("c", 3)])
        self.assertEqual(service.heap_size(), 0)
        self.assertEqual(service.stale_count(), 0)

    def test_heap_size_grows_with_reschedules(self):
        service = TimerService()
        for at in range(10, 20):
            service.set("a", at)
        service.set("b", 5)
        self.assertEqual(service.active_count(), 2)
        self.assertEqual(service.heap_size(), 11)


class TestAgainstReference(unittest.TestCase):
    @staticmethod
    def random_commands(rng, count):
        ids = ["a", "b", "c", "d"]
        current = 0
        commands = []
        for _ in range(count):
            roll = rng.random()
            if roll < 0.5:
                at = rng.randint(current, current + 8)
                commands.append(("SET", rng.choice(ids), at))
            elif roll < 0.7:
                commands.append(("CANCEL", rng.choice(ids), None))
            else:
                to = rng.randint(current, current + 8)
                current = to
                commands.append(("ADVANCE", None, to))
        return commands

    def test_matches_reference_on_random_input(self):
        for seed in range(20):
            rng = random.Random(seed)
            commands = self.random_commands(rng, 120)
            service = TimerService()
            reference = ReferenceTimers()
            for kind, first, second in commands:
                if kind == "SET":
                    service.set(first, second)
                    reference.set(first, second)
                elif kind == "CANCEL":
                    service.cancel(first)
                    reference.cancel(first)
                else:
                    self.assertEqual(service.advance(second), reference.advance(second))
            self.assertEqual(service.active_count(), len(reference._active))


class TestCliRun(unittest.TestCase):
    def test_run_matches_expected_answers(self):
        lines = [
            '{"cmd": "SET", "id": "a", "at": 5}',
            '{"cmd": "SET", "id": "b", "at": 3}',
            '{"cmd": "ADVANCE", "to": 3}',
            '{"cmd": "ADVANCE", "to": 5}',
            '{"cmd": "ADVANCE", "to": 6}',
        ]
        self.assertEqual(run(lines), [[("b", 3)], [("a", 5)], []])

    def test_end_of_input_does_not_advance(self):
        lines = ['{"cmd": "SET", "id": "a", "at": 5}']
        self.assertEqual(run(lines), [])


if __name__ == "__main__":
    unittest.main()
