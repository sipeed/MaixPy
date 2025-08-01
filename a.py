import cv2
import numpy as np
import math
import random


def rotate_img(src, angle, scale=1.0):
    height, width = src.shape[:2]
    radian = math.radians(angle)

    # 计算旋转后图像的尺寸
    width_rotate = int((abs(width * math.cos(radian)) + abs(height * math.sin(radian))) * scale)
    height_rotate = int((abs(width * math.sin(radian)) + abs(height * math.cos(radian))) * scale)

    # 获取旋转中心
    center = (width / 2.0, height / 2.0)

    # 获取旋转矩阵
    M = cv2.getRotationMatrix2D(center, angle, scale)

    # 平移使得图像在新图中心
    M[0, 2] += (width_rotate - width) / 2.0
    M[1, 2] += (height_rotate - height) / 2.0

    # 进行仿射变换（保留 alpha 通道）
    if src.shape[2] == 4:
        border_val = (0, 0, 0, 0)
    else:
        border_val = (0, 0, 0)

    dst = cv2.warpAffine(src, M, (width_rotate, height_rotate),
                         flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT,
                         borderValue=border_val)
    return dst


img = cv2.imread("laohu2.png", cv2.IMREAD_UNCHANGED)

target = rotate_img(img, random.randint(0, 360), 1)
print(target.shape)
cv2.imwrite('rotated_result.png', target)
