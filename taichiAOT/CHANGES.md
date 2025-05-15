# Corrections and patches
This is a copy from the repository https://github.com/smoothie-ws/TaichiAOT-Python-API
## TiArgument fix
This is a critical change for correctly passing multiple arguments to taichi kernels. Taichi kernels expect arguments to have a TiArgument* type, that is an array of TiArgument structs. If the size of this struct does not align with the size that taichi_c_api.dll expects, passing multiple kernel arguments will fail silently.
By removing the TiTensor type from the TiArgumentValue struct, now the size aligns with what taichi_c_api.dll expects.
## Added dynamic loading of the Taichi C API library
In the _api_loader.py a bigger path finder is added since on Android the libtaichi_c_api.so won't necesserily be in the currently accessible paths. This could definitely be done better if someone knows how Android file system works, but it gets the job done.
