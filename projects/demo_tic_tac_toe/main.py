'''
    Please read README.md first
    @author neucrack & lxowalle
    @license MIT
'''


from types import CellType
from maix import camera, display, image, time, app, touchscreen
import cv2
import numpy as np
import gc
from utils import rgb888_to_lab

# 80 fps or 60fps
disp = display.Display()
ts = touchscreen.TouchScreen()

mode = 1

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def key_clicked(btn_rects):
    global last_pressed
    x, y, pressed = ts.read()
    if pressed:
        for i, btn in enumerate(btn_rects):
            if is_in_button(x, y, btn):
                if not last_pressed:
                    last_pressed = True
                    return True, i, btn
    else:
        last_pressed = False
    return False, 0, []

def check_mode_switch(img : image.Image, disp_w, disp_h):
    global mode
    btns = [
        [0, 0, 75, 30],
    ]
    btn_rects_disp = [image.resize_map_pos(img.width(), img.height(), disp_w, disp_h, image.Fit.FIT_CONTAIN, btns[0][0], btns[0][1], btns[0][2], btns[0][3])]
    clicked, idx, rect = key_clicked(btn_rects_disp)
    if clicked:
        mode += 1
        if mode > 4:
            mode = 1
    img.draw_string(2, 5, f"mode{mode}", color=image.COLOR_WHITE, scale=1.3)
    img.draw_rect(btns[0][0], btns[0][1], btns[0][2], btns[0][3], image.COLOR_WHITE, 2)

def find_grid_centers(corners):
    """
    corners: List of 4 tuples representing the corners of the 3x3 grid in the order:
             top-left, top-right, bottom-right, bottom-left
    """
    # Define the 3x3 grid points in the normalized coordinate space
    grid_points = np.array([[0, 0], [1/3, 0], [2/3, 0], [1, 0],
                            [0, 1/3], [1/3, 1/3], [2/3, 1/3], [1, 1/3],
                            [0, 2/3], [1/3, 2/3], [2/3, 2/3], [1, 2/3],
                            [0, 1], [1/3, 1], [2/3, 1], [1, 1]])

    # Convert corners to numpy array
    src_points = np.array(corners, dtype=np.float32)

    # Define destination points for the perspective transform
    dst_points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)

    # Compute the perspective transform matrix
    transform_matrix = cv2.getPerspectiveTransform(dst_points, src_points)

    # Transform grid points to image coordinate space
    transformed_points = cv2.perspectiveTransform(np.array([grid_points], dtype=np.float32), transform_matrix)[0]

    # Calculate the center points of the grid cells
    centers = []
    for i in range(0, 3):
        for j in range(0, 3):
            cx = (transformed_points[i * 4 + j][0] + transformed_points[i * 4 + j + 1][0] + 
                  transformed_points[(i + 1) * 4 + j][0] + transformed_points[(i + 1) * 4 + j + 1][0]) / 4
            cy = (transformed_points[i * 4 + j][1] + transformed_points[i * 4 + j + 1][1] + 
                  transformed_points[(i + 1) * 4 + j][1] + transformed_points[(i + 1) * 4 + j + 1][1]) / 4
            centers.append((int(cx), int(cy)))

    return centers

