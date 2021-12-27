import time
import os
import shutil
import datetime
import cv2
import threading
from collections import deque
from enum import Enum
from threading import Thread

lock = threading.Lock()

class TimeLapseUnit(Enum):
    MINUTE = 1
    HOUR = 2
    DAY = 3

class TimeLapseDriver(object):
    def __init__(self):
        # Record
        self.num_frames = 60
        self.unit = TimeLapseUnit.MINUTE

        # Playback
        self.fps = 15
        self.retain_frames = 1000

        self._frame_queue = deque()
        self._temp_path = os.path.join('./static', 'time_lapse.mp4')

        self._counter = 0
        self._seconds_to_wait = self._calculate_seconds_to_wait(self.num_frames, self.unit)

        # Stream
        cap_url = 'rtsp://' + \
            os.environ['CAM_USER'] + ':' + \
            os.environ['CAM_PASSWORD'] + \
            '@192.168.1.246:554/cam/realmonitor?channel=1&subtype=0'
        self._cam_stream = cv2.VideoCapture(cap_url)
        self._latest_frame = None

        self._cap_thread = Thread(target=self._get_latest_frame())
        self._cap_thread.daemon = True
        self._cap_thread.start()

        # Empty out frame buffer
        for file in os.listdir('./frames'):
            os.remove(os.path.join('./frames', file))

    def __del__(self):
        self._cam_stream.release()
        self._cap_thread.join()

    def _get_latest_frame(self):
        status, frame = self._cam_stream.read()
        if status:
            self._latest_frame = frame

    def run(self):
        while(True):
            time.sleep(1)

            # Count up to the next snapshot
            if self._counter < self._seconds_to_wait:
                self._counter += 1
                continue

            # Take snapshot and reset counter
            self._counter = 0
            self.take_snapshot()

    def update_params(self, num_frames, unit, fps, retain):
        # Set new parameters and reset counter
        self.num_frames = num_frames
        self.fps = fps
        self.unit = TimeLapseUnit(unit)

        self._counter = 0

        # Reset frame deque if it changed sizes
        lock.acquire()
        if retain < self.retain_frames:
            while len(self._frame_queue) > retain:
                os.remove(self._frame_queue.popleft())
        lock.release()

        self.retain_frames = retain
        self._seconds_to_wait = self._calculate_seconds_to_wait(self.num_frames, self.unit)

    def take_snapshot(self):
        frame_file = './frames/' + str(datetime.datetime.now()) + '.jpeg'

        if self._latest_frame is not None:
            lock.acquire()
            self._frame_queue.append(frame_file)
            if len(self._frame_queue) > self.retain_frames:
                os.remove(self._frame_queue.popleft())
            lock.release()

            cv2.imwrite(frame_file, self._latest_frame)
            self._cam_stream.release()

    def save_time_lapse(self):
        if os.path.exists(self._temp_path):
            shutil.copy2(self._temp_path, os.path.join('./movies', str(datetime.datetime.now()) + '.mp4'))

    def gen_time_lapse(self):
        if len(self._frame_queue) == 0:
            return None

        self._delete_time_lapse()

        img_arr = []
        img = cv2.imread(self._frame_queue[0])
        height, width, _ = img.shape

        lock.acquire()
        for image in self._frame_queue:
            img_arr.append(cv2.imread(image))
        lock.release()

        writer = cv2.VideoWriter(
            self._temp_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.fps,
            (width, height)
        )

        for img in img_arr:
            writer.write(img)

        writer.release()
        return 'time_lapse.mp4'

    def _delete_time_lapse(self):
        if os.path.exists(self._temp_path):
            os.remove(self._temp_path)

    @staticmethod
    def _calculate_seconds_to_wait(num_frames: int, unit: TimeLapseUnit) -> int:
        # Calculate seconds between snapshots
        if unit == TimeLapseUnit.MINUTE:
            return 60 // num_frames
        elif unit == TimeLapseUnit.HOUR:
            return 3600 // num_frames
        elif unit == TimeLapseUnit.DAY:
            return 86400 // num_frames
