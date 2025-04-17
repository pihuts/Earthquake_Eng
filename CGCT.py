
import numpy as np

asd = [0,6,5,6,5,6,5,6,5]* 9 
span_list = np.array(asd).reshape(9,9).astype(np.float64)  # left to right
span_list_cum = np.cumsum(span_list, axis=1)  # left to right
asd = [0,5,5,5,5,6,6,6,6] * 9
height_list = np.array(asd).reshape(9,9).T.astype(np.float64)   # left to right
height_list_cum = np.cumsum(height_list, axis=0)  # bot to top
length_list = np.full_like(span_list, 0.5)  # left to right
width_list = np.full_like(span_list, 0.5)  # left to right
array3d = np.array([span_list_cum, height_list_cum, length_list, width_list])
array3d[:,:4,:2] = np.NAN
array3d[:,-2:,-2:] = np.NAN

print(array3d)