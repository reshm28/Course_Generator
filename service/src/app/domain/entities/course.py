from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class Lesson:
    title: str
    summary: str
    objectives: List[str] = field(default_factory=list)
    key_points: List[str] = field(default_factory=list)


@dataclass(slots=True)
class Module:
    title: str
    description: str
    lessons: List[Lesson] = field(default_factory=list)


@dataclass(slots=True)
class Course:
    topic: str
    modules: List[Module] = field(default_factory=list)
