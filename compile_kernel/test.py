# -*- coding: utf-8 -*-
"""
Created on Sun May 11 13:00:59 2025

@author: balazs
"""
import sys
sys.path.append('..')

import taichiAOT as tiaot
from tiaotndarray import ndarray
import numpy as np

runtime = tiaot.ti_create_runtime(tiaot.TiArch.TI_ARCH_VULKAN, 0)
module = tiaot.ti_load_aot_module(runtime, 'saved_aot.tcm')

kernel_matmul = tiaot.ti_get_aot_module_kernel(module, 'matmul')
fill = tiaot.ti_get_aot_module_kernel(module, 'fill')

n = 200
a = ndarray(runtime, np.float32().dtype, (n, n))
b = ndarray(runtime, np.float32().dtype, (n, n))
c = ndarray(runtime, np.float32().dtype, (n, n))

argument_array = tiaot.TiArgument * 3
args = argument_array()

args[0] = a.kernel_arg
args[1] = b.kernel_arg
args[2] = c.kernel_arg

tiaot.ti_launch_kernel(runtime, fill, 2, 
                       (tiaot.TiArgument * 2)(a.kernel_arg, 
                                              tiaot.TiArgument(
                                                  tiaot.TiArgumentType.TI_ARGUMENT_TYPE_F32, 
                                                  tiaot.TiArgumentValue(f32 = 1.5))))
tiaot.ti_launch_kernel(runtime, fill, 2, 
                       (tiaot.TiArgument * 2)(b.kernel_arg, 
                                              tiaot.TiArgument(
                                                  tiaot.TiArgumentType.TI_ARGUMENT_TYPE_F32, 
                                                  tiaot.TiArgumentValue(f32 = 2.5))))


tiaot.ti_launch_kernel(runtime, kernel_matmul, len(args), args)
tiaot.ti_wait(runtime)

print(a.to_numpy()[0,0])
print(b.to_numpy()[0,0])
print(c.to_numpy()[0,0])

del a, b, c
