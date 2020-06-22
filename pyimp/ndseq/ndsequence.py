

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
shape2strides = lambda shape: reduce(lambda a, c: tuple(b*c for b in a)+(1,), shape, ())
flatten_index = lambda index, strides, shape: \
    sum((i%n)*s for (i,s) in zip(index,strides,shape))
expand_index = lambda index, strides, shape: \
    tuple((index//s)%n for (s,n) in zip(strides,shape))


class SequenceView(Sequence):
  """
  Return a read-only view of the sequence object *target*.
  """
  
  _target   = None
  _class    = None
  
  def __init__(self, target, use_class=None):
    if use_class is None: use_class = target.__class__
    self._target = target
    self._class = use_class
  
  def __getitem__(self, index):
    return self._class.__getitem__(self._target, index)
  
  def __setitem__(self, index, value):
    return self._class.__setitem__(self._target, index, value)
  
  def __len__(self):
    return self._class.__len__(self._target)


def reshape(items, shape, itemtype=None, cls=None):
  if itemtype is None:
    itemtype = items.itemtype if hasattr(items, "itemtype") else int
  if cls is None: cls = type(items)
  shape_info = ShapeInfo()
  return cls(iter_shape(items, shape_info), shape=shape)


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
  shape_info.strides = shape2strides(shape)
  shape_info.types  = tuple(types)
  shape_info.n_items = n_items
  shape_info.volume = product(shape) if shape else 0
  shape_info.irregular = shape_info.n_items != shape_info.volume


def ShapeInfo__init__(self, n_items=0, volume=0, irregular=False
    , shape=(), strides=[], types=()):
  self.n_items = n_items
  self.volume = volume
  self.irregular = irregular
  self.shape = shape
  self.strides = strides
  self.types = types

ShapeInfo__init__.__name__ = "__init__"

ShapeInfo  = type( "ShapeInfo", (object,), 
    { "n_items":    None    # item count
    , "volume":     None    # shape volume
    , "irregular":  None    # inconsistant axes sizes
    , "shape":      []      # the shape
    , "strides":    []      # the strides of each axis
    , "types":      []      # item types
    , "__init__":   ShapeInfo__init__
    , "__repr__":   lambda s: "ShapeInfo({:s})" \
        .format(', '.join("{:s}={:s}".format(k, repr(getattr(s, k))) \
        for k in ("n_items", "volume", "irregular", "shape", "strides" \
        , "types")))
    } )


class NDSequence(object):
  
  _items    = None
  _shape    = None
  _strides  = None
  _bytestrides = None
  _itemtype = None
  _itemsize = None
  _casttype = None
  _view     = None
  
  @property
  def casttype(self):
    return self._casttype
  
  @property
  def flat(self):
    return self._view
  
  @property
  def itemsize(self):
    return self._itemsize
  
  @property
  def itemtype(self):
    return self._itemtype
  
  @property
  def shape(self):
    return self._shape
  
  @property
  def strides(self):
    return self._strides
  
  @property
  def itemstrides(self):
    return self._strides
  
  @property
  def bytestrides(self):
    return self._bytestrides
  
  def _finalize(self, shape_info, shape, itemtype, itemsize, casttype
      , **kwargs):
    if casttype is None:
      casttype = itemtype
    if shape_info.irregular:
      print('irregular', shape_info.irregular)
    if shape and shape != shape_info.shape:
      #print('shape', shape, shape_info.shape)
      strides = shape2strides(shape)
    else:
      shape = shape_info.shape
      strides = shape_info.strides
    # get the basest base
    base = self.__class__
    while issubclass(base, NDSequence):
      base = base.__base__
    bytesize = 4    # just anyold number but really this needs to be cross 
                    # compatible wither wahtever the base class is.  No way 
                    # to do this maybe.
    bytestrides = tuple(s*bytesize for s in strides)
    self._items     = self
    self._shape     = shape
    self._strides   = strides
    self._bytestrides   = bytestrides
    self._itemtype  = itemtype
    self._itemsize  = itemsize
    self._casttype  = casttype
    self._view      = SequenceView(self._items, base)
  
  def __cast__(self, value):
    return self._casttype( value )
  
  def __value__(self, value):
    return self._itemtype( value )
  
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
  
  def transpose(self, axes=-1):
    return self.swapaxes( (0, axes % len(self.shape)) )
  
  def swapaxis(self, *axis_pairs):
    strides, shape = self.strides, self.shape
    n_self, n_shape  = len(self._items), len(shape)
    remap = list(range(n_shape))
    for (i0, i1) in axis_pairs:
      remap[i0], remap[i1] = (remap[i1], remap[i0])
    restrides = tuple(strides[i] for i in remap)
    reshape = tuple(shape[i] for i in remap)
    indexes = tuple(flatten_index(i, restrides, reshape) for i in range(n_self))
    return type(self)(self.flat[indexes], shape=reshape, itemtype=self.itemtype)

