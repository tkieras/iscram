import abc
from collections import OrderedDict

from iscram.domain.model import SystemGraph


class RepositoryLookupError(Exception):
    def __init__(self, message):
        self.message = message


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, sg: SystemGraph, resource_identifier: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get_graph(self, sg_id: str) -> SystemGraph:
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, sg: SystemGraph, resource_identifier: str, data):
        raise NotImplementedError

    @abc.abstractmethod
    def put_graph(self, sg: SystemGraph):
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
            result = None

        return result

    def get_graph(self, sg_id: str) -> SystemGraph:
        return self.storage.get(sg_id)

    def put(self, sg: SystemGraph, resource_identifier: str, data):
        if sg not in self.storage:
            self.storage[sg] = {}

        self.storage[sg][resource_identifier] = data

    def put_graph(self, sg: SystemGraph):
        self.storage[sg.get_id()] = sg

    def delete(self, sg: SystemGraph, resource_identifier: str):
        try:
            self.storage[sg][resource_identifier]
        except KeyError:
            return None

        self.storage[sg].pop(resource_identifier)


class LRUCacheRepository(AbstractRepository):
    def __init__(self, capacity=20):
        self.storage = OrderedDict()
        self.capacity = capacity

    def _get(self, key):
        result = self.storage.get(key)
        if result is not None:
            self.storage.move_to_end(key)
        return result

    def _put(self, key, data):
        self.storage[key] = data
        self.storage.move_to_end(key)
        if len(self.storage) > self.capacity:
            self.storage.popitem(last=False)

    @classmethod
    def _make_key(cls, sg: SystemGraph, resource_identifier: str = None):
        if not resource_identifier:
            return sg.get_id()
        else:
            return str(hash(sg)) + "|" + str(hash(resource_identifier))

    def get(self, sg: SystemGraph, resource_identifier: str):
        return self._get(LRUCacheRepository._make_key(sg, resource_identifier))

    def put(self, sg: SystemGraph, resource_identifier: str, data):
        self._put(LRUCacheRepository._make_key(sg, resource_identifier), data)

    def delete(self, sg: SystemGraph, resource_identifier: str):
        if key := LRUCacheRepository._make_key(sg, resource_identifier) in self.storage:
            del self.storage[key]

    def get_graph(self, sg_id: str) -> SystemGraph:
        sg = self._get(sg_id)
        if sg is None:
            raise RepositoryLookupError("No system graph found with id: " + sg_id)
        return sg

    def put_graph(self, sg: SystemGraph):
        self._put(LRUCacheRepository._make_key(sg), sg)