def find_qipan():
    cam = camera.Camera(320, 320, fps=60) # fps can set to 80
    area_threshold = 80
    pixels_threshold = 50
    thresholds = [[0, 80, 0, 80, 30, 80]]        # red
    # thresholds = [[0, 80, -120, -10, 0, 30]]        # green
    # thresholds = [[0, 80, 30, 100, -120, -60]]    # blue
    while mode == 1 or mode == 2:
        find_center_method = mode  # 1：根据4个角确定格子中心, 2：使用找色块确定格子中心
        img = cam.read()

        # 软件畸变矫正，速度比较慢，建议直接买无畸变摄像头（Sipeed 官方淘宝点询问）
        # img = img.lens_corr(strength=1.5)

        img_cv = image.image2cv(img, False, False)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

        # 高斯模糊去噪声
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 边缘检测，阈值 0，150
        edged = cv2.Canny(blurred, 50, 150)

        # 膨胀处理
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edged, kernel, iterations=1)

        # 腐蚀处理
        eroded = cv2.erode(dilated, kernel, iterations=1)

        binary = eroded

        # 显示二值化后的图
        #    左下角显示
        # img_tmp = image.cv2image(binary, False, False).resize(img.width() // 4, img.height() // 4)
        # img.draw_image(0, img.height() - img_tmp.height(), img_tmp)
        #    整张图显示
        # disp.show(image.cv2image(binary, False, False))

        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            # 筛选出最大的轮廓
            largest_contour = max(contours, key=cv2.contourArea)

            # 近似多边形
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)

            # 如果找到的是一个四边形
            if len(approx) == 4:
                # print("rect found")
                corners = approx.reshape((4, 2))
                # 按顺序排列角点（左上、右上、右下、左下）
                rect = np.zeros((4, 2), dtype="int")
                s = corners.sum(axis=1)
                rect[0] = corners[np.argmin(s)]
                rect[2] = corners[np.argmax(s)]
                diff = np.diff(corners, axis=1)
                rect[1] = corners[np.argmin(diff)]
                rect[3] = corners[np.argmax(diff)]
                corners = rect

                # TODO: 这是外角点，可以优化一下找到线中心的点，这里直接写死往内收拢 1 个像素
                half_x = 1
                half_y = 1
                corners[0] += (half_x, half_y)
                corners[1] += (-half_x, half_y)
                corners[2] += (-half_x, -half_y)
                corners[3] += (half_x, -half_y)

                # 绘制顶点和轮廓
                for corner in corners:
                    cv2.circle(img_cv, tuple(corner), 4, (0, 255, 0), -1)

                # 绘制四边路径性
                # cv2.drawContours(img_cv, [approx], -1, (0, 255, 0), 1)

                # 洪泛填充外部，如果棋盘外部的背景和棋盘内部的背景相同且后面用了找色块的方式找才需要这一步
                if find_center_method == 2:
                    img.flood_fill(corners[0][0] - 5, corners[0][1] - 5, 0.3, 0.3, image.COLOR_BLUE)
                    # img.flood_fill(corners[1][0] - 5, corners[1][1] + 5, 0.5, 0.05, image.COLOR_BLUE)
                    # img.flood_fill(corners[0][0] + 5, corners[0][1] + 5, 0.5, 0.05, image.COLOR_BLUE)
                    # img.flood_fill(corners[0][0] + 5, corners[0][1] - 5, 0.5, 0.05, image.COLOR_BLUE)

                centers = []
                outer_rect = [corners[:,0].min(), corners[:,1].min(), corners[:,0].max() - corners[:,0].min(), corners[:,1].max() - corners[:,1].min()]
                # 找格子中心点方法一：直接根据顶点计算
                if find_center_method == 1:
                    # 根据顶点找出中心点
                    centers  = find_grid_centers(corners)
                # 找格子中心点方法二： 找色块的方式来确定中心点
                elif find_center_method == 2:                # 上面出来的结果已经是 点从左上顺时针
                    blobs = img.find_blobs(thresholds, roi=outer_rect, x_stride=2, y_stride=1, area_threshold=area_threshold, pixels_threshold=pixels_threshold)
                    for b in blobs:
                        centers.append((b.cx(), b.cy()))
                    # 因为此方法找到的中心点坐标是乱序的，对找到的中心点进行编号, y + x 最大就是右下角，最小就是左上角， y-x 最大就是左下角，y-x 最小就是右上角，其它几个点根据在旁边两个点中间判断
                    if len(centers) == 9:
                        centers = np.array(centers)
                        rect = np.zeros((9, 2), dtype="int")
                        s = centers.sum(axis=1)
                        idx_0 = np.argmin(s)
                        idx_8 = np.argmax(s)
                        diff = np.diff(centers, axis=1)
                        idx_2 = np.argmin(diff)
                        idx_6 = np.argmax(diff)
                        rect[0] = centers[idx_0]
                        rect[2] = centers[idx_2]
                        rect[6] = centers[idx_6]
                        rect[8] = centers[idx_8]
                        #   其它点
                        calc_center = (rect[0] + rect[2] + rect[6] + rect[8]) / 4
                        mask = np.zeros(centers.shape[0], dtype=bool)
                        idxes = [1, 3, 4, 5, 7]
                        mask[idxes] = True
                        others = centers[mask]
                        idx_l = others[:,0].argmin()
                        idx_r = others[:,0].argmax()
                        idx_t = others[:,1].argmin()
                        idx_b = others[:,1].argmax()
                        found = np.array([idx_l, idx_r, idx_t, idx_b])
                        mask = np.isin(range(len(others)), found, invert=False)
                        idx_c = np.where(mask == False)[0]
                        if len(idx_c) == 1:
                            rect[1] = others[idx_t]
                            rect[3] = others[idx_l]
                            rect[4] = others[idx_c]
                            rect[5] = others[idx_r]
                            rect[7] = others[idx_b]
                        else:
                            # 等于 45度的情况
                            print("== 45 degree")
                        centers = rect
                else:
                    raise Exception("find_center_method value error")

                # 画外围框，可以方便安装时正面对齐
                img.draw_rect(outer_rect[0], outer_rect[1], outer_rect[2], outer_rect[3], image.COLOR_WHITE)
                # 画出中心点
                # 写编号
                if len(centers) == 9:
                    for i in range(9):
                        x, y = centers[i][0], centers[i][1]
                        cv2.circle(img_cv, (x, y), 2, (0, 255, 0), -1)
                        img.draw_string(x, y, f"{i + 1}", image.COLOR_WHITE, scale=2, thickness=-1)

        check_mode_switch(img, disp.width(), disp.height())
        disp.show(img)
    del cam
    gc.collect()

