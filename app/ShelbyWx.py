import yaml
from flask import Flask, render_template, jsonify, request
from TimeLapseDriver import TimeLapseDriver
from threading import Thread
from ambient_api.ambientapi import AmbientAPI

app = Flask(__name__)
api = AmbientAPI()

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

        time_lapse_driver.update_params(
            int(request.form['frames']),
            int(request.form['units']),
            int(request.form['fps']),
            int(request.form['retain'])
        )

    return render_template('index.html')

@app.route('/_update_wx_data', methods=['GET'])
def update_wx_data():
    device = api.get_devices()[0]
    return device.get_data()

@app.route('/_get_latest_time_lapse', methods=['GET'])
def get_latest_time_lapse():
    time_lapse = time_lapse_driver.gen_time_lapse()
    if time_lapse is None:
        return {}
    return jsonify(src='/static/' + time_lapse)

@app.route('/_get_time_lapse_params', methods=['GET'])
def get_time_lapse_params():
    return jsonify(
        num_frames=time_lapse_driver.num_frames,
        unit=time_lapse_driver.unit.value, 
        fps=time_lapse_driver.fps,
        retain=time_lapse_driver.retain_frames
    )

if __name__ == '__main__':
    # Setup env vars
    keys = yaml.load(open('./keys.yml', 'r'), Loader=yaml.Loader)

    Thread(target=time_lapse_driver.run).start()
    Thread(target=app.run).start()
