from dataclasses import dataclass
from typing import Protocol

from app.domain.entities.item import Item
from app.domain.value_objects.ids import ItemId


class ItemRepository(Protocol):
    def add(self, item: Item) -> None: ...


@dataclass
class CreateItemInput:
    name: str


class CreateItemUseCase:
    def __init__(self, repo: ItemRepository) -> None:
        self._repo = repo

    def execute(self, data: CreateItemInput) -> Item:
        item = Item(id=ItemId.new(), name=data.name)
        self._repo.add(item)
        return item
