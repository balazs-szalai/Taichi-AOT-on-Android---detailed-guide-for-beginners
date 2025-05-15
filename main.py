# -*- coding: utf-8 -*-
"""
Created on Tue May 13 15:39:50 2025

@author: balazs
"""
import sys
sys.path.append('compile_kernel')

import numpy as np
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
message = 'fine'


from kivy.utils import platform
import sys

def traverse_filesystem(start_path):
    result = []
    for root, dirs, files in os.walk(start_path):
        for name in files:
            full_path = os.path.join(root, name)
            result.append(full_path)
    return "\n".join(result)


def find_file(orig_file):
    print(orig_file)
    search_paths = [
        '\\'.join(__file__.split('\\')[:-1]),
        os.environ.get('ANDROID_PRIVATE', ''),              # Usually /data/data/org.your.app/files
        '/data/data',                                       # App-specific directories
        '/data/app',                                        # APK-managed storage
        '/storage/emulated/0',                              # Shared storage
        os.getcwd()                                         # Current working dir
    ]
    result = []
    for start_path in search_paths:
        for root, dirs, files in os.walk(start_path):
            for name in files:
                full_path = os.path.join(root, name)
                result.append(full_path)
    
    which = []
    for f in result:
        if orig_file in f:
            which.append(f)
    return which

devices_list = []
try:
    import taichiAOT as tiaot
    from tiaotndarray import ndarray
    runtime = tiaot.ti_create_runtime(tiaot.TiArch.TI_ARCH_VULKAN, 0)
    module = tiaot.ti_load_aot_module(runtime, find_file('saved_aot.tcm')[0])
    print(find_file('saved_aot.tcm'))
    
    kernel_matmul = tiaot.ti_get_aot_module_kernel(module, 'matmul')
    
    n = 5
    def call():
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
        
        ret = c.numpy[0,0]
        
        del a, b, c
        
        return ret
    
    devices_list = tiaot.ti_get_available_archs()[1][:]
except Exception as e:
    message = str(e)


    

class MyWidget(BoxLayout):
    message = StringProperty("Press the button!")
    search = StringProperty(str(devices_list))

    def on_button_press(self):
        try:
            message = str(call())
        except Exception as e:
            message = str(e)
        self.message = message
    
    def on_enter(self):
        self.search = self.ids.textinput.text

class MyApp(App):
    def build(self):
        return MyWidget()

if __name__ == "__main__":
    MyApp().run()
