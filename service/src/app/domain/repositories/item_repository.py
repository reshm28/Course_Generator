from abc import ABC, abstractmethod
from typing import Iterable

from app.domain.entities.item import Item
from app.domain.value_objects.ids import ItemId


class ItemRepository(ABC):
    @abstractmethod
    def add(self, item: Item) -> None: ...

    @abstractmethod
    def get(self, item_id: ItemId) -> Item | None: ...

    @abstractmethod
    def list(self) -> Iterable[Item]: ...
