from maix import display, app, image
disp = display.Display()
print("display init done")
print(f"display size: {disp.width()}x{disp.height()}")

######################################
import cv2
import numpy as np
# 画布大小
w, h = disp.width(), disp.height()
# 坐标中心
center = np.array([w//2, h//2])

# 构造旋转矩阵: 把原始Z轴(0,0,1)转到acc_norm方向
def rotation_matrix_from_vectors(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    if s < 1e-8:
        return np.eye(3)
    kmat = np.array([[    0, -v[2],  v[1]],
                     [ v[2],     0, -v[0]],
                     [-v[1],  v[0],     0]])
    return np.eye(3) + kmat + kmat @ kmat * ((1-c)/(s**2))

# 原始坐标轴单位向量
axes = {
    'X': np.array([1,0,0]),
    'Y': np.array([0,1,0]),
    'Z': np.array([0,0,1])
}
colors = {'X': (0,0,255), 'Y': (0,255,0), 'Z': (255,0,0)}

# 投影到画布（简单正交投影，忽略Z）
def project(vec):
    scale = 150
    x = int(center[0] + vec[0]*scale)
    y = int(center[1] - vec[1]*scale)
    return (x, y)
######################################

import time
import lsm6dsow
imu = lsm6dsow.Lsm6dsow()
imu.set_acc_odr(imu.ODR_TABLE[7])
imu.set_gyro_odr(imu.ODR_TABLE[7])
imu.set_acc_scale(imu.ACC_SENS_TABLE[0])
imu.set_gyro_scale(imu.GYRO_SENS_TABLE[0])

count = 0
duration = 180.0  # 统计180秒
start = time.time()
while not app.need_exit():
    # 新建画布
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 0

    remain_time = start + duration - time.time()
    if remain_time < 0:
        break
    else:
        cv2.putText(canvas, f"Auto exit after {remain_time:.1f}s", (20,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

    # 同时采样加速度和陀螺仪
    upd, acc_gyro_vals = imu.read()
    acc_vals = acc_gyro_vals[0]
    gyro_vals = acc_gyro_vals[1]
    if upd:
        # print("ACC(m/s²):", " ".join("{:8.4f}".format(x) for x in acc_vals),
        #         "GYRO(°/s):", " ".join("{:8.4f}".format(x) for x in gyro_vals))
        count += 1

    # 1. 示例加速度（m/s²）和角速度（°/s），请替换为你的实际数据
    acc = np.array(acc_vals)    # X, Y, Z
    gyro = np.array(gyro_vals)      # X, Y, Z

    # 2. 归一化加速度作为“新Z轴方向”
    acc_norm = acc / np.linalg.norm(acc) if np.linalg.norm(acc) > 1e-5 else np.array([0,0,1])

    # 3. 计算旋转后的坐标轴
    R = rotation_matrix_from_vectors(np.array([0,0,1]), acc_norm)
    rot_axes = {k: R @ v for k,v in axes.items()}

    # 4. 画三轴
    for k in ['X', 'Y', 'Z']:
        tip = project(rot_axes[k])
        cv2.arrowedLine(canvas, tuple(center), tip, colors[k], 3, tipLength=0.10)
        cv2.putText(canvas, k, tip, cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors[k], 2)

    # 5. 显示数值
    cv2.putText(canvas, f"acc: [{acc[0]:.2f}, {acc[1]:.2f}, {acc[2]:.2f}]", (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    cv2.putText(canvas, f"gyro: [{gyro[0]:.2f}, {gyro[1]:.2f}, {gyro[2]:.2f}]", (20,90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    
    fps = count / (time.time() - start)
    cv2.putText(canvas, f"fps: {fps:.2f}", (20,120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    img = image.cv2image(canvas)
    disp.show(img)

rate = count / duration
print(f"有效采集速率: {rate:.2f} Hz")

