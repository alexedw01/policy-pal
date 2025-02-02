
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/congress')
def get_congress_data():
    response = requests.get('https://api.congress.gov/v3/bill?api_key=YOUR_API_KEY')
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)

