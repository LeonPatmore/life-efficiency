from typing import Generic, TypeVar


class RepositoryImplementation:

    def __init__(self, object_type: type):
        self.object_type = object_type

    def add(self, item: object) -> object:
        raise NotImplementedError

    def get_all(self) -> list:
        raise NotImplementedError

    def get(self, item_id: str):
        raise NotImplementedError

    def remove(self, item_id: str):
        raise NotImplementedError

    def update(self, item_id: str, attribute: str, val):
        raise NotImplementedError


# noinspection PyTypeChecker
repository_implementation: type(RepositoryImplementation) = RepositoryImplementation


T = TypeVar("T")


class Repository(RepositoryImplementation, Generic[T]):

    def __init__(self, object_type: type(T)):
        super().__init__(object_type)
        self.repository_implementation = repository_implementation(object_type)

    def add(self, item: T) -> T:
        return self.repository_implementation.add(item)

    def get_all(self) -> list[T]:
        return self.repository_implementation.get_all()

    def get(self, item_id: str) -> T:
        return self.repository_implementation.get(item_id)

    def remove(self, item_id: str):
        self.repository_implementation.remove(item_id)

    def update(self, item_id: str, attribute: str, val):
        self.repository_implementation.update(item_id, attribute, val)
