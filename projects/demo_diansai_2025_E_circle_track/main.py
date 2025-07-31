'''
    2025电赛E题找A4 UV纸圆心，可以找到圆心和第三个圆圈，帧率 > 25fps。
    有多种设置和算法，根据实际情况选择。
    控制云台可以基于中心点误差 err_center 进行 PID 控制
    @author Neucrack@sipeed & lxo@sieed 协助
    @license MIT
    @date 2025.7.30
'''

from maix import camera, display, image, nn, app, time
disp = display.Display()
img = image.Image(disp.width(), disp.height())
msg = "Loading ..."
size = image.string_size(msg, scale = 1.5, thickness=2)
img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2, msg, scale=1.5, thickness=2)
disp.show(img)

import cv2
import numpy as np
import os


DEBUG=False
PRINT_TIME = False
debug_draw_err_line = False
debug_draw_err_msg = False
debug_draw_circle = False
debug_draw_rect = False
debug_show_hires = False

################################ config #########################################

# DEBUG=True                 # 打开调试模式，取消注释即可
# PRINT_TIME = True          # 打印每一步消耗的时间，取消注释即可
debug_draw_err_line = True   # 画出圆心和画面中心的误差线，需要消耗1ms左右时间
# debug_draw_err_msg = True    # 画出圆心和画面中心的误差值和 FPS 信息，需要消耗7ms左右时间，慎用
debug_draw_circle = True       # 画出圆圈，实际是画点，需要再打开变量, debug 模式都会画，耗费时间比较多，慎用
# debug_draw_rect = True         # 画出矩形框
debug_show_hires = True        # 显示结果在高分辨率图上，而不是小分辨率图上， 开启了 hires_mode 才生效


crop_padding = 12            # 裁切图时的外扩距离，调试到保证最近和最远位置整个黑框在检测框里，可以打开 DEBUG 模式看
rect_min_limit = 12          # 找到的大黑边框四个点最小距离必须大于这个值才有效，防止找到错误的值，可以放到最远位置测试
std_from_white_rect = True   # 裁切标准图是裁切自A4纸内部白色部分（更精准），False则是带黑框的外围框（整个A4纸）（更快一点点）
circle_num_points = 50       # 生成的第三个圆圈的点数量，控制圆边的平滑程度，可以用来巡迹
std_res = [int(29.7 / 21 * 80), 80]        # 找中心点和圆圈的分辨率，越大越精确，更慢，A4 29.7 x 21cm
hires_mode = True           # 高分辨模式，适合 find_circle 模式使用，帧率会更低但是找圆圈更精准
                             # 不 find_circle 也可以使用，找4个角点更精准，需要配合设置合理的 std_res
                             # 注意开启了这个模式，输出的误差值也是基于大图的分辨率
high_res = 448               # 高分辨率模式宽高,越高越清晰但是帧率越低，注意 std_res 也要跟着改大点
model_path = "/root/models/model_3356.mud" # 检测黑框模型路径，从 https://maixhub.com/model/zoo/1159 下载并传到开发板的 /root/models 目录


find_circle = False          # 在找到黑框以内白框后是否继续找圆，如果圆圈画得标准，在纸正中心则不用找，如果画点不在纸正中心则需要找。
                             # 建议把A4纸制作正确就不用找了，帧率更高。
                             # 可以用hires_mode 更清晰才能识别到，另外设置合理的 std_res
cam_buff_num = 1             # 摄像头缓冲， 1 延迟更低帧率慢一点点， 2延迟更高帧率高一点点
find_laser = False           # 找激光点（未测试），实际使用时直接把摄像头中心和激光点保持移植就好了，不需要找激光点

auto_awb = True                            # 自动白平衡或者手动白平衡
awb_gain = [0.134, 0.0625, 0.0625, 0.1139]  # 手动白平衡，auto_awb为False才生效， R GR GB B 的值，调 R 和 B 即可
contrast = 80                               # 对比度，会影响到检测，阴影和圆圈痕迹都会更重

###################################################################################

if not os.path.exists(model_path):
    model_path1 = "model/model_3356.mud"
    if not os.path.exists(model_path1):
        print(f"load model failed, please put model in {model_path}, or {os.path.getcwd()}/{model_path1}")
    model_path = model_path1

# 初始化摄像头
detector = nn.YOLOv5(model=model_path, dual_buff = True)

