import os
import time
import json


from flask import Flask, request, Response, jsonify, render_template, redirect, url_for, send_from_directory, \
    stream_with_context
from flask_cors import CORS

from utils.functions import *  # Import all functions from functions.py
from utils.gemini import GeminiModel

import yaml  # Ensure this is installed and imported

app = Flask(__name__)
CORS(app)

"""basic functions"""
@app.route("/")
def index():
    """Launch file index.html on main page"""
    try:
        return render_template("index.html")
    except Exception as e:
        app.logger.error(f"Error rendering index.html: {e}")
        return jsonify({"error": "Unable to load the page. Probably index.html is missing"}), 500



@app.route("/locales/<path:filename>")
def serve_locale(filename):
    """Send localization json files (en.json&fi.json) from the 'locales' directory."""
    return send_from_directory("locales", filename)

@app.route('/static/videos/<filename>')
def serve_video(filename):
    """Serve static vidoe files from the 'static' directory."""
    return send_from_directory('static/videos', filename, mimetype='video/mp4')


# Static files route
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from the 'static' directory."""
    try:
        return send_from_directory(os.path.join(app.root_path, 'static'), filename)
    except Exception as e:
        app.logger.error(f"Error serving static file {filename}: {e}")
        return jsonify({"error": f"Unable to serve {filename}"}), 500

@app.route("/scraped_companies", methods=["GET"])
def get_scraped_companies():
    """
    Endpoint to retrieve scraped companies data.
    """
    try:
        scraped_companies = load_scraped_companies()
        return jsonify({"status": "success", "data": scraped_companies})
    except FileNotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/process", methods=["POST"])
def process_data():
    try:
        data = request.json
        prompts = load_prompts()
        gemini_model = GeminiModel(model_name="gemini-1.5-flash")

        def generate_responses():
            yield '{"status": "success", "results": ['  # Initial JSON structure
            first = True
            for company_name, company_info in data.items():
                if not first:
                    yield ','
                first = False

                time.sleep(3)
                scraped_data = f"""
                Company Name: {company_name}
                Industry: {company_info.get('mainBusinessLine', 'N/A')}
                Website: {company_info.get('url', 'N/A')}
                """
                analysis, sales_leads = process_company(scraped_data, gemini_model, prompts)
                result = {
                    "company_name": company_name,
                    "analysis": analysis,
                    "sales_leads": sales_leads
                }
                yield json.dumps(result)
            yield ']}'

        return Response(stream_with_context(generate_responses()), content_type="application/x-ndjson")
    except Exception as e:
        app.logger.error(f"Error in /process: {e}")
        return jsonify({"status": "error", "message": str(e)})






@app.errorhandler(404)
def page_not_found(e):
    """404 error handler."""
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler."""
    return jsonify({"error": "Internal server error. "}), 500

if __name__ == "__main__":
    # Launch flask in localhost, in debug mode.
    app.run(host="127.0.0.1", port=5000, debug=True)
    # Can be launched in host="0.0.0.0" in order to check by using other devices in the same network