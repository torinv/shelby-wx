import asyncio

class TimeLapseDriver(object):
    @staticmethod
    async def run():
        while(True):
            await asyncio.sleep(1)
            print("Hello world")

    @staticmethod
    def save_time_lapse():
        pass