# ndseqpy
Yet another n-dimensional sequence implementation with subclasses for list, bytearray, array.array and ctypes.


### example

  ```python
  >>> import ndseq as nd
  >>> ndba = nd.NDByteArray( ((0,1,2),(3,4,5),(6,7,8)) )
  >>> ndba[0,0]
  (0,)
  >>> ndba[:,0]
  (0, 3, 6)
  >>> ndba[0,:]
  (0, 1, 2)
  >>> ndba.flat[1:8]
  bytearray(b'\x01\x02\x03\x04\x05\x06\x07')
  >>> ndba[1,:] = (10,11,12)
  >>> ndba
  NDByteArray(b'\x00\x01\x02\n\x0b\x0c\x06\x07\x08')
  >>> ndba.flat[0:2]
  bytearray(b'\x00\x01')
  >>> ndba.flat[0:2] = (100,100)
  >>> ndba
  NDByteArray(b'dd\x02\n\x0b\x0c\x06\x07\x08')
  ```
