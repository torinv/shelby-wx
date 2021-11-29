from flask import Flask, render_template, jsonify, request
from TimeLapseDriver import TimeLapseDriver, TimeLapseUnit
import json
from threading import Thread

app = Flask(__name__)

time_lapse_driver = TimeLapseDriver()

@app.route('/', methods=['GET', 'POST'])
def index_save_time_lapse():
    if request.form.get('save') == 'Save Time Lapse':
        time_lapse_driver.save_time_lapse()

    if request.form.get('update') == 'Update':
        try:
            int(request.form['frames'])
        except:
            pass

        time_lapse_driver.update_params(int(request.form['frames']), int(request.form['units']))

    return render_template('index.html')

@app.route('/_update_wx_data', methods=['GET'])
def update_wx_data():
    # TODO: requests.get the actual AW API here
    return json.load(open('./test_data_event.json', 'r'))

@app.route('/_get_latest_time_lapse', methods=['GET'])
def get_latest_time_lapse():
    return {}

@app.route('/_get_time_lapse_params', methods=['GET'])
def get_time_lapse_params():
    return jsonify(num_frames=time_lapse_driver.num_frames, unit=time_lapse_driver.unit.value)


if __name__ == '__main__':
    Thread(target=time_lapse_driver.run).start()
    Thread(target=app.run).start()
