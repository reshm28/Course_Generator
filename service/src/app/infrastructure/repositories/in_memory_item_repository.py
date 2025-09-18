from typing import Dict, Iterable

from app.domain.repositories.item_repository import ItemRepository
from app.domain.entities.item import Item
from app.domain.value_objects.ids import ItemId


class InMemoryItemRepository(ItemRepository):
    def __init__(self) -> None:
        self._items: Dict[str, Item] = {}

    def add(self, item: Item) -> None:
        self._items[item.id.value] = item

    def get(self, item_id: ItemId) -> Item | None:
        return self._items.get(item_id.value)

    def list(self) -> Iterable[Item]:
        return list(self._items.values())
