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
        # Parse the incoming request data
        request_data = request.json
        user_input = request_data.get("userInput", "").strip()
        app.logger.debug(f"DEBUG: Received user input: {user_input}")
        if not user_input:
            app.logger.warning("WARN: User input is empty. Ensure the frontend is sending the correct value.")

        # Load prompts and initialize the AI model
        app.logger.debug("DEBUG: Loading prompts and initializing AI model.")
        prompts = load_prompts()
        gemini_model = GeminiModel()

        results = []
        total_companies = len(request_data.get("companies", {}))
        app.logger.debug(f"DEBUG: Total companies to process: {total_companies}")

        # Function to process and generate responses for each company
        def process_companies():
            for index, (company_name, company_info) in enumerate(request_data.get("companies", {}).items(), start=1):
                try:
                    app.logger.debug(f"DEBUG: Processing company {index}/{total_companies}: {company_name}")

                    # Prepare scraped data (only company-specific information)
                    scraped_data = json.dumps(company_info, indent=2)
                    app.logger.debug(f"DEBUG: Prepared scraped data for {company_name}: {scraped_data}")

                    # Call process_company to get results
                    analysis, sales_leads, probability_html, probability_value = process_company(
                        scraped_data, user_input, gemini_model, prompts
                    )
                    app.logger.debug(f"DEBUG: Successfully processed {company_name}.")

                    # Append results to the list
                    results.append({
                        "company_name": company_name,
                        "analysis": analysis,
                        "sales_leads": sales_leads,
                        "partnership_probability": probability_value,
                        "probability_html": probability_html,  # Include HTML for display
                    })
                except Exception as company_error:
                    app.logger.error(f"Error processing company {company_name}: {company_error}")
                    continue  # Skip to the next company in case of an error

        # Process the companies and sort the results by partnership probability
        app.logger.debug("DEBUG: Starting company processing.")
        process_companies()
        app.logger.debug("DEBUG: Finished processing all companies.")

        sorted_results = sorted(results, key=lambda x: x["partnership_probability"], reverse=True)
        app.logger.debug("DEBUG: Results sorted by partnership probability.")

        # Return the sorted results
        return jsonify({"status": "success", "results": sorted_results})
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