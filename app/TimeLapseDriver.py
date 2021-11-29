import time
import requests
import os
import datetime
import shutil
from enum import Enum
from requests.auth import HTTPDigestAuth

class TimeLapseUnit(Enum):
    MINUTE = 1
    HOUR = 2
    DAY = 3

class TimeLapseDriver(object):
    def __init__(self):
        self.num_frames = 1
        self.unit = TimeLapseUnit.MINUTE

        self._counter = 0
        self._seconds_to_wait = 1

    def run(self):
        while(True):
            time.sleep(1)

            if self._counter < self._seconds_to_wait:
                self._counter += 1
                continue

            self._counter = 0
            self.take_snapshot()

    def update_params(self, num_frames, unit):
        # Set new parameters and reset counter
        self.num_frames = num_frames
        self.unit = TimeLapseUnit(unit)

        self._counter = 0

        # Calculate seconds between snapshot
        if self.unit == TimeLapseUnit.MINUTE:
            self._seconds_to_wait = 60 // self.num_frames
        elif self.unit == TimeLapseUnit.HOUR:
            self._seconds_to_wait = 3600 // self.num_frames
        elif self.unit == TimeLapseUnit.DAY:
            self._seconds_to_wait = 86400 // self.num_frames

    @staticmethod
    def take_snapshot():
        url = 'http://192.168.1.250/cgi-bin/snapshot.cgi'
        response = requests.get(url, auth=HTTPDigestAuth(os.environ['CAM_USER'], os.environ['CAM_PASSWORD']))
        breakpoint()
        if response.status_code == 200:
            # TODO: this doesn't work; figure out how to save off images
            with open('../test/' + str(datetime.datetime.now()) + '.jpeg', 'wb') as f:
                shutil.copyfileobj(response.raw, f)

    @staticmethod
    def save_time_lapse():
        print("it works!!")

    @staticmethod
    def get_latest_time_lapse():
        pass