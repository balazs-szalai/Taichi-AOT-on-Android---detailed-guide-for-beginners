# A complete guide for beginners to deploy Taichi kernels to android
The Taichi's python runtime and JIT is not really Android friendly. But the Taichi C API and Taichi AOT are also not trivial to use. In this guide we will:
1. Compile a Taichi kernel with its AOT module and load it from Python.
2. Cross compile the Taichi C API shared library for arm64 architecture.
3. Writing a simple Kivy app which loads and uses the  AOT compiled Taichi kernel.
4. Build this app for Android using Buildozer.
First you should set up the Linux environment then set up Buildozer and try to build the app, this will download all the necessary android build tools, then you can try crosscompiling the Taichi C API for Android if necessary.

## Compile a Taichi kernel with its AOT module and load it from Python
For this we will use the Python wrapper for the Taichi C API from https://github.com/smoothie-ws/TaichiAOT-Python-API and make same small but important changes to this package to make it work. 
The changes made are outlined in [taichiAOT/CHANGES.md](taichiAOT/CHANGES.md). In the file [compile_kernel/taichi_aot_comp.py](compile_kernel/taichi_aot_comp.py) we compile a simple matrix multiplication kernel just for testing purposes. This has to be compiled for Vulkan since Taichi AOT only really support Vulkan. The compiled module is saved in the [compile_kernel](compile_kernel)/saved_aot.tcm file. By running [compile_kernel/test.py](compile_kernel/test.py) we can check if everything is running fine. 
The file [compile_kernel/tiaotndarray.py](compile_kernel/tiaotndarray.py) we defined an easy-to-use ndarray wrapper for the Taichi ndarray. This is useful since the Taichi C API only allows for memory allocation and mapping the allocated device memory to host accessible space, but this can be wrapped into a Numpy array, and this small class also handles the creation of TiArgument for the ti_kernel_launch function.

## Set up a Linux environment
We can first install every necessary packages using apt and pip:

    sudo apt update
    sudo apt install python3-venv python3-pip openjdk-17-jdk \
      git zip unzip build-essential libssl-dev zlib1g-dev \
      libffi-dev libncurses5 libstdc++6 curl autoconf automake libtool cmake
    python3 -m venv buildozer-env
    source buildozer-env/bin/activate
    pip install --upgrade pip wheel setuptools
    pip install buildozer scikit-build
    pip3 install --upgrade Cython==0.29.33 virtualenv

This installs all the essential packages, creates a clean virtual environment for buildozer, activates it and pip install all the neseccary python packages. These steps will be shown again later but here they are gathered in one place for completeness. For building libtaichi_c_api.so from source you need cmake 3.17 or newer.

## Cross compile the Taichi C API shared library for arm64
Although not well documented in the Taichi docs, the raw Taichi repositor from https://github.com/taichi-dev/taichi allows for straightforward compilation of the C API using CMake. To make it work on Android we need to compile the Taichi C API with Vulkan but without LLVM (you could compile it with LLVM, but I could not make it work due to some error in the CMake which I don't understand, but it's also not necessary).  These stepps need o be done in Linux, I did it in WSL. Which we will set up first with a few useful (or essential) packages:

    sudo apt update
    sudo apt install python3-venv python3-pip openjdk-17-jdk \
      git zip unzip build-essential libssl-dev zlib1g-dev \
      libffi-dev libncurses5 libstdc++6 curl autoconf automake libtool

Let's assume you have git accessible from Bash (after the setup you should have). Now clone the Taichi repository, open it, initialize submodules and create a folder for the android build:
    
    git clone https://github.com/taichi-dev/taichi
    cd taichi
    git submodule update --init --recursive
    mkdir android_build
    cd android_build
You might also need to install skbuild:

    pip install scikit-build

Then aquire an Android NDK for arm compilation. You can either download it form the internet or use the NDK coming with Buildozer (therefore it is recommended to set up Buildozer now and try to build it). Create a variable for the NDK root folder for example:

    export ANDROID_NDK_ROOT=$HOME/.buildozer/android/platform/android-ndk-r25b