def blob_is_valid(b):
    is_valid = True
    if b.area() > 3000: # 认为面积大于3000时无效,受距离影响
        is_valid = False
    if b.w() > 55 or b.h() > 55: # 过滤过大的宽高
        is_valid = False
    return is_valid

def find_qizi():
    cam = camera.Camera(320, 320, fps = 60) # fps can set to 80
    area_threshold = 300
    pixels_threshold = 300
    last_pointer = [0, 0]
    last_string = ""
    # 1. 点击触摸屏获取棋子的LAB值，根据LAB值获取一个合适的阈值
    # 2. 在white_thresholds（白棋阈值）或white_thresholds（黑棋阈值）中增加、或者合并新的阈值。阈值越多执行越慢，也可以自行编写逻辑记录上次的阈值来提高速度
    # 3. 设置area_threshold和pixels_threshold过滤一些较小的色块
    # 4. 自定义blob_is_valid来添加其他过滤规则
    # 5. 添加roi来过滤不需要检测的部分，降低环境复杂程度
    # 注意：环境太暗时无法识别黑棋有可能是因为棋子离黑线过近，棋子的影子和黑线连在一起被认为时一个色块，导致该棋子被过滤了。建议保证室内有均匀的光线
    white_thresholds = [[63,96,-13,17,8,56], [60,94,-16,14,-25,23]]
    black_thresholds = [[9,45,-15,18,-20,19], [16,46,3,33,3,33], [14,44,-16,25,-13,36], [0,33,-15,16,-19,13]]
    white_blobs = None
    black_blobs = None
    roi = [5, 5, cam.width() - 10, cam.height() - 10] # 配置roi范围
    while mode == 3:
        img = cam.read()
        # 检测黑/白棋子
        for threshold in black_thresholds:
            black_blobs = img.find_blobs([threshold], roi = roi, area_threshold = area_threshold, pixels_threshold = pixels_threshold)
            valid_cnt = 0
            # 检查有效数量大于等于5,则认为阈值有效,否则使用下一个阈值
            for b in black_blobs:
                if blob_is_valid(b):
                    valid_cnt += 1
            if valid_cnt >= 5:
                break

        for threshold in white_thresholds:
            white_blobs = img.find_blobs([threshold], area_threshold = area_threshold, pixels_threshold = pixels_threshold)
            valid_cnt = 0
            # 检查有效数量大于等于5,则认为阈值有效,否则使用下一个阈值
            for b in white_blobs:
                if blob_is_valid(b):
                    valid_cnt += 1
            if valid_cnt >= 5:
                break

        # 检测完成后打印黑/白棋子位置，在这里做逻辑处理
        if black_blobs:
            for b in black_blobs:
                if blob_is_valid(b):
                    corners = b.mini_corners()
                    for i in range(4):
                        img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_GREEN, 2)

        if white_blobs:
            for b in white_blobs:
                if blob_is_valid(b):
                    corners = b.mini_corners()
                    for i in range(4):
                        img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE, 2)

        # 点击屏幕，获取当前lab值，并给出一个预测值。TODO:坐标映射有BUG，以屏幕绿点位置为准
        t = ts.read()
        x, y, touch = t[0], t[1], t[2]
        if touch:
            cam_w = cam.width()
            cam_h = cam.height()
            disp_w = disp.width()
            disp_h = disp.height()
            x += ((cam_w - img.width()) / 2)
            y += ((cam_h - img.height()) / 2)
            real_x = int(x * cam_w / disp_w)
            real_y = int(y * cam_h / disp_h)
            last_pointer[0] = real_x
            last_pointer[1] = real_y
            rgb = img.get_pixel(real_x, real_y, True)
            l, a, b = rgb888_to_lab(rgb[0], rgb[1], rgb[2])
            last_string = f"l:{l}, a:{a}, b:{b}, try [{max(l-15, 0)},{min(l+15, 100)},{max(a-15, -128)},{min(a+15, 127)},{max(b-15, -128)},{min(b+15, 127)}]"
            print(last_string)
        img.draw_circle(last_pointer[0], last_pointer[1], 3, image.COLOR_GREEN, -1)
        img.draw_string(0, 10, last_string, image.COLOR_RED)

        # 画出roi区域
        img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_YELLOW, 2)
        check_mode_switch(img, disp.width(), disp.height())
        disp.show(img)
    del cam
    gc.collect()


