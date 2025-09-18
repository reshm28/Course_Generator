from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class ItemId:
    value: str

    @staticmethod
    def new() -> "ItemId":
        return ItemId(value=str(uuid.uuid4()))
