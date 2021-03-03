import abc

from iscram.domain.model import SystemGraph


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
        if resource_identifier == "cutsets":
            key = sg.structure()
        else:
            key = sg

        try:
            result = self.storage[key][resource_identifier]
        except KeyError:
            result = None

        return result

    def put(self, sg: SystemGraph, resource_identifier: str, data):
        if resource_identifier == "cutsets":
            key = sg.structure()
        else:
            key = sg

        if key not in self.storage:
            self.storage[key] = {}

        self.storage[key][resource_identifier] = data

    def delete(self, sg: SystemGraph, resource_identifier: str):
        if resource_identifier == "cutsets":
            key = sg.structure()
        else:
            key = sg

        try:
            self.storage[key][resource_identifier]
        except KeyError:
            return None

        self.storage[key].pop(resource_identifier)
