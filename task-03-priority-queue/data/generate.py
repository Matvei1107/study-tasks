"""Генератор случайного потока команд для варианта 6.

Пишет JSONL в стандартный вывод. Соблюдает ограничения задачи:
at >= текущего времени, to не убывает.

Пример:
    python generate.py --count 30 --seed 42 > data/random.jsonl
"""

import argparse
import json
import random


def generate(count, seed, ids, max_time):
    rng = random.Random(seed)
    current = 0
    commands = []
    for _ in range(count):
        roll = rng.random()
        if roll < 0.5:
            timer_id = rng.choice(ids)
            at = rng.randint(current, current + max_time)
            commands.append({"cmd": "SET", "id": timer_id, "at": at})
        elif roll < 0.7:
            commands.append({"cmd": "CANCEL", "id": rng.choice(ids)})
        else:
            to = rng.randint(current, current + max_time)
            current = to
            commands.append({"cmd": "ADVANCE", "to": to})
    return commands


def main():
    parser = argparse.ArgumentParser(description="генератор команд варианта 6")
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--ids", type=int, default=8, help="сколько разных id использовать")
    parser.add_argument("--max-time", type=int, default=10, help="размах времени")
    args = parser.parse_args()

    ids = ["t%d" % i for i in range(args.ids)]
    commands = generate(args.count, args.seed, ids, args.max_time)
    for command in commands:
        print(json.dumps(command, ensure_ascii=False))


if __name__ == "__main__":
    main()
