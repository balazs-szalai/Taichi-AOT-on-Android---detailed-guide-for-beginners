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

n = 200
a = ndarray.from_numpy(runtime, np.random.random((n, n)).astype(np.float32))
b = ndarray.from_numpy(runtime, np.random.random((n, n)).astype(np.float32))
c = ndarray(runtime, np.float32().dtype, (n, n))

argument_array = tiaot.TiArgument * 3
args = argument_array()

args[0] = a.kernel_arg
args[1] = b.kernel_arg
args[2] = c.kernel_arg

tiaot.ti_launch_kernel(runtime, kernel_matmul, len(args), args)
tiaot.ti_wait(runtime)

print(a.numpy[0,0])
print(b.numpy[0,0])
print(c.numpy[0,0])

del a, b, c
