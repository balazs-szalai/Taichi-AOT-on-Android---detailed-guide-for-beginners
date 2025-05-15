# -*- coding: utf-8 -*-
"""
Created on Sun May 11 14:42:28 2025

@author: balazs
"""
import sys
sys.path.append('..')

import taichiAOT as tiaot
import numpy as np
import ctypes


def compute_ndarray_size(dtype, shape, element_shape = ()):
    scalar_size = dtype.itemsize
    num_elements = np.prod(shape, dtype=int)
    element_volume = np.prod(element_shape, dtype=int) if element_shape else 1
    total_bytes = int(scalar_size * num_elements * element_volume)
    return total_bytes

def numpy_shape(shape, element_shape = ()):
    return tuple(shape) + tuple(element_shape)


class ndarray:
    def __init__(self, runtime, dtype, shape, element_shape = (), host_accessible = True):
        assert dtype in (np.float32, np.int32)
        if dtype == np.float32:
            ti_type_int = tiaot.TiDataType.TI_DATA_TYPE_F32
        else:
            ti_type_int = tiaot.TiDataType.TI_DATA_TYPE_I32
        argtype = tiaot.TiArgumentType.TI_ARGUMENT_TYPE_NDARRAY
        
        
        size = compute_ndarray_size(dtype, shape, element_shape)
        np_shape = numpy_shape(shape, element_shape)
        
        self.dtype = dtype
        self.shape = shape
        self.element_shape = element_shape
        self.runtime = runtime
        self.np_shape = np_shape
        
        allocate_info = tiaot.TiMemoryAllocateInfo(size = size, 
                                                   host_write = host_accessible, 
                                                   host_read = host_accessible, 
                                export_sharing = True, 
                                usage = tiaot.TiMemoryUsageFlags.TI_MEMORY_USAGE_STORAGE_BIT)
        
        self.memory = tiaot.ti_allocate_memory(runtime, allocate_info)
        
        ptr = tiaot.ti_map_memory(runtime, self.memory)
        
        ctypes_type = np.ctypeslib.as_ctypes_type(dtype)
        typed_ptr = ctypes.cast(ptr, ctypes.POINTER(ctypes_type))
        
        tidims = (ctypes.c_uint32 * 16)()
        tidims[0] = shape[0]
        tidims[1] = shape[1]
        tishape = tiaot.TiNdShape(dim_count = 2,
                                  dims = tidims)
        
        tidims = (ctypes.c_uint32 * 16)()
        for i, dim in enumerate(element_shape):
            tidims[i] = dim
        if tidims[0] == 0:
            tidims[0] = 1
        tielemshape = tiaot.TiNdShape(dim_count = len(element_shape) if element_shape else 1,
                                  dims = tidims)
        
        self.numpy = np.ctypeslib.as_array(typed_ptr, shape=np_shape)
        
        self.tiarray = tiaot.TiNdArray(memory = self.memory,
                                       shape = tishape,
                                       elem_shape = tielemshape,
                                       elem_type = ti_type_int)
        
        
        self.kernel_arg = tiaot.TiArgument(type = argtype, 
                                           value = tiaot.TiArgumentValue(ndarray = self.tiarray))
        
    
    def __del__(self):
        del self.numpy
        tiaot.ti_unmap_memory(self.runtime, self.memory)
        tiaot.ti_free_memory(self.runtime, self.memory)
    
    @classmethod
    def from_numpy(cls, runtime, np_array):
        ret = ndarray(runtime, np_array.dtype, np_array.shape)
        ret.numpy[...] = np_array[...]
        return ret
    
    def remap(self):
        del self.numpy
        tiaot.ti_unmap_memory(self.runtime, self.memory)
        
        ptr = tiaot.ti_map_memory(self.runtime, self.memory)
        
        ctypes_type = np.ctypeslib.as_ctypes_type(self.dtype)
        typed_ptr = ctypes.cast(ptr, ctypes.POINTER(ctypes_type))
        
        self.numpy = np.ctypeslib.as_array(typed_ptr, shape=self.np_shape)
        
        
        
        
        
        
        