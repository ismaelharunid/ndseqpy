

import operator, math
from .ndsequence import Iterable, NDSequence, ShapeInfo \
    , iter_shape, reshape, flatten_index, expand_index


_can_binaryop = lambda ashape,n_ashape,bshape,n_bshape: \
    n_ashape >= n_bshape \
    and all(a >= b and a % b == 0 \
    for (a,b) in zip(ashape[-n_bshape:], bshape))
can_binaryop = lambda ashape,bshape: \
    _can_binaryop(ashape,len(ashape),bshape,len(bshape))



def make_binaryop(op, item_type=None, name=None):
  if item_type is None:
    item_type = lambda v: v
  if name is None:
    name = op.__name__
  def binaryop(a, operand):
    ashape, astrides = a.shape, a.strides
    if isinstance(operand, NDSequence):
      b, bshape, bstrides = operand.flat, operand.shape, operand.strides
    else:
      shape_info = ShapeInfo()
      b = tuple(iter_shape((operand if isinstance(operand, Iterable) \
              else (operand,)), shape_info))
      #print(operand, shape_info)
      bshape, bstrides = shape_info.shape, shape_info.strides
    n_ashape, n_bshape = len(ashape), len(bshape)
    #if n_ashape >= n_bshape \
    #    and all(na >= nb and na % nb == 0 \
    #    for (na,nb) in zip(ashape[-n_bshape:], n_bshape)):
    if _can_binaryop(ashape,n_ashape, bshape,n_bshape):
      na, nb = len(a), len(b)   # the flat length of each
      #print(len(astrides), astrides, len(bstrides), bstrides)
      if nb == 1 or astrides[-1] == bstrides[-1]:
        # do it the easy way if we can
        rit = (item_type(op(a.flat[i], b[i%nb])) for i in range(na))
      else:
        rit = (item_type(op(a.flat[index], b[flatten_index(index, bstrides, bshape)])) \
            for index in (expand_index(i, astrides, ashape) for i in range(na)))
      return type(a)(rit, ashape, a.itemtype)
    raise ValueError("operands could not be broadcast together with shapes " \
        "{:s} {:s}".format(repr(ashape), repr(bshape)))
  binaryop.__name__ = name
  return binaryop

def make_binaryops_many(ops_many, item_type=None, lib=None):
  op_pairs = tuple((op, getattr(lib, op)) if lib and type(op) is str else \
      (op.__name__, op) for op in ops_many)
  return dict((name, make_binaryop(op, item_type, name)) \
      for (name, op) in op_pairs)

BINARYOPERATOR_OPS = ("__add__", "__and__", "__eq__" \
    , "__floordiv__", "__ge__", "__gt__", "__le__", "__lshift__", "__lt__" \
    , "__mod__", "__mul__", "__ne__", "__or__", "__pow__", "__rshift__" \
    , "__sub__", "__truediv__", "__xor__")
BINARYMATH_MIXIN = make_binaryops_many(BINARYOPERATOR_OPS, lib=operator)
# , "__divmod__" is not included in operators so we have to add seperatly, 
# however it produces 2 results so it's a bit strange.  We have to decide
# how sequences deal with a 2-tuple result.  Problable it should just produce
# to ndsequences of the same shape.

def make_unaryop(op, item_type=None, name=None):
  if item_type is None:
    item_type = lambda v: v
  if name is None:
    name = op.__name__
  def unaryop(a):
    ashape, astrides = a.shape, a.strides
    rit = (item_type(op(a.flat[i][0])) for i in range(na))
    return type(a)(rit, ashape, a.itemtype)
  unaryop.__name__ = name
  return unaryop

def make_unaryops_many(ops_many, item_type=None, lib=None):
  op_pairs = tuple((op, getattr(lib, op)) if lib and type(op) is str else \
      (op.__name__, op) for op in ops_many)
  return dict((name, make_unaryop(op, item_type, name)) \
      for (name, op) in op_pairs)

UNARYOPERATOR_OPS = ("__abs__", "__hash__", "__invert__", "__neg__" \
    , "__pos__")
UNARYMATH_OPS = ("ceil", "floor")
UNARYMATH_MIXIN = make_unaryops_many(UNARYOPERATOR_OPS, lib=operator)
UNARYMATH_MIXIN.update( make_unaryops_many(UNARYMATH_OPS, lib=math) )


def ndmatmul(left, right):
  a = left.flat
  ashape, astrides = left.shape, left.strides
  if isinstance(right, NDSequence):
    b, bshape, bstrides = right.flat, right.shape, right.strides
  else:
    shape_info = ShapeInfo()
    b = tuple(iter_shape((right if isinstance(right, Iterable) \
            else (right,)), shape_info))
    #print(right, shape_info)
    bshape, bstrides = shape_info.shape, shape_info.strides
  n_ashape, n_bshape = len(ashape), len(bshape)
  if n_ashape != n_bshape:
    raise ValueError("operands could not be broadcast together with shapes " \
        "{:s} {:s}".format(repr(ashape), repr(bshape)))
  if n_ashape != 2:
    raise NotImplementedError("Please implement 3+ dimension matmul")
  ra,ca = ashape
  rb,cb = bshape
  return type(left)((sum(a[i+k*ca]*b[j+i*cb] for i in range(ca)) \
      for k in range(ra) for j in range(cb)), shape=(cb, ra) \
      , itemtype=left.itemtype)

MATMATH_OPERATORS = ("__matmul__",)
MATMATH_MIXIN = \
    { "__matmul__": ndmatmul
    , "matmul": ndmatmul
    }

NDMATH_MIXIN = {}
NDMATH_MIXIN.update( BINARYMATH_MIXIN )
NDMATH_MIXIN.update( UNARYMATH_MIXIN )
NDMATH_MIXIN.update( MATMATH_MIXIN )

