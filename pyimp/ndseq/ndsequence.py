

try:
  from collections.abc import *
  # AsyncGenerator, AsyncIterable, AsyncIterator, Awaitable, ByteString \
  # , Callable, Collection, Container, Coroutine, Generator, Hashable \
  # , ItemsView, Iterable, Iterator, KeysView, Mapping, MappingView \
  # , MutableMapping, MutableSequence, MutableSet, Reversible, Sequence \
  # , Set, Sized, ValuesView
except ImportError:
  from collections import Callable, Container, Counter, Hashable, ItemsView \
      , Iterable, Iterator, KeysView, Mapping, MappingView, MutableMapping \
      , MutableSequence, MutableSet, Sequence, Set, Sized \
      , ValuesView

import abc
from functools import reduce
import operator


issized     = lambda items: isinstance(items, Sized)
isindexable = lambda items: hasattr(items, '__getitem__')
isflat = lambda items: not any(isindexable(i) for i in items)
product = lambda items: reduce(lambda a, b: a*b, items)

def iter_shape(iterable, shape_info, force_type=None):
  if force_type:
    if not isinstance(force_type, type) and not callable(force_type):
      raise ValueError("force_type expects a type, class or callable, not {:s}" \
          .format(type(force_type).__name__))
  stack, shape, types = [], [], []
  stopped = False
  it, n_items, d_items = iter(iterable), 0, 0
  try:
    item = it.__next__()
    d_items += 1
    shape.append(d_items)
  except StopIteration:
    stopped = True
  while not stopped:
    if isinstance(item, Iterable):
      i_shape = len(stack)
      shape[i_shape] = max(shape[i_shape], d_items)
      stack.append( (it, d_items) )
      i_shape = len(stack)
      it, d_items = iter(item), 0
      if i_shape >= len(shape):
        shape.append(d_items)
      else:
        shape[i_shape] = max(shape[i_shape], d_items)
    else:
      n_items += 1
      if type(item) not in types:
        types.append(type(item))
      yield item if force_type is None else force_type(item)
    while True:
      try:
        item = it.__next__()
        d_items += 1
        break
      except StopIteration:
        i_shape = len(stack)
        shape[i_shape] = max(shape[i_shape], d_items)
        if i_shape == 0:
          stopped = True
          break
        it, d_items = stack.pop()
  else: # while not stopped:
    pass
  shape_info.shape = tuple(shape)
  shape_info.types  = tuple(types)
  shape_info.n_items = n_items
  shape_info.volume = product(shape) if shape else 0
  shape_info.irregular = shape_info.n_items != shape_info.volume


def ShapeInfo__init__(self, n_items=0, volume=0, irregular=False, shape=(), types=()):
  self.n_items = n_items
  self.volume = volume
  self.irregular = irregular
  self.shape = shape
  self.types = types
ShapeInfo__init__.__name__ = "__init__"

ShapeInfo  = type( "ShapeInfo", (object,), 
    { "n_items":    None    # item count
    , "volume":     None    # shape volume
    , "irregular":  None    # inconsistant axes sizes
    , "shape":      []      # the shape
    , "types":      []      # item types
    , "__init__":   ShapeInfo__init__
    , "__repr__":   lambda s: "ShapeInfo({:s})" \
        .format(', '.join("{:s}={:s}".format(k, repr(getattr(s, k))) \
        for k in ("n_items", "volume", "irregular", "shape", "types")))
    } )


class NDimSequence(object):
  
  _items    = None
  _shape    = None
  _itemtype = None
  _itemsize = None
  _casttype = None
  _strides  = None
  
  def _finalize(self, shape_info, shape, itemtype, itemsize, casttype
      , **kwargs):
    if shape_info.irregular:
      print('irregular', shape_info.irregular)
    if shape and shape != shape_info.shape:
      print('shape', shape, shape_info.shape)
    else:
      shape = shape_info.shape
    self._items     = self
    self._shape     = shape
    self._itemtype  = itemtype
    self._itemsize  = itemsize
    self._casttype  = casttype
    self._strides = reduce(lambda a, c: tuple(b*c for b in a)+(1,), (3,3,3), ())
  
  def __index__(self, key):
    """
    convert key into a tuple of individual indexes
    """
    lengths, strides = self._shape, self._strides
    if type(key) is not tuple:
      key = (key,)
    key += (slice(0,None,1),) * (len(lengths)-len(key))
    index, length = [0], len(self)
    #print(key)
    for (l, s, k) in zip(reversed(lengths), reversed(strides), reversed(key)):
      #print (l, s, k)
      if type(k) is int:
        k = slice(k, k+1, 1).indices(l)
      elif type(k) is slice:
        k = tuple(i for i in k.indices(l))
      elif k is Ellipsis:
        k = slice(0, None, 1).indices(l)
      elif k is None:
        k = (l, l+1, 1)
      else:
        print("bad", k)
        break
      index = tuple(i*s+j for i in range(*k) for j in index)
    else:
      return index
    return key
  
  def __delitem__(self, key):
    indexes = self.__index__(key)
    foo = super()
    return tuple(foo.__delitem__(i) for i in reversed(indexes))
  
  def __getitem__(self, key):
    indexes = self.__index__(key)
    foo = super()
    return tuple(foo.__getitem__(i) for i in indexes)
  
  def __setitem__(self, key, values):
    indexes = self.__index__(key)
    assert len(indexes) == len(values)
    foo = super()
    return tuple(foo.__setitem__(i, v) for (i, v) in zip(reversed(indexes), reversed(values)))

