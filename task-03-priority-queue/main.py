"""Разбор команд варианта 6 и запуск.

На вход - поток команд в JSONL, по одной на строку:
    {"cmd": "SET", "id": "t1", "at": 5}
    {"cmd": "CANCEL", "id": "t1"}
    {"cmd": "ADVANCE", "to": 10}

На каждый ADVANCE печатается JSON-массив сработавших таймеров:
    [["t1", 5], ["t2", 5]]

Использование:
    python main.py data/example.jsonl
    python main.py -            # читать со стандартного ввода
"""

import json
import sys

from timers import TimerService


def handle(service, command):
    """Выполнить одну команду. Для ADVANCE вернуть список сработавших таймеров."""
    cmd = command["cmd"]
    if cmd == "SET":
        service.set(str(command["id"]), int(command["at"]))
        return None
    if cmd == "CANCEL":
        service.cancel(str(command["id"]))
        return None
    if cmd == "ADVANCE":
        return service.advance(int(command["to"]))
    raise ValueError("неизвестная команда: %r" % (cmd,))


def run(lines):
    """Прогнать строки входа и вернуть список ответов (по одному на ADVANCE)."""
    service = TimerService()
    answers = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        command = json.loads(line)
        fired = handle(service, command)
        if fired is not None:
            answers.append(fired)
    return answers


def main(argv):
    if len(argv) != 2:
        print("использование: python main.py <файл с командами | ->", file=sys.stderr)
        return 1
    source = argv[1]
    if source == "-":
        lines = sys.stdin
        for fired in run(lines):
            print(json.dumps(fired, ensure_ascii=False))
    else:
        with open(source, encoding="utf-8") as f:
            for fired in run(f):
                print(json.dumps(fired, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
