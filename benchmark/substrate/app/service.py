"""Minimal task service used by the benchmark substrate repository."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Task:
    """A single unit of work."""

    task_id: int
    title: str
    done: bool = False


@dataclass
class TaskService:
    """In-memory task registry with sequential identifiers."""

    _next_id: int = 1
    _tasks: Dict[int, Task] = field(default_factory=dict)

    def create(self, title: str) -> Task:
        cleaned = title.strip()
        if not cleaned:
            raise ValueError("title must not be empty")
        task = Task(task_id=self._next_id, title=cleaned)
        self._tasks[task.task_id] = task
        self._next_id += 1
        return task

    def complete(self, task_id: int) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"unknown task: {task_id}")
        task.done = True
        return task

    def pending(self) -> List[Task]:
        return [task for task in self._tasks.values() if not task.done]

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)
