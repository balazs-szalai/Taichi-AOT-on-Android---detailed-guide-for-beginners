# Correcting the TiArgumentValue struct
This is a critical change for correctly passing multiple arguments to taichi kernels. Taichi kernels expect arguments to have a TiArgument* type, that is an array of TiArgument structs. If the size of this struct does not align with the size that taichi_c_api.dll expects, passing multiple kernel arguments will fail silently.
By removing the TiTensor type from the TiArgumentValue struct, now the size aligns with what taichi_c_api.dll expects.
