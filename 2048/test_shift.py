import numpy as np

arr = np.array([1, 2], dtype=np.uint16)
val = arr[1]
print(type(val))
print(val << 16)
