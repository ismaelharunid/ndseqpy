
from .ndsequence import NDimSequence, ShapeInfo, iter_shape


class NDList(NDimSequence, list):
  
  def __init__(self, initializer, shape=None, itemtype=int, itemsize=1
      , **kwargs):
    shape_info = ShapeInfo()
    super().__init__(iter_shape(initializer, shape_info, int), **kwargs)
    self._finalize(shape_info, shape, itemtype, itemsize, int, **kwargs)

