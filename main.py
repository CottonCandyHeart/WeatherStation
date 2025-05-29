from flask import Flask, jsonify, render_template
from mqtt_client import start_mqtt, latest_data

from mqtt_client import start_mqtt, latest_data, get_daily_averages

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify(latest_data)

@app.route('/history')
def get_averages():
    return jsonify(get_daily_averages())

if __name__ == '__main__':
    start_mqtt()
    app.run(debug=True)