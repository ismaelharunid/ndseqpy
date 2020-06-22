
from .ndsequence import NDSequence, ShapeInfo, iter_shape
from .ndmath import NDMATH_MIXIN


class NDList(NDSequence, list):
  
  def __init__(self, initializer, shape=None, itemtype=int, itemsize=1
      , **kwargs):
    shape_info = ShapeInfo()
    super().__init__(iter_shape(initializer, shape_info, itemtype), **kwargs)
    self._finalize(shape_info, shape, itemtype, itemsize, itemtype, **kwargs)

NDMathList = type("NDMathList", (NDList,), NDMATH_MIXIN)
