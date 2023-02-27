import sys
from numbers import Number
from collections import deque


zero_depth_bases = (str, bytes, Number, range, bytearray)
iteritems = 'items'


class Size:
    """Recursively iterate to sum size of object & members."""
    _seen_ids = set()

    def __init__(self):
        sys.setrecursionlimit(2000)

    def __del__(self):
        sys.setrecursionlimit(998)

    def get(self, obj):
        obj_id = id(obj)
        if obj_id in self._seen_ids:
            return 0
        self._seen_ids.add(obj_id)
        size = sys.getsizeof(obj)
        if isinstance(obj, zero_depth_bases):
            pass  # bypass remaining control flow and return
        elif isinstance(obj, (tuple, list, set, deque)):
            size += sum(self.get(i) for i in obj)
        elif isinstance(obj, map) or hasattr(obj, iteritems):
            size += sum(self.get(k) + self.get(v) for k, v in getattr(obj, iteritems)())
        # Check for custom object instances - may subclass above too
        if hasattr(obj, '__dict__'):
            size += self.get(vars(obj))
        if hasattr(obj, '__slots__'):  # can have __slots__ with __dict__
            size += sum(self.get(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s))
        return size