# 初始化摄像头
if hires_mode:
    cam = camera.Camera(high_res, high_res, detector.input_format(), buff_num=cam_buff_num)
else:
    cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format(), buff_num=cam_buff_num)
if not auto_awb:
    cam.awb_mode(camera.AwbMode.Manual)
    cam.set_wb_gain(awb_gain)
cam.constrast(contrast)
# cam.set_windowing([448, 448])

def find_laser_point(img, original_img):
    '''
        随便写的，有需要请自己修改算法
    '''

    # 这里需要调阈值
    ths = [[0, 100, -128, 127, -128, -18]]
    blobs = img_std.find_blobs(ths, x_stride=2, y_stride=2)
    max_s = 0
    max_b = None
    for b in blobs:
        s = b.w() * b.h()
        if s > max_s:
            max_s = s
            max_b = b
    if DEBUG:
        laser_binary = img.binary(ths, copy=True)
        original_img.draw_image(original_img.width() - laser_binary.width(), original_img.height() - laser_binary.height(), laser_binary)
    return max_b

_t = time.ticks_ms()
def debug_time(msg):
    if PRINT_TIME:
        global _t
        print(f"t: {time.ticks_ms() - _t:4d} {msg}")
        _t = time.ticks_ms()

err_center = [0, 0] # 距离中心的误差
center_pos = [cam.width() // 2, cam.height() // 2] # 画面的中心
last_center = center_pos # 上一次检测到的圆心距离
last_center_small = [detector.input_width(), detector.input_height()] # 高清模式时，在小图的中心坐标
while not app.need_exit():
    debug_time("start")
    img = cam.read()
    debug_time("cam read")
    # AI 检测外框
    if hires_mode:
        img_ai = img.resize(detector.input_width(), detector.input_height())
    else:
        img_ai = img # new copy
    debug_time("resize")
    objs = detector.detect(img_ai, conf_th = 0.5, iou_th = 0.45)
    max_idx = -1
    max_s = 0
    for i, obj in enumerate(objs):
        s = obj.w * obj.h
        if s > max_s:
            max_s = s
            max_idx = i
        # img_ai.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED, thickness=4)
        # msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        # img_ai.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED, scale=2)
    debug_time("detect")
    if max_idx >= 0:
        obj = objs[max_idx]
        w = obj.w + crop_padding * 2
        h = obj.h + crop_padding * 2
        w = w + 1 if w % 2 != 0 else w
        h = h + 1 if h % 2 != 0 else h
        x = obj.x - crop_padding
        y = obj.y - crop_padding
        if x < 0:
            w += x
            x = 0
        if y < 0:
            h += y
            y = 0
        if x + w > img_ai.width():
            w = img_ai.width() - x
        if y + h > img_ai.height():
            h = img_ai.height() - y
        crop_ai = img_ai.crop(x, y, w, h)
        crop_ai_rect = [x, y, w, h]
        # 算出裁切范围对应在大图的位置
        # 注意这里只考虑到了拉伸缩放(iamge.Fit.FILL)
        img_ai_scale = [img.width() / img_ai.width(), img.height() / img_ai.height()]
        # crop_rect = image.resize_map_pos_reverse(img.width(), img.height(), img_ai.width(), img_ai.height(), image.Fit.FIT_FILL, obj.x, obj.y, obj.w, obj.h)
        crop_rect = [int(obj.x * img_ai_scale[0]), int(obj.y * img_ai_scale[1]), int(obj.w * img_ai_scale[0]), int(h * img_ai_scale[0])]
        img_cv = image.image2cv(img, False, False)
        crop_ai_cv = image.image2cv(crop_ai, False, False)
        debug_time("crop")

        gray = crop_ai.to_format(image.Format.FMT_GRAYSCALE)
        gray_cv = image.image2cv(gray, False, False)
        debug_time("gray")

        # 二值化图，找出黑色外轮廓，可以用其它算法
        # 高斯模糊去噪声
        # blurred = cv2.GaussianBlur(gray_cv, (5, 5), 0)
        # 边缘检测，阈值 0，150
        # edged = cv2.Canny(blurred, 50, 150)
        # # 膨胀处理
        # kernel = np.ones((5, 5), np.uint8)
        # dilated = cv2.dilate(edged, kernel, iterations=1)
        # # 腐蚀处理
        # binary = cv2.erode(dilated, kernel, iterations=1)
        # 自适应二值化，最后两个参数可以调整
        binary = cv2.adaptiveThreshold(gray_cv, 255,
                       cv2.ADAPTIVE_THRESH_MEAN_C,
                       cv2.THRESH_BINARY_INV, 27, 31)
        debug_time("binary")


        if std_from_white_rect:
            # 执行洪泛填充找出内白色轮廓
            h, w = binary.shape[:2]
            mask = np.zeros((h + 2, w + 2), np.uint8)
            # 设置种子点（左上角和右下角），如果环境好，可以只点一个角
            seed_point = (2, 2)
            seed_point2 = (w - 2, h - 2)
            # 设置填充值（白色 255）
            fill_value = 255
            # 执行洪泛填充（以左上角像素值为基准）
            cv2.floodFill(binary, mask, seed_point, fill_value, loDiff=5, upDiff=5, flags=4)
            cv2.floodFill(binary, mask, seed_point2, fill_value, loDiff=5, upDiff=5, flags=4)
            binary = cv2.bitwise_not(binary)
            debug_time("fill")

        # 查找轮廓4个角点
        approx = None
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            # 筛选出最大的轮廓
            largest_contour = max(contours, key=cv2.contourArea)
            # 近似多边形
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            debug_time("find countours")
            # 如果找到的是一个四边形
            if len(approx) == 4:
                # 获取矩形四个角点
                # 对角点进行排序：左上、右上、右下、左下
                corners = approx.reshape((4, 2))
                # 按顺序排列角点（左上、右上、右下、左下）
                rect = np.zeros((4, 2), dtype="float32")
                s = corners.sum(axis=1)
                rect[0] = corners[np.argmin(s)] # 最小和，左上
                rect[2] = corners[np.argmax(s)] # 最大和，右下
                diff = np.diff(corners, axis=1) # y - x
                rect[3] = corners[np.argmax(diff)] # 差最大，左下
                rect[1] = corners[np.argmin(diff)] # 差最小，右上
                minW = min(rect[1][0] - rect[0][0], rect[2][0] - rect[3][0])
                minH = min(rect[3][1] - rect[0][1], rect[2][1] - rect[1][1])
                if minH > rect_min_limit and minW > rect_min_limit:
                    debug_time("find rect")

                    # 计算目标图像宽高（按最大边计算）
                    # (tl, tr, br, bl) = rect
                    # widthA = np.linalg.norm(br - bl)
                    # widthB = np.linalg.norm(tr - tl)
                    # maxWidth = int(max(widthA, widthB) * img_ai_scale[0] * std_scale)

                    # heightA = np.linalg.norm(tr - br)
                    # heightB = np.linalg.norm(tl - bl)
                    # maxHeight = int(max(heightA, heightB) * img_ai_scale[1] * std_scale)
                    # print(maxWidth, maxHeight)


                    maxWidth = std_res[0]
                    maxHeight = std_res[1]

                    # rect 映射到大图, 从大图中得到标准内框图
                    rect[:, 0] += crop_ai_rect[0]
                    rect[:, 1] += crop_ai_rect[1]
                    rect[:, 0] *= img_ai_scale[0]
                    rect[:, 1] *= img_ai_scale[1]
                    # 透视变换
                    dst = np.array([
                        [0, 0],
                        [maxWidth - 1, 0],
                        [maxWidth - 1, maxHeight - 1],
                        [0, maxHeight - 1]], dtype="float32")
                    M = cv2.getPerspectiveTransform(rect, dst)
                    M_inv = np.linalg.inv(M)
                    img_std_cv = cv2.warpPerspective(img_cv, M, (maxWidth, maxHeight))
                    img_std = image.cv2image(img_std_cv, False, False)
                    debug_time("get std img")

                    # 如果前面找到得标准图有黑框，用find_blobs 处理一下
                    # ths = [[0, 10, -128, 127, -128, 127]]
                    # blobs = img_std.find_blobs(ths, roi=[0, 0, 10, 10], x_stride=1, y_stride=1)
                    # A4 纸 21cm, 黑框 1.8*2=3.6cm， 白色区域为 17.4cm，圆圈2cm间距
                    # 得出 圆圈间距像素为 2/17.4 * 白色区域高度像素。（0.1149425287356322）
                    # 如果是黑色边框，则 2/21 * 黑框高度像素。(0.09523809523809523)
                    # if len(blobs) > 0: # 有黑框
                        # circle_dist = img_std.height() * 0.09523809523809523
                    # else:
                    if std_from_white_rect:
                        circle_dist = int(img_std.height() * 0.1149425287356322)
                    else:
                        circle_dist = img_std.height() * 0.09523809523809523
                    if circle_dist > 0:
                        center = [img_std.width() // 2, img_std.height() // 2]
                        # 是否找圆和圆心
                        center_new = None
                        if find_circle:
                            img_std_gray_cv = cv2.cvtColor(img_std_cv, cv2.COLOR_RGB2GRAY)
                            w = h = int(circle_dist * 3)
                            roi = [center[0] - w // 2, center[1] - h // 2, w, h]
                            img_small_circle_cv = img_std_gray_cv[roi[1]:roi[1] + roi[3], roi[0]:roi[0]+roi[2]]
                            if DEBUG:
                                img_small_circle = image.cv2image(img_small_circle_cv, False, False)
                                img.draw_image(crop_ai.width(), img_std.height(), img_small_circle)

                            # 用霍夫变换找圆
                            circles = cv2.HoughCircles(img_small_circle_cv, cv2.HOUGH_GRADIENT, dp=1.2,
                                                    minDist=roi[2] // 2,
                                                    param1=100, param2=20,
                                                    minRadius=roi[2] // 4, maxRadius=roi[2] // 2)
                            # 把找圆范围画出来
                            if DEBUG:
                                img_std.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_ORANGE)
                                cv2.circle(img_std_cv, center, 1, (0, 255, 0), -1)
                            # 若检测到圆，得到中心和半径
                            circle_dist_new = 0
                            if circles is not None:
                                circles = np.uint16(np.around(circles))
                                for c in circles[0, :]:
                                    center_new = (c[0] + roi[0], c[1] + roi[1])  # 圆心坐标偏移回原图
                                    circle_dist_new = c[2]
                                    if DEBUG:
                                        cv2.circle(img_std_cv, center_new, circle_dist_new, (0, 255, 0), 1)
                                        cv2.circle(img_std_cv, center_new, 1, (0, 0, 255), 3)  # 圆心
                                    # 这里认为只能检测到一个圆，如果多个，那画面有问题，或者再优化这里的代码
                                    break
                            # binary = cv2.adaptiveThreshold(img_std_gray_cv, 255,
                            #                cv2.ADAPTIVE_THRESH_MEAN_C,
                            #                cv2.THRESH_BINARY_INV, 11, 3)
                            # # 膨胀加强线条
                            # kernel = np.ones((2, 2), np.uint8)
                            # enhanced = cv2.dilate(binary, kernel, iterations=1)
                            # eroded = cv2.erode(enhanced, kernel, iterations=1)
                            # circles = img3.find_circles(roi = roi, x_stride=4, y_stride = 4, threshold=2000, r_step = 4)
                            if center_new:
                                # 更新圆环中心和圆环间距离
                                center = center_new
                                circle_dist = circle_dist_new
                                # 在标准图中画出新中心和第三个圈
                                if DEBUG:
                                    cv2.circle(img_std_cv, center, 1, (0, 255, 0), -1)
                                    cv2.circle(img_std_cv, center, circle_dist * 3, (0, 255, 0), 1)
                            debug_time("find circle")

                            # 如果不找圆心，或者找到了圆心
                        if (not find_circle) or (center_new):
                            # 原图画圆中心
                            std_center_points = np.array([[center]], dtype=np.float32)
                            original_center_point = cv2.perspectiveTransform(std_center_points, M_inv)[0][0].astype(np.int32).tolist()
                            err_center = [
                                original_center_point[0] - center_pos[0],
                                original_center_point[1] - center_pos[1],
                            ]
                            last_center = original_center_point
                            last_center_small = [int(last_center[0] / img_ai_scale[0]), int(last_center[1] / img_ai_scale[1])]
                            # 原图画圆
                            radius = circle_dist * 3 # 第三个圈的半径
                            # 构造圆上的轮廓点
                            debug_time("get points 3")
                            angles = np.linspace(0, 2 * np.pi, circle_num_points, endpoint=False)  # endpoint=False 避免首尾重复
                            cos_vals = np.cos(angles)
                            sin_vals = np.sin(angles)

                            # 向量方式生成所有点
                            x = center[0] + radius * cos_vals
                            y = center[1] + radius * sin_vals
                            circle_pts = np.stack((x, y), axis=1).astype(np.float32)  # shape: (N, 2)
                            circle_pts = circle_pts[np.newaxis, :, :]  # reshape to (1, N, 2)
                            debug_time("get points 1")

                            # 反变换回原图
                            orig_circle_pts = cv2.perspectiveTransform(circle_pts, M_inv)
                            debug_time("get points")

                            # 找激光点
                            original_lasert_point = None
                            if find_laser:
                                laser_point = find_laser_point(img_std, img if DEBUG else img_ai)
                                if laser_point:
                                    # 原图坐标
                                    points = np.array([[[laser_point.x(), laser_point.y()]]], dtype=np.float32)
                                    original_lasert_point = cv2.perspectiveTransform(points, M_inv)[0][0]
                            # 画在大图上
                            if DEBUG or debug_show_hires:
                                img.draw_circle(original_center_point[0], original_center_point[1], 4, image.COLOR_RED, thickness=-1)
                                pts = np.round(orig_circle_pts[0]).astype(np.int32)
                                cv2.polylines(img_cv, [pts], isClosed=True, color=(0, 0, 255), thickness=1)
                                if original_lasert_point is not None:
                                    img.draw_circle(original_lasert_point[0], original_lasert_point[1], 3, image.COLOR_GREEN, thickness=1)
                            else:
                            # 画在小图上显示
                                # too slow
                                # center_ai = image.resize_map_pos(img.width(), img.height(), img_ai.width(), img_ai.height(), image.Fit.FIT_FILL, original_center_point[0], original_center_point[1])
                                center_ai = [int(original_center_point[0] * img_ai_scale[0]), int(original_center_point[1] * img_ai_scale[1])]
                                img_ai.draw_circle(center_ai[0], center_ai[1], 2, image.COLOR_RED, thickness=-1)
                                pts = orig_circle_pts[0]  # shape: (N, 2)

                                scaled_pts = (pts * img_ai_scale).astype(np.int32)  # shape: (N, 2)
                                points = scaled_pts.reshape(-1).tolist()  # 转为 Python list（与原结果相同）
                                if debug_draw_circle:
                                    img_ai.draw_keypoints(points, image.COLOR_RED, 1, line_thickness=1)
                                if original_lasert_point is not None:
                                    img_ai.draw_circle(original_lasert_point[0], original_lasert_point[1], 3, image.COLOR_GREEN, thickness=1)
                            debug_time("draw points")
                        if DEBUG:
                            img.draw_image(crop_ai.width(), 0, img_std)
                    else:
                        print("detected circle too small", img_std.width(), img_std.height())
                else:
                    print(minW, minH, "rect not valid")

        # 绘制路径
        if approx is not None:
            cv2.drawContours(crop_ai_cv, [approx], -1, (255, 255, 255), 1)
        if DEBUG:
            img.draw_image(0, 0, crop_ai)
            img2 = image.cv2image(binary, False, False)
            img.draw_image(0, crop_ai.height(), img2)

        if debug_draw_rect:
            img.draw_rect(crop_rect[0], crop_rect[1], crop_rect[2], crop_rect[3], color = image.COLOR_RED, thickness=2)
            # msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
            # img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED, scale=2)
        debug_time("draw")
    if DEBUG or debug_show_hires:
        if debug_draw_err_line:
            img.draw_line(center_pos[0], center_pos[1], last_center[0], last_center[1], image.COLOR_RED, thickness=3)
        if debug_draw_err_msg:
            img.draw_string(2, img.height() - 32, f"err: {err_center[0]:5.1f}, {err_center[1]:5.1f}, fps: {time.fps():2.0f}", image.COLOR_RED, scale=1.5, thickness=2)
        disp.show(img)
    else:
        if debug_draw_err_line:
            img_ai.draw_line(center_pos[0], center_pos[1], last_center_small[0], last_center_small[1], image.COLOR_RED, thickness=3)
        if debug_draw_err_msg:
            img_ai.draw_string(2, img.height() - 32, f"err: {err_center[0]:5.1f}, {err_center[1]:5.1f}, fps: {time.fps():2.0f}", image.COLOR_RED, scale=1.5, thickness=2)
        disp.show(img_ai)
    debug_time("display img")