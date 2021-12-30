import os
import requests
from pytz import timezone
from datetime import datetime as dt
from flask import Flask, render_template, jsonify, request
from TimeLapseDriver import TimeLapseDriver
from threading import Thread

app = Flask(__name__)
api_string = 'https://rt.ambientweather.net/v1/devices?applicationKey=' + \
    os.environ['AMBIENT_APPLICATION_KEY'] + \
    '&apiKey=' + os.environ['AMBIENT_API_KEY']

time_lapse_driver = TimeLapseDriver()

@app.route('/', methods=['GET', 'POST'])
def index_save_time_lapse():
    if request.form.get('save') == 'Save Time Lapse':
        Thread(target=time_lapse_driver.save_time_lapse).start()

    if request.form.get('update') == 'Update':
        try:
            int(request.form['frames'])
        except:
            pass

        time_lapse_driver.update_params(
            int(request.form['frames']),
            int(request.form['units']),
            int(request.form['fps']),
            int(request.form['retain'])
        )

    return render_template('index.html')

@app.route('/_update_wx_data', methods=['GET'])
def update_wx_data():
    resp = requests.get(api_string)
    if resp.status_code == 200:
        weather_data = resp.json()[0]['lastData']

        timestamp = dt.fromtimestamp(weather_data['dateutc'] // 1000)
        tz = timezone('America/Los_Angeles')
        timestamp = tz.localize(timestamp)
        formatted_timestamp = timestamp.strftime("%I:%M %p %Z")
        weather_data['dateutc'] = formatted_timestamp

        return jsonify(weather_data)
    return {}

@app.route('/_get_time_lapse_params', methods=['GET'])
def get_time_lapse_params():
    return jsonify(
        num_frames=time_lapse_driver.num_frames,
        unit=time_lapse_driver.unit.value, 
        fps=time_lapse_driver.fps,
        retain=time_lapse_driver.retain_frames
    )


if __name__ == '__main__':
    Thread(target=time_lapse_driver.run).start()
    Thread(target=app.run, args=['0.0.0.0']).start()
