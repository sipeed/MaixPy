Scan the qrcode in camera screen and send the result of the qrcode from the communication module(Default is uart).

Example:

1. run the program
```shell
./main.py
```

2. Put the qrcode in the camera, and you will see the qrcode is marked by a rectangle.
3. Check the data sent by the communication module. Use `app.get_sys_config_kv("comm", "method")` to get the protocol used by the current communication module. Default protocol is `uart`, baudrate is `115200`.
```shell
# uart data
AA CA AC BB 0D 00 00 00 E1 05 31 32 33 34 35 36 37 38 39 1A 15
# 31 32 33 34 35 36 37 38 39： means the qrcode is "123456789"
```
