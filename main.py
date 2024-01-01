import os
import requests
from flask import request, Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})




@app.route('/', methods=['POST'])
def upload():
    try:
        pod_ip = request.form.get('podIp')
        pod_password = request.form.get('podPassword')

        # Access the file data using request.files
        uploaded_file = request.files['LICENSE_pkg']


        if not pod_ip:
            return jsonify({"status": 400, "message": "Please provide Pod IP address"}), 400

        if not uploaded_file:
            return jsonify({"status": 400, "message": "Please select a license file"}), 400

        url = f"https://{pod_ip}/Config/service/uploadLicense"

        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
        }

        # Create a dictionary with authentication details
        auth = ('admin', pod_password)

        # Make the requests POST with file data
        response = requests.post(url,verify=False, files={'LICENSE_pkg': (uploaded_file.filename, uploaded_file.read())}, auth=auth, headers=headers)

        responseData = response.json()

        print(response.status_code)
        print(responseData)

        if responseData.get('passwordRequired', False):
            return jsonify({"status": 400, "message": "Please provide a password"}), 400

        if response.status_code == 200:
            return jsonify({"status": response.status_code, "message": responseData}), 200

        if responseData['message'] == "timeout of 5000ms exceeded":
            print(response.status_code)
            print(response)
            return jsonify({"status": response.status_code, "message": "timeout of 5000ms exceeded"}), 400

        print(responseData)
        print(response.status_code)

    except requests.exceptions.RequestException as error:
        if "timeout of 5000ms exceeded" in str(error):
            print("Error first catch:", error)
            return jsonify({"status": 400, "message": "timeout of 5000ms exceeded"}), 400
        elif "connect ENETUNREACH" in str(error):
            print("Error second catch:", error)
            return jsonify({"status": 400, "message": "can not connect"}), 400
        else:
            print("Error last catch:", error)
            return jsonify({"status": 400, "message": "socket hangs up"}), 400



@app.route("/ping", methods=['GET', 'POST'])
def test_pod():
    if request.method == "GET":
        return test_pod_func()
    elif request.method == "POST":
        # Handle POST requests
        data = request.json  # Assuming the data is sent in JSON format
        return jsonify({"message": f"Received POST request with data: {data}"})

def test_pod_func():
        return jsonify({"message": f"pong"})
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))