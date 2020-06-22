
from .ndsequence import NDSequence, ShapeInfo, iter_shape
from .ndmath import NDMATH_MIXIN

import array


PY2ATYPE = { str: 'b', int: 'l', float: 'f'}

def py2atype(pytype):
  if pytype in PY2ATYPE:
    return PY2ATYPE[pytype]

class NDArray(NDSequence, array.array):
  
  #_shape_info = None
  
  def __new__(cls, initializer, shape=None, itemtype=int, itemsize=1
      , casttype=None, **kwargs):
    shape_info = ShapeInfo()
    self = super().__new__(cls, py2atype(itemtype) or 'l' \
        , iter_shape(initializer, shape_info, itemtype), **kwargs)
    #self._shape_info = shape_info
    self._finalize(shape_info, shape, itemtype, itemsize, casttype, **kwargs)
    return self
  
  def __init__(self, initializer, shape=None, itemtype=int, itemsize=1
      , casttype=None, **kwargs):
    pass
    #super().__init__(iter_shape(initializer, shape_info, itemtype), **kwargs)
    #self._finalize(self._shape_info, shape, itemtype, itemsize, casttype, **kwargs)


NDMathArray = type("NDMathArray", (NDArray,), NDMATH_MIXIN)