def find_qizi_auto_threshold():
    cam = camera.Camera(320, 240)
    cam.saturation(0)
    cam.constrast(100)

    last_pointer = [0, 0]
    last_string = ""
    threshold_white = [0, 0]
    threshold_black = [0, 0]
    while mode == 4:
        t = time.ticks_ms()
        img = cam.read()             # Max FPS is determined by the camera hardware and driver settings

        # 通过直方图找到合适的阈值
        hist = img.get_histogram([[0,100]])
        tmp_threshold = []
        l_min = 0
        l_max = 0
        last_idx = 0
        is_first = True
        for idx, value in enumerate(hist.bins()):
            if value > 0.01:
                # print(idx, value)
                if is_first:
                    l_min = idx
                    is_first = False

                if idx - last_idx >= 10:
                    tmp_threshold.append([l_min, l_max])
                    l_min = idx
                    last_idx = idx
                    continue
                else:
                    l_max = idx
                    last_idx = idx
        if l_min >= l_max:
            tmp_threshold.append([l_min, 100])
        else:
            tmp_threshold.append([l_min, l_max])

        # 更新黑白棋阈值
        if len(tmp_threshold) > 0:
            threshold_black = [max(tmp_threshold[0][0] - 15, 0), min(tmp_threshold[0][1] + 15, 100)]
        if len(tmp_threshold) > 2:
            threshold_white = [max(tmp_threshold[2][0] - 15, 0), min(tmp_threshold[2][1] + 15, 100)]

        # 寻找黑白棋
        blobs = img.find_blobs([threshold_black], area_threshold=300, pixels_threshold=300)
        for b in blobs:
            if b.area() < 2000:
                corners = b.mini_corners()
                for i in range(4):
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_BLUE, 2)

        blobs = img.find_blobs([threshold_white], area_threshold=300, pixels_threshold=300)
        for b in blobs:
            corners = b.mini_corners()
            for i in range(4):
                img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED, 2)

        # 点击屏幕，获取当前lab值，并给出一个预测值。TODO:坐标映射有BUG，以屏幕绿点位置为准
        t = ts.read()
        x, y, touch = t[0], t[1], t[2]
        if touch:
            cam_w = cam.width()
            cam_h = cam.height()
            disp_w = disp.width()
            disp_h = disp.height()
            x += ((cam_w - img.width()) / 2)
            y += ((cam_h - img.height()) / 2)
            real_x = int(x * cam_w / disp_w)
            real_y = int(y * cam_h / disp_h)
            last_pointer[0] = real_x
            last_pointer[1] = real_y
            rgb = img.get_pixel(real_x, real_y, True)
            l, a, b = rgb888_to_lab(rgb[0], rgb[1], rgb[2])
            last_string = f"l:{l}, a:{a}, b:{b}, try [{max(l-15, 0)},{min(l+15, 100)},{max(a-15, -128)},{min(a+15, 127)},{max(b-15, -128)},{min(b+15, 127)}]"
            print(last_string)
        img.draw_circle(last_pointer[0], last_pointer[1], 3, image.COLOR_GREEN, -1)
        img.draw_string(0, 10, last_string, image.COLOR_RED)

        check_mode_switch(img, disp.width(), disp.height())
        disp.show(img)
    del cam
    gc.collect()

def main():
    while not app.need_exit():
        find_qipan()
        find_qizi()
        find_qizi_auto_threshold()

if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        e = traceback.format_exc()
        print(e)
        img = image.Image(disp.width(), disp.height())
        img.draw_string(2, 2, e, image.COLOR_WHITE, font="hershey_complex_small", scale=0.6)
        disp.show(img)
        while not app.need_exit():
            time.sleep(0.2)
