from flask import Flask, jsonify, render_template, request
import requests
import time
import subprocess
from helpers.xml_helper import extract_sid_from_xml, extract_dispatch_state_from_xml


app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')


# Update the SPLUNK_URL to use host.docker.internal
SPLUNK_URL = "https://host.docker.internal:8089" 
auth = ("pratik", "Splunk@123")

# Route to fetch data from Splunk
@app.route("/fetch_data", methods=["GET"])
def fetch_data():
    search_query = "Search index=predictrix | table user_id, page, location, event, device"

    search_job_url = f"{SPLUNK_URL}/services/search/jobs"
    params = {
        "search": search_query, 
        "output_mode": "json"
    }
    headers = {'Accept': 'application/json'}
    
    response = requests.post(search_job_url, auth=auth, data=params, headers=headers, verify=False)

    if response.status_code != 201:
        return jsonify({"error": f"Failed to create search job: {response.text}"}), 500

    if 'application/json' in response.headers.get('Content-Type', ''):
        try:
            search_job = response.json()
            sid = search_job.get('sid')
        except ValueError as e:
            return jsonify({"error": f"Failed to parse JSON response: {e}, Response: {response.text}"}), 500
    elif 'application/xml' in response.headers.get('Content-Type', '') or 'text/xml' in response.headers.get('Content-Type', ''):
        try:
            namespaces = {'s': 'http://dev.splunk.com/ns/rest'}
            sid = extract_sid_from_xml(response.text, namespaces)
        except Exception as e:
            return jsonify({"error": f"Failed to parse XML response: {e}, Response: {response.text}"}), 500
    else:
        return jsonify({"error": "Unsupported response format"}), 500

    if not sid:
        return jsonify({"error": "Search job ID not returned"}), 500

    status_url = f"{SPLUNK_URL}/services/search/jobs/{sid}"
    headers = {'Accept': 'application/xml'}

    for _ in range(30):
        status_response = requests.get(status_url, auth=auth, headers=headers, verify=False)
        if status_response.status_code == 200:
            if 'application/xml' in status_response.headers.get('Content-Type', '') or 'text/xml' in status_response.headers.get('Content-Type', ''):
                try:
                    namespaces = {'s': 'http://dev.splunk.com/ns/rest'}
                    dispatch_state = extract_dispatch_state_from_xml(status_response.text, namespaces)
                    if dispatch_state == 'DONE':
                        break
                    elif dispatch_state == 'FAILED':
                        return jsonify({"error": "Search job failed."}), 500
                    elif dispatch_state == 'CANCELED':
                        return jsonify({"error": "Search job was canceled."}), 500
                except Exception as e:
                    return jsonify({"error": f"Error parsing XML in status response: {e}, Response: {status_response.text}"}), 500
            else:
                return jsonify({"error": f"Unexpected content type in status response: {status_response.headers.get('Content-Type')}"}), 500
        else:
            return jsonify({"error": f"Error fetching status: {status_response.text}"}), 500
        time.sleep(10)

    results_url = f"{SPLUNK_URL}/services/search/jobs/{sid}/results"
    results_response = requests.get(results_url, auth=auth, params={"output_mode": "json"}, headers=headers, verify=False)

    if results_response.status_code == 200:
        if 'application/json' in results_response.headers.get('Content-Type', ''):
            results = results_response.json().get('results', [])
            return render_template("data.html", results=results)
        else:
            return jsonify({"error": "Unexpected response format, expected JSON."}), 500
    else:
        return jsonify({"error": f"Failed to fetch search results: {results_response.text}"}), 500

# Route to handle the button click from the website to push data to Splunk
import logging

@app.route('/push-data', methods=['POST'])
def push_data():
    try:
        # Log the start of the process
        app.logger.info("Attempting to run the Python script to push data to Splunk")
        
        # Run your existing Python script to push data to Splunk
        result = subprocess.run([r'python', r'/app/api/predictrix.py'], capture_output=True, text=True)
        
        # Log the result of the script
        app.logger.info(f"Script output: {result.stdout}")
        
        # If the script ran successfully, return success message
        if result.returncode == 0:
            return jsonify({"message": "Data successfully sent to Splunk!"})
        else:
            app.logger.error(f"Error in script execution: {result.stderr}")
            return jsonify({"message": f"Error: {result.stderr}"}), 500
    except Exception as e:
        # Log the exception
        app.logger.error(f"Exception occurred: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Route for the root URL
@app.route('/')
def index():
    return render_template('data.html')  # Ensure data.html is in the templates folder

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)
