from flask import Flask, jsonify, render_template
from mqtt_client import start_mqtt, latest_data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify(latest_data)

if __name__ == '__main__':
    start_mqtt()
    app.run(debug=True)