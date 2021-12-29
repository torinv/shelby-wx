import time
import os
import imageio
import datetime
import cv2
import threading
from collections import deque
from enum import Enum
from threading import Thread

FRAME_WIDTH = 3840
FRAME_HEIGHT = 2160

lock = threading.Lock()

class TimeLapseUnit(Enum):
    MINUTE = 1
    HOUR = 2
    DAY = 3

class TimeLapseDriver(object):
    def __init__(self, save_images_to_disk: bool=False):
        # Record
        self._save_to_disk = save_images_to_disk
        self.num_frames = 60
        self.unit = TimeLapseUnit.MINUTE

        # Playback
        self.fps = 15
        self.retain_frames = 1000

        self._frame_queue = deque()
        self._temp_path = os.path.join('./static', 'time_lapse.gif')

        self._counter = 0
        self._seconds_to_wait = self._calculate_seconds_to_wait(self.num_frames, self.unit)

        # Stream
        self._capture_url = 'rtsp://' + \
            os.environ['CAM_USER'] + ':' + \
            os.environ['CAM_PASSWORD'] + \
            '@192.168.1.246:554/cam/realmonitor?channel=1&subtype=0'
        self._latest_frame = None

        self._capture_thread = Thread(target=self._get_latest_frame)
        self._capture_thread.daemon = True
        self._capture_thread.start()

        # Empty out frame buffer
        for file in os.listdir('./frames'):
            os.remove(os.path.join('./frames', file))

    def __del__(self):
        self._capture_thread.join()

    def _get_latest_frame(self):
        cam_stream = cv2.VideoCapture(self._capture_url)
        while True:
            status, frame = cam_stream.read()
            if status:
                self._latest_frame = frame
            time.sleep(1)

    def _trim_frame_queue(self):
        if len(self._frame_queue) > self.retain_frames:
            if self._save_to_disk:
                os.remove(self._frame_queue.popleft())
            else:
                self._frame_queue.popleft()

    def run(self):
        while True:
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
            self._trim_frame_queue()
        lock.release()

        self.retain_frames = retain
        self._seconds_to_wait = self._calculate_seconds_to_wait(self.num_frames, self.unit)

    def take_snapshot(self):
        if self._latest_frame is not None:
            if self._save_to_disk:
                self.save_snapshot_disk()
            else:
                self.save_snapshot_ram()

    def save_snapshot_ram(self):
        lock.acquire()
        self._frame_queue.append(self._latest_frame)
        self._trim_frame_queue()
        lock.release()

    def save_snapshot_disk(self):
        frame_file = './frames/' + str(datetime.datetime.now()) + '.jpeg'

        lock.acquire()
        self._frame_queue.append(frame_file)
        self._trim_frame_queue()
        lock.release()

        cv2.imwrite(frame_file, self._latest_frame)

    def gen_time_lapse_preview(self):
        if len(self._frame_queue) == 0:
            return None

        self._delete_time_lapse()

        lock.acquire()
        with imageio.get_writer(self._temp_path, mode='I', duration=1 / self.fps) as writer:
            for image in self._frame_queue:
                writer.append_data(cv2.resize(image, (640, 360)))
        lock.release()

        return 'time_lapse.gif'

    def save_time_lapse(self):
        writer = cv2.VideoWriter(
            os.path.join('./movies', str(datetime.datetime.now()) + '.mp4'),
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.fps,
            (FRAME_WIDTH, FRAME_HEIGHT)
        )

        if self._save_to_disk:
            self.gen_time_lapse_disk(writer)
        else:
            self.gen_time_lapse_ram(writer)

        writer.release()

    def gen_time_lapse_ram(self, writer):
        lock.acquire()
        for img in self._frame_queue:
            writer.write(img)
        lock.release()

    def gen_time_lapse_disk(self, writer):
        img_arr = []
        lock.acquire()
        for image in self._frame_queue:
            img_arr.append(cv2.imread(image))
        lock.release()

        for img in img_arr:
            writer.write(img)

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
