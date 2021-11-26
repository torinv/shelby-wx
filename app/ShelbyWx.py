from flask import Flask, render_template
from flask_cors import CORS
from TimeLapseDriver import TimeLapseDriver
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