You should use your own file path for the NDK root folder.

Let's assume you have a working CMake environment, if not, you can install the necessary components through:

    sudo apt install cmake
 Inside the android_build folder you set up the CMake as:

     cmake .. \
      -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK_ROOT/build/cmake/android.toolchain.cmake \
      -DANDROID_ABI=arm64-v8a \
      -DANDROID_NATIVE_API_LEVEL=29 \
      -DANDROID_STL=c++_static \
      -DCMAKE_BUILD_TYPE=Release \
      -DTI_WITH_LLVM=OFF \
      -DTI_WITH_OPENGL=OFF \
      -DTI_WITH_VULKAN=ON
This sets up the make process for Android SDK 29 (it might be necessary to also aquire it, I'm not sure) without LLVM but with Vulkan. Now you can build it:

    cmake --build . --target taichi_c_api

After the build process is finished, you should find libtaichi_c_api.so in the current (that is android_build) folder. This repository does contain a precompiled version in the libs/android-v8 folder.

## Writing a simple Kivy app for testing
This is the easy part, a simple Kivy app is contained in the main.py file with a myapp.kv file. This does nothing much, just loads the libtaichi_c_api.so, in the first textbox it shows the accesible devices (a 1 means that at least one Vulkan supported device is found). If you press the button it will allocate 3 ndarrays using the Taichi C API and using our custom testing modul and matrix multiplication kernel it multiplies 2 of the, the result is in the thrird, if a seemingly random number appears in the second textbox, the app runs correctly and executes the custom kernel on the Vulkan device.

## Building the app for Android
This is mostly just standard Buildozer compilation, which of course only works in Linux. 
That is, we first create a new clean python environment for buildozer:

    python3 -m venv buildozer-env
    source buildozer-env/bin/activate
    pip install --upgrade pip wheel setuptools

    pip install buildozer cython
    pip3 install --upgrade Cython==0.29.33 virtualenv

You should now clone this repository:

    git clone https://github.com/balazs-szalai/Taichi-AOT-on-Android---detailed-guide-for-beginners
    cd Taichi-AOT-on-Android---detailed-guide-for-beginners
And initialize buildozer:

    buildozer init

This creates a buildozer.spec file, which needs to be edited. You should change the included extentions:

    source.include_exts = py,png,jpg,kv,atlas,tcm,so
edit the requirements:

    requirements = python3,kivy,numpy
you should schange the targeted architectures to just arm64 (since that's what we built libtaichi_c_api.so):

    android.archs = arm64-v8a
set the Android api level to what you specified in the building of libtaichi_c_api.so

    android.api = 29
Optionally you might want to set the NDK path to what you used at building libtaichi_c_api.so, but Buildozer should find it automatically. Also, it might or might not be necessary to create an .xml file to specify the usage of Vulkan compute

    printf '<uses-feature \n    android:name="android.hardware.vulkan.compute" \n    android:required="true" />\n' > vulkan_feature.xml
and specify this in buildozer.spec

    android.extra_manifest_xml = vulkan_feature.xml
Additionally, you should also create an assets folder and add the saved_aot.tcm to it and create a libs/android-v8 folder and add libtaichi_c_api.so to it then set it up in the buildozer.spec as

    android.add_assets = assets
    android.add_libs_arm64_v8a = libs/android-v8/*.so

Now everything should be set up for building the app:

    buildozer -v android debug
and after the lengthy build process a bin folder should appear with the compiled android .apk file. Our work is complete, we can install this apk to and Android device, the file I built with this method can be downloaded from https://github.com/balazs-szalai/Taichi-AOT-on-Android---detailed-guide-for-beginners/releases/download/v1.0/myapp-0.1-arm64-v8a-debug.apk. 

## Thought for the end
We solved a lot of different issues: we made Taichi AOT work in pure Python, compiled the Taichi C API to Android and successfully built an app using these components for Android.

However, it is important to point out that I could not make the app not crash on a real Android device (I tried my own phone with Android 12 and my brother's with Android 15). But the code itself should work since and emulated Android 14 device from Android Studio did run the app without issues.

