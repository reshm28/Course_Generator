from app.application.use_cases.create_item import CreateItemInput, CreateItemUseCase
from app.infrastructure.repositories.in_memory_item_repository import InMemoryItemRepository


def test_create_item_use_case():
    repo = InMemoryItemRepository()
    use_case = CreateItemUseCase(repo)

    item = use_case.execute(CreateItemInput(name="test"))

    assert repo.get(item.id) is not None
    assert item.name == "test"
