# SOURCE: https://gist.github.com/malmaud/7dab52ab7649d78efdc09b885f3a7079
import attr
from typing import *
from dataclasses import dataclass
import asyncio
import types
import re


class InputAwait:
    target: str

    def __init__(self, target) -> None:
        self.target = target


@types.coroutine
def get_input(target: str) -> Iterable[Union[str, InputAwait]]:
    res = yield InputAwait(target)
    return res


def get_hit(target: str, x: str) -> Optional[str]:
    m = re.match(target + r"\s(.*)", x)
    if m:
        return m[1]
    else:
        return None


def get_hits(targets: List[str]) -> Tuple[int, str]:
    while True:
        x = input()
        for i, target in enumerate(targets):
            m = get_hit(target, x)
            if m is None:
                continue
            return i, m


async def f() -> int:
    value = await get_input("x")
    return int(value) + 1


async def g() -> str:
    value = await get_input("y")
    return f"Thanks for saying {value}"


class AsyncInput:
    tasks: List[Coroutine] = []

    def __init__(self, *tasks):
        self.tasks = tasks

    def run_tasks(self) -> List:
        results: List = []
        queue: List[str] = []
        for task in self.tasks:
            res = task.send(None)
            if isinstance(res, InputAwait):
                queue.append(res.target)
            else:
                raise ValueError("bad yield")
        done_tasks = 0
        while done_tasks < len(self.tasks):
            task_id, hit_res = get_hits(queue)
            try:
                self.tasks[task_id].send(hit_res)
            except StopIteration as err:
                results.append((task_id, err.value))
                done_tasks += 1

        return results
