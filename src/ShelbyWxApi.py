from flask import Flask
from flask_restful import Resource, Api
from TimeLapseDriver import TimeLapseDriver
import json

app = Flask(__name__)
api = Api(app)

class TestWxApi(Resource):
    def get(self):
        return json.load(open('./test/test_data_event.json'))

class SaveTimeLapse(Resource):
    def post(self):
        TimeLapseDriver.save_time_lapse()
        return 200

api.add_resource(TestWxApi, '/test-wx-api')
api.add_resource(SaveTimeLapse, '/save-time-lapse')

if __name__ == '__main__':
    app.run(debug=True)
