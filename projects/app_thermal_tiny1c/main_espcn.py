from maix import display, app, image, camera, time, nn, tensor
import numpy as np
import cv2
import time
import inspect

width = 256
height = 192

disp = display.Display()
print("display init done")
print(f"display size: {disp.width()}x{disp.height()}")
cam = camera.Camera(disp.width(), disp.height())    # Manually set resolution
                                                    # | 手动设置分辨率

img = cam.read()
disp.show(img)
factor = 3
if factor == 2:
    xNmodel = nn.NN("./espcn_x2.mud") # 1x192x256x1 -> 1x384x512x1
elif factor == 3:
    xNmodel = nn.NN("./espcn_x3.mud") # 1x192x256x1 -> 1x384x768x1
else:
    raise RuntimeError("Unsupported factor")

while not app.need_exit():
    scr = np.zeros((disp.height(), disp.width(), 3), dtype=np.uint8)

    # 创建 768x512 的画布
    canvas = np.zeros((height*factor, width*factor*2), dtype=np.uint8)

    img = cam.read()
    img_bgr = image.image2cv(img, ensure_bgr=True, copy=True)
    img_bgr = cv2.resize(img_bgr, (width, height))
    I_img_np = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    print(I_img_np.shape, I_img_np.dtype)

    # 1. 记录开始时间
    a0 = time.perf_counter()

    I_img = image.cv2image(I_img_np)
    xN_tensors = xNmodel.forward_image(I_img)
    # print(xN_tensors.keys())
    xN_tensor = xN_tensors['19']
    xN_O_img_np = tensor.tensor_to_numpy_float32(xN_tensor, copy = False)
    xN_O_img_np = xN_O_img_np.astype(np.uint8)
    xN_O_img_np = xN_O_img_np.reshape((height*factor, width*factor))
    print(xN_O_img_np.shape, xN_O_img_np.dtype)

    xN_I_img_np = cv2.resize(I_img_np, (width*factor, height*factor))
    # print(xN_I_img_np.shape, xN_I_img_np.dtype)

    # 上下拼接
    canvas = np.vstack([xN_I_img_np, xN_O_img_np])
    edge_min =  min(disp.height(), disp.width())
    canvas = cv2.resize(canvas, (edge_min, edge_min))
    canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)

    scr[:edge_min, :edge_min, ...] = canvas

    img = image.cv2image(scr)

    print(f"{inspect.currentframe().f_lineno}: 耗时: {time.perf_counter() - a0:.6f} 秒")

    disp.show(img)
