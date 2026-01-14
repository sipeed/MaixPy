## 简介
本应用是一款运行于MaixPy 实现了基于 YOLOv8-Pose / YOLO11-Pose 的人体姿态检测，可以检测到人体17个关键点。能够实时采集摄像头画面并完成人体姿态关键点识别与展示，操作简洁、运行高效，适用于快速人体姿态捕捉、简易运动分析等场景。

## 主要功能
![](./assets/body_keypoints.jpg)
1.  设备兼容性：本应用针对MaixCam系列设备开发，其中MaixCam2设备使用YOLO11模型，MaixCam/Pro备使用YOLOv8模型
2.  实时摄像头采集：自动调用设备摄像头，获取高清实时画面，画面分辨率适配姿态检测模型需求。
3.  人体姿态检测与识别：基于预加载的姿态检测模型，自动识别画面中的人体目标，筛选置信度符合要求的检测结果。
4.  检测结果可视化：在实时画面上标注人体目标矩形框、目标类别及置信度评分，同时绘制人体关键姿态点连线。
5.  自动检测人体17个关键点:
    ```
    1. 鼻子（Nose）
    2. 左眼（Left Eye）
    3. 右眼（Right Eye）
    4. 左耳（Left Ear）
    5. 右耳（Right Ear）
    6. 左肩（Left Shoulder）
    7. 右肩（Right Shoulder）
    8. 左肘（Left Elbow）
    9. 右肘（Right Elbow）
    10. 左手腕（Left Wrist）
    11. 右手腕（Right Wrist）
    12. 左髋（Left Hip）
    13. 右髋（Right Hip）
    14. 左膝（Left Knee）
    15. 右膝（Right Knee）
    16. 左脚踝（Left Ankle）
    17. 右脚踝（Right Ankle）
    ```

## 更多
[源码](https://github.com/sipeed/MaixPy/tree/main/projects/app_human_pose)
[MaixCAM MaixPy 检测人体关键点姿态检测](https://wiki.sipeed.com/maixpy/doc/zh/vision/body_key_points.html)