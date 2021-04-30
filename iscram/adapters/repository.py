import abc
from collections import OrderedDict

from iscram.domain.model import SystemGraph


class RepositoryLookupError(Exception):
    def __init__(self, message):
        self.message = message


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, obj):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, key):
        raise NotImplementedError


class FakeRepository(AbstractRepository):
    def __init__(self):
        self.storage = {}

    def get(self, key):
        return self.storage.get(key)

    def put(self, obj):
        self.storage[hash(obj)] = obj

    def delete(self, key):
        if key in self.storage:
            del self.storage[key]


class LRUCacheRepository(AbstractRepository):
    def __init__(self, capacity=20):
        self._storage = OrderedDict()
        self.capacity = capacity

    def _get(self, key):
        result = self._storage.get(key)
        if result is not None:
            self._storage.move_to_end(key)
        return result

    def _put(self, key, data):
        self._storage[key] = data
        self._storage.move_to_end(key)
        if len(self._storage) > self.capacity:
            self._storage.popitem(last=False)

    @classmethod
    def _make_key(cls, sg: SystemGraph, resource_identifier: str = None):
        if not resource_identifier:
            return sg.get_id()
        else:
            return str(hash(sg)) + "|" + str(hash(resource_identifier))

    def get(self, key):
        result = self._get(key)
        if result is None:
            raise RepositoryLookupError("Could not find object with key: " + key)
        return self._get(key)

    def put(self, sg: SystemGraph):
        self._put(LRUCacheRepository._make_key(sg), sg)

    def delete(self, key):
        if key in self._storage:
            del self._storage[key]

