
from .ndsequence import NDimSequence, ShapeInfo, iter_shape

import array


class NDArray(NDimSequence, array.array):
  
  _shape_info = None
  
  def __new__(cls, initializer, shape=None, itemtype=int, itemsize=1
      , **kwargs):
    shape_info = ShapeInfo()
    self = super().__new__(cls, 'l', iter_shape(initializer, shape_info, int), **kwargs)
    self._shape_info = shape_info
    return self
  
  def __init__(self, initializer, shape=None, itemtype=int, itemsize=1
      , **kwargs):
    #shape_info = ShapeInfo()
    #super().__init__('l', iter_shape(initializer, shape_info, int), **kwargs)
    self._finalize(self._shape_info, shape, itemtype, itemsize, int, **kwargs)


