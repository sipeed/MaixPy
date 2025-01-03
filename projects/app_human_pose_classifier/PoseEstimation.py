import numpy as np
from collections import deque

class PoseEstimation:
    def __init__(self, keypoints_window_size=5):
        self.keypoints_map_deque = deque(maxlen=keypoints_window_size)
        self.status = []

    def feed_keypoints_17(self, keypoints_17):
        """
        # keypoints 是 17 个关键点的坐标 [(x1, y1), (x2, y2), ..., (x17, y17)]
        基于 yolo-pose 17关键点模型估测骨架坐标:
        0 - 鼻子 (Nose)
        1 - 左眼 (Left Eye)
        2 - 右眼 (Right Eye)
        3 - 左耳 (Left Ear)
        4 - 右耳 (Right Ear)
        5 - 左肩 (Left Shoulder)
        6 - 右肩 (Right Shoulder)
        7 - 左肘 (Left Elbow)
        8 - 右肘 (Right Elbow)
        9 - 左手腕 (Left Wrist)
        10 - 右手腕 (Right Wrist)
        11 - 左髋部 (Left Hip)
        12 - 右髋部 (Right Hip)
        13 - 左膝 (Left Knee)
        14 - 右膝 (Right Knee)
        15 - 左脚踝 (Left Ankle)
        16 - 右脚踝 (Right Ankle)

        3-1-0-2-4 构成 头部 (Head)
        5-6-12-11-5 构成 躯干 (Torso)
        5-7-9 或 6-8-10 构成 上肢 (Upper Limbs)
        11-13-15 或 12-14-16 构成 下肢 (Lower Limbs)
        """
        keypoints = np.array(keypoints_17).reshape((-1, 2))
        assert(keypoints.shape == (17,2))

        kp_map = {}
        kp_map['Nose'] = keypoints[0]         # 鼻子
        kp_map['Left Eye'] = keypoints[1]     # 左眼
        kp_map['Right Eye'] = keypoints[2]    # 右眼
        kp_map['Left Ear'] = keypoints[3]     # 左耳
        kp_map['Right Ear'] = keypoints[4]    # 右耳
        kp_map['Left Shoulder'] = keypoints[5] # 左肩
        kp_map['Right Shoulder'] = keypoints[6] # 右肩
        kp_map['Left Elbow'] = keypoints[7]   # 左肘
        kp_map['Right Elbow'] = keypoints[8]  # 右肘
        kp_map['Left Wrist'] = keypoints[9]   # 左手腕
        kp_map['Right Wrist'] = keypoints[10] # 右手腕
        kp_map['Left Hip'] = keypoints[11]    # 左髋部
        kp_map['Right Hip'] = keypoints[12]   # 右髋部
        kp_map['Left Knee'] = keypoints[13]   # 左膝
        kp_map['Right Knee'] = keypoints[14]  # 右膝
        kp_map['Left Ankle'] = keypoints[15]  # 左脚踝
        kp_map['Right Ankle'] = keypoints[16] # 右脚踝

        self.feed_keypoints_map(kp_map)

    def feed_keypoints_map(self, keypoints_map):
        self.keypoints_map_deque.append(keypoints_map)

        def angle_vec(v1: np.ndarray, v2: np.ndarray) -> float:
            return np.degrees(np.arctan2(np.cross(v1, v2), np.dot(v1, v2)))

        # km = keypoints_map
        km = {key: sum(d[key] for d in self.keypoints_map_deque) / len(self.keypoints_map_deque) for key in self.keypoints_map_deque[0].keys()}
        status = []

        UP = (0, -1)

        hs_l = km['Left Shoulder']-km['Left Hip']
        hs_r = km['Right Shoulder']-km['Right Hip']
        hs_c = (hs_l + hs_r) / 2

        uhs_l = angle_vec(UP, hs_l)
        uhs_r = angle_vec(UP, hs_r)
        uhs_c = angle_vec(UP, hs_c)
        status += [f"<uhs: l={uhs_l:.1f}, r={uhs_r:.1f}, c={uhs_c:.1f}>"]

        if abs(uhs_c) < 30: # 上身竖直
            status += ["上身竖直"]
        elif abs(uhs_c) < 80: # 上身倾斜
            status += ["上身倾斜"]
        else: # 上身平躺
            status += ["上身平躺"]

        hk_l = km['Left Knee']-km['Left Hip']
        hk_r = km['Right Knee']-km['Right Hip']
        hk_c = (hk_l + hk_r) / 2

        shk_l = angle_vec(hs_c, hk_l)
        shk_r = angle_vec(hs_c, hk_r)
        shk_c = angle_vec(hs_c, hk_c)
        status += [f"<shk: l={shk_l:.1f}, r={shk_r:.1f}, c={shk_c:.1f}>"]

        def det_curve(ang, status):
            ang = abs(ang)
            if ang < 160: # 弯曲
                status[-1] += "弯曲"
            else: # 伸直
                status[-1] += "伸直"

        status += ["左大腿"]
        det_curve(shk_l, status)
        status += ["右大腿"]
        det_curve(shk_r, status)

        se_l = km['Left Elbow']-km['Left Shoulder']
        se_r = km['Right Elbow']-km['Right Shoulder']
        se_c = (se_l + se_r) / 2

        hse_l = angle_vec(-hs_l, se_l)
        hse_r = angle_vec(-hs_r, se_r)
        hse_c = angle_vec(-hs_c, se_c)
        status += [f"<hse: l={hse_l:.1f}, r={hse_r:.1f}, c={hse_c:.1f}>"]

        def det_hse(ang, status):
            ang = abs(ang)
            if ang < 20: # 下垂
                status[-1] += "下垂"
            elif ang < 80: # 抬起
                status[-1] += "抬起"
            elif ang < 110: # 平举
                status[-1] += "平举"
            elif ang < 160: # 举高
                status[-1] += "举高"
            else: # 上竖
                status[-1] += "上竖"

        status += ["左大臂"]
        det_hse(hse_l, status)
        status += ["右大臂"]
        det_hse(hse_r, status)

        ew_l = km['Left Wrist']-km['Left Elbow']
        ew_r = km['Right Wrist']-km['Right Elbow']
        ew_c = (ew_l + ew_r) / 2

        sew_l = angle_vec(-se_l, ew_l)
        sew_r = angle_vec(-se_r, ew_r)
        sew_c = angle_vec(-se_c, ew_c)
        status += [f"<sew: l={sew_l:.1f}, r={sew_r:.1f}, c={sew_c:.1f}>"]

        status += ["左小臂"]
        det_curve(sew_l, status)
        status += ["右小臂"]
        det_curve(sew_r, status)


        ka_l = km['Left Ankle']-km['Left Knee']
        ka_r = km['Right Ankle']-km['Right Knee']

        hka_l = angle_vec(-hk_l, ka_l)
        hka_r = angle_vec(-hk_r, ka_r)
        status += [f"<hka: l={hka_l:.1f}, r={hka_r:.1f}>"]

        status += ["左小腿"]
        det_curve(hka_l, status)
        status += ["右小腿"]
        det_curve(hka_r, status)


        sw_l = km['Left Wrist']-km['Left Shoulder']
        sw_r = km['Right Wrist']-km['Right Shoulder']
        sw_c = (sw_l + sw_r) / 2

        hsw_l = angle_vec(-hs_c, sw_l)
        hsw_r = angle_vec(-hs_c, sw_r)
        status += [f"<hsw: l={hsw_l:.1f}, r={hsw_r:.1f}"]

        status += ["综合："]
        if "上身平躺" in status:
            status += ["躺下"]
        elif "上身竖直" in status:
            if "左大腿伸直" in status or "右大腿伸直" in status:
                status += ["直立"]
            else:
                status += ["坐下"]
        else:
            if "左大腿伸直" in status or "右大腿伸直" in status: # todo: 斜躺平躺都可以弯腿。实际是二维平面投影图，应该要考虑人脸朝向（正向，背向，向左，向右。区分左右）
                status += ["斜躺"]
            else:
                status += ["坐下"]

        if "左大臂平举" in status and "左小臂伸直" in status:
            status += ["向左1"]
        if "右大臂平举" in status and "右小臂伸直" in status:
            status += ["向右1"]
        if "向左1" in status and "向右1" in status:
            del status[-1]
            del status[-1]
            status += ["双手平举"]

        if "左大臂举高" in status and "左小臂伸直" in status:
            status += ["举左手"]
        if "右大臂举高" in status and "右小臂伸直" in status:
            status += ["举右手"]
        if "举左手" in status and "举右手" in status:
            del status[-1]
            del status[-1]
            status += ["举双手"]

        if ("左大臂上竖" in status or "左大臂举高" in status) and "左小臂弯曲" in status and ("右大臂上竖" in status or "右大臂举高" in status) and "右小臂弯曲" in status:
            if abs(hsw_l) > 160 and abs(hsw_r) > 160:
                status += ["双手比心"]

        if "双手平举" in status and "左小腿伸直" in status and "右小腿伸直" in status:
            if -shk_r < 165 and -shk_r > 110 and shk_l < 165 and shk_l > 110 and abs(shk_c) > 170:
                status += ["大字型"]

        # print(status)
        self.status = status[status.index("综合：")+1:]

    def get_status(self):
        return "\n".join(self.status)


    def evaluate_pose(self, keypoints):
        self.feed_keypoints_17(keypoints)
        return self.get_status()