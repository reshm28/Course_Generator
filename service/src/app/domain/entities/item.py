from dataclasses import dataclass

from app.domain.value_objects.ids import ItemId


@dataclass(slots=True)
class Item:
    id: ItemId
    name: str
