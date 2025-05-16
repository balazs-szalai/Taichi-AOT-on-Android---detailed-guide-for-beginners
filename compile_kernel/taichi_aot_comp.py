# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 18:51:55 2024

@author: balazs
"""

import taichi as ti 
import numpy as np
ti.init(ti.vulkan)

@ti.kernel 
def matmul(a: ti.types.ndarray(ti.f32, 2), 
           b: ti.types.ndarray(ti.f32, 2), 
           c: ti.types.ndarray(ti.f32, 2)):
    n, m = a.shape
    m, p = b.shape
    
    for i, j in ti.ndrange(n, p):
        s = 0.0
        for k in range(m):
            s += a[i, k] * b[k, j]
        c[i, j] = s

@ti.kernel
def fill(a: ti.types.ndarray(ti.f32, 2),
         val: ti.f32):
    n, m = a.shape
    for i, j in ti.ndrange(n, m):
        a[i, j] = val


m = ti.aot.Module(arch = ti.vulkan)
m.add_kernel(matmul, name = 'matmul')
m.add_kernel(fill, name = 'fill')
m.archive(r'saved_aot.tcm')
