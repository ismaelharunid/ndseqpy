
from .ndsequence import NDSequence, ShapeInfo, iter_shape
from .ndmath import NDMATH_MIXIN


class NDByteArray(NDSequence, bytearray):
  
  def __init__(self, initializer, shape=None, itemtype=int, itemsize=1
      , casttype=None, **kwargs):
    shape_info = ShapeInfo()
    super().__init__(iter_shape(initializer, shape_info, itemtype), **kwargs)
    self._finalize(shape_info, shape, itemtype, itemsize, casttype, **kwargs)

NDMathByteArray = type("NDMathByteArray", (NDByteArray,), NDMATH_MIXIN)
