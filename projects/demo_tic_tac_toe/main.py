'''
    Please read README.md first
    @author neucrack & lxowalle
    @license MIT
'''


from maix import camera, display, image, time, app, touchscreen
import cv2
import numpy as np

# 80 fps or 60fps
cam = camera.Camera(320, 320, fps=80)
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
        [0, 0, 100, 40],
    ]
    btn_rects_disp = [image.resize_map_pos(img.width(), img.height(), disp_w, disp_h, image.Fit.FIT_CONTAIN, btns[0][0], btns[0][1], btns[0][2], btns[0][3])]
    clicked, idx, rect = key_clicked(btn_rects_disp)
    if clicked:
        mode += 1
        if mode > 2:
            mode = 1
    img.draw_string(2, 10, f"mode {mode}", color=image.COLOR_WHITE, scale=1.5)
    img.draw_rect(btns[0][0], btns[0][1], btns[0][2], btns[0][3], image.COLOR_WHITE, 2)

def find_qipan():
    find_center_method = 1  # 1, 2
    area_threshold = 80
    pixels_threshold = 50
    thresholds = [[0, 80, 0, 80, 30, 80]]        # red
    # thresholds = [[0, 80, -120, -10, 0, 30]]        # green
    # thresholds = [[0, 80, 30, 100, -120, -60]]    # blue
    while mode == 1:
        img = cam.read()
        check_mode_switch(img, disp.width(), disp.height())
        img_cv = image.image2cv(img, False, False)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

        # 高斯模糊去噪声
        # blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 边缘检测
        edged = cv2.Canny(gray, 50, 150)

        # 膨胀处理
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edged, kernel, iterations=1)

        # disp.show(image.cv2image(dilated, False, False))
        # 查找轮廓
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                # 绘制顶点和轮廓
                # for corner in corners:
                #     cv2.circle(img_cv, tuple(corner), 4, (0, 255, 0), -1)

                # 绘制四边路径性
                # cv2.drawContours(img_cv, [approx], -1, (0, 255, 0), 1)

                # 洪泛填充外部，如果棋盘外部的背景和棋盘内部的背景不同才需要这一步
                img.flood_fill(corners[0][0] - 5, corners[0][1] - 5, 0.3, 0.3, image.COLOR_BLUE)
                # img.flood_fill(corners[1][0] - 5, corners[1][1] + 5, 0.5, 0.05, image.COLOR_BLUE)
                # img.flood_fill(corners[0][0] + 5, corners[0][1] + 5, 0.5, 0.05, image.COLOR_BLUE)
                # img.flood_fill(corners[0][0] + 5, corners[0][1] - 5, 0.5, 0.05, image.COLOR_BLUE)

                # 按顺序排列角点（左上、右上、右下、左下）
                # rect = np.zeros((4, 2), dtype="float32")
                # s = corners.sum(axis=1)
                # rect[0] = corners[np.argmin(s)]
                # rect[2] = corners[np.argmax(s)]
                # diff = np.diff(corners, axis=1)
                # rect[1] = corners[np.argmin(diff)]
                # rect[3] = corners[np.argmax(diff)]

                # (tl, tr, br, bl) = rect
                # 上面出来的结果已经是 点从左上逆时针，所以跳过找顶点
                tl = corners[0]
                bl = corners[1]
                br = corners[2]
                tr = corners[3]

                # 计算3x3格子的交叉点
                cross_points = []
                for i in range(4):
                    for j in range(4):
                        # 线性插值计算交叉点
                        cross_x = int((tl[0] * (3 - i) + tr[0] * i) * (3 - j) / 9 +
                                    (bl[0] * (3 - i) + br[0] * i) * j / 9)
                        cross_y = int((tl[1] * (3 - i) + tr[1] * i) * (3 - j) / 9 +
                                    (bl[1] * (3 - i) + br[1] * i) * j / 9)
                        cross_points.append((cross_x, cross_y))
                        cv2.circle(img_cv, (cross_x, cross_y), 3, (0, 255, 0), -1)

                centers = []
                # 找格子中心点方法一：直接根据顶点计算
                if find_center_method == 1:
                    for i in range(3):
                        for j in range(3):
                            center_x = int((cross_points[i * 4 + j][0] + cross_points[i * 4 + j + 1][0] + cross_points[(i + 1) * 4 + j][0] + cross_points[(i + 1) * 4 + j + 1][0]) / 4)
                            center_y = int((cross_points[i * 4 + j][1] + cross_points[i * 4 + j + 1][1] + cross_points[(i + 1) * 4 + j][1] + cross_points[(i + 1) * 4 + j + 1][1]) / 4)
                            centers.append((center_x, center_y))
                            cv2.circle(img_cv, (center_x, center_y), 2, (0, 255, 0), -1)
                elif find_center_method == 2:
                    # 找格子中心点方法二： 找色块的方式来确定中心点
                    roi = [corners[:,0].min(), corners[:,1].min(), corners[:,0].max() - corners[:,0].min(), corners[:,1].max() - corners[:,1].min()]
                    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_WHITE)
                    blobs = img.find_blobs(thresholds, roi=roi, x_stride=2, y_stride=1, area_threshold=area_threshold, pixels_threshold=pixels_threshold)
                    for b in blobs:
                        centers.append((b.cx(), b.cy()))
                        img.draw_circle(b.cx(), b.cy(), 2, image.COLOR_WHITE, -1)
                else:
                    raise Exception("find_center_method value error")

                # 对找到的中心点进行编号, y + x 最大就是右下角，最小就是左上角， y-x 最大就是左下角，y-x 最小就是右上角，其它几个点根据在旁边两个点中间判断
                if len(centers) == 9:
                    centers = np.array(centers)
                    rect = np.zeros((9, 2), dtype="float32")
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
                        # 写编号
                        for i in range(9):
                            img.draw_string(rect[i][0], rect[i][1], f"{i + 1}", image.COLOR_WHITE, scale=2, thickness=-1)
                    else:
                        # 大于 45度的情况
                        print("> 45 degree")

        disp.show(img)

def find_qizi():
    area_threshold = 300
    pixels_threshold = 300
    thresholds = []
    threshold_red = [40, 60, 33, 53, -10, 10]
    threshold_black = [0, 40, -128, 127, -128, 127]
    threshold_white = [60, 100, -11, 21, -43, -13]
    thresholds.append(threshold_red)
    thresholds.append(threshold_black)
    thresholds.append(threshold_white)

    while mode == 2:
        img = cam.read()
        check_mode_switch(img, disp.width(), disp.height())
        blobs = img.find_blobs(thresholds, roi=[1,1,img.width()-1, img.height()-1], x_stride=2, y_stride=1, area_threshold=area_threshold, pixels_threshold=pixels_threshold)
        for b in blobs:
            corners = b.mini_corners()
            if b.code() == 1:
                for i in range(4):
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_YELLOW, 2)
            elif b.code() == 2:
                if b.area() < 800:      # 过滤掉棋盘，认为area大于800时是棋盘，根据实际值调节
                    enclosing_circle = b.enclosing_circle()
                    img.draw_circle(enclosing_circle[0], enclosing_circle[1], enclosing_circle[2], image.COLOR_GREEN, 2)
            elif b.code() == 4:
                enclosing_circle = b.enclosing_circle()
                img.draw_circle(enclosing_circle[0], enclosing_circle[1], enclosing_circle[2], image.COLOR_RED, 2)
            corners = b.corners()

        disp.show(img)

def main():
    while not app.need_exit():
        find_qipan()
        find_qizi()

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
