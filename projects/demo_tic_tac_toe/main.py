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

# 80 fps or 60fps
disp = display.Display()
ts = touchscreen.TouchScreen()

mode = 3

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
        if mode > 3:
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

def find_qizi():
    debug = True
    black_area_max_th = 6000
    area_threshold = 300
    pixels_threshold = 300
    threshold_red = [[40, 60, 33, 53, -10, 10]]
    threshold_black = [[0, 20, -128, 127, -128, 127]]
    threshold_white = [[60, 100, -11, 21, -43, -13]]

    cam = camera.Camera(320, 320, fps = 60) # fps can set to 80
    # cam.constrast(50)
    # cam.saturation(0)
    while mode == 3:
        img = cam.read()

        # 软件畸变矫正，速度比较慢，建议直接买无畸变摄像头（Sipeed 官方淘宝点询问）
        # img = img.lens_corr(strength=1.5)

        img_cv = image.image2cv(img, False, False)
        # gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
        # 高斯模糊去噪声
        blurred = cv2.GaussianBlur(img_cv, (5, 5), 0)

        blobs = img.find_blobs(threshold_red, roi=[1,1,img.width()-1, img.height()-1], x_stride=2, y_stride=1, area_threshold=area_threshold, pixels_threshold=pixels_threshold)
        for b in blobs:
            corners = b.mini_corners()
            for i in range(4):
                img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_YELLOW, 2)
        blobs = img.find_blobs(threshold_black, roi=[1,1,img.width()-1, img.height()-1], x_stride=2, y_stride=1, area_threshold=area_threshold, pixels_threshold=pixels_threshold)
        for b in blobs:
            corners = b.mini_corners()
            if b.area() < black_area_max_th:      # 过滤掉棋盘，认为area大于800时是棋盘，根据实际值调节
                enclosing_circle = b.enclosing_circle()
                img.draw_circle(enclosing_circle[0], enclosing_circle[1], enclosing_circle[2], image.COLOR_GREEN, 2)
            else:
                print("black area:", b.area())
        blobs = img.find_blobs(threshold_white, roi=[1,1,img.width()-1, img.height()-1], x_stride=2, y_stride=1, area_threshold=area_threshold, pixels_threshold=pixels_threshold)
        for b in blobs:
            corners = b.mini_corners()
            enclosing_circle = b.enclosing_circle()
            img.draw_circle(enclosing_circle[0], enclosing_circle[1], enclosing_circle[2], image.COLOR_RED, 2)

        if debug:
            # 左下画红色二值化图
            binary = img.binary(threshold_red, copy=True)
            binary1 = binary.resize(img.width() // 4, img.height() // 4)

            # 右下画黑色二值化图
            binary = img.binary(threshold_black, copy=True)
            binary2 = binary.resize(img.width() // 4, img.height() // 4)
            

            # 右上画白色二值化图
            binary = img.binary(threshold_white, copy=True)
            binary3 = binary.resize(img.width() // 4, img.height() // 4)

            img.draw_image(0, img.height() - binary1.height(), binary1)
            img.draw_image(img.width() - binary2.width(), img.height() - binary2.height(), binary2)
            img.draw_image(img.width() - binary3.width(), 0, binary3)

        check_mode_switch(img, disp.width(), disp.height())
        disp.show(img)
    del cam
    gc.collect()

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
