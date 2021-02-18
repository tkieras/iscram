import abc

from iscram.domain.model import SystemGraph


class RepositoryError(RuntimeError):
    pass


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, sg: SystemGraph, resource_identifier: str):
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, sg: SystemGraph, resource_identifier: str, data):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, sg: SystemGraph, resource_identifier: str):
        raise NotImplementedError


class FakeRepository(AbstractRepository):
    def __init__(self):
        self.storage = {}

    def get(self, sg: SystemGraph, resource_identifier: str):
        try:
            result = self.storage[sg][resource_identifier]
        except KeyError:
            raise RepositoryError

        return result

    def put(self, sg: SystemGraph, resource_identifier: str, data):
        if sg not in self.storage:
            self.storage[sg] = {}

        self.storage[sg][resource_identifier] = data

    def delete(self, sg: SystemGraph, resource_identifier: str):
        try:
            self.storage[sg][resource_identifier]
        except KeyError:
            raise RepositoryError

        self.storage[sg].pop(resource_identifier)
