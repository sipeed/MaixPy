---
title: MaixCAM MaixPy Object Tracking and Counting (e.g., Pedestrian Counting)
---

## Introduction to Object Tracking

Previously, we used YOLOv5, YOLOv8, or even `find_blobs` to detect objects. However, when there are multiple objects in the frame and we need to distinguish between each object, object tracking becomes necessary.

For instance, if there are five people moving in the frame, we need to assign each person a number and track their movement.

Applications:
* Pedestrian counting, such as counting the number of people passing through a certain area.
* Counting workpieces, such as counting products on a production line.
* Recording and recognizing the movement trajectories of objects.

## MaixCAM/MaixPy Object Tracking and Pedestrian Counting Results

As shown in the video below, the system can track each person and count those who cross the yellow area from top to bottom (displayed in the lower-left corner):

<video playsinline controls autoplay loop muted preload src="/static/video/tracker.mp4" style="width: 100%; min-height: 20em;"></video>

## Using MaixCAM/MaixPy for Object Tracking and Pedestrian Counting

You can directly install the [application](https://maixhub.com/app/61) to experience it.
You can also check the [examples in the `examples/vision/tracker` directory](https://github.com/sipeed/MaixPy/tree/main/examples/vision/tracker).

The `tracker_bytetrack.py` example is a basic object tracking example and involves several steps:
* Use YOLOv5 or YOLOv8 to detect objects. This allows you to replace the model to detect different objects according to your needs.
* Use the `maix.tracker.ByteTracker` algorithm for object tracking. Simply calling the `update` function will give you the results (the trajectory of each object in the frame), which is very straightforward.

Several parameters need to be adjusted according to your specific scenario. Refer to the example code and API documentation for detailed parameter descriptions:
```python
# configs
conf_threshold = 0.3       # detection threshold
iou_threshold = 0.45       # detection IOU threshold
max_lost_buff_time = 120   # the number of frames to keep lost tracks
track_thresh = 0.4         # tracking confidence threshold
high_thresh = 0.6          # threshold to add a new track
match_thresh = 0.8         # matching threshold for tracking; if IOU < match_thresh between an object in two frames, they are considered the same object
max_history_num = 5        # maximum length of a track's position history
show_detect = False        # show detection
valid_class_id = [0]       # classes used in the detection model
```

The `tracker_bytetrack_count.py` example adds pedestrian counting. To keep it simple, the example only implements counting for people walking from top to bottom. If a person is below the yellow area and their trajectory crosses into the yellow area, they are counted as crossing from top to bottom. You can write custom logic based on your specific application scenario.

