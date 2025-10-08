import requests
import pandas as pd
import json
import time
from datetime import datetime
import os
import webbrowser

# --- Configuration ---
WP_API_BASE_URL = "https://preprintwatch.com/wp-json/pw-kgx3/v1/submit"
CSV_FILE_PATH = "test_data.csv" # Ensure this file is uploaded to your Colab environment
OUTPUT_LOG_FILE = "test_results.log"
REPORT_FILE_PATH = f"API_Performance_Report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html"

# --- Helper Function for Logging ---
def log_message(message, level="INFO"):
    """Logs a message to both the console and a log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry) # Print to Colab output
    with open(OUTPUT_LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

# --- HTML Report Generation Module ---
def generate_html_report(results, summary):
    """Generates a complete, standardized HTML report from the test results."""
    # Helper function to determine row color based on status
    def get_status_color(passed):
        return "#d4edda" if passed else "#f8d7da"

    # Build the detailed results table rows
    results_rows_html = ""
    for result in results:
        results_rows_html += f"""
        <tr style="background-color: {get_status_color(result['passed'])}">
            <td>{result['test_case']}</td>
            <td>{result['status_code']}</td>
            <td>{f"{result['response_time']:.4f}s" if result['response_time'] is not None else 'N/A'}</td>
            <td>{'PASS' if result['passed'] else 'FAIL'}</td>
        </tr>
        """

    # Build the status code distribution table rows
    status_dist_html = ""
    for code, count in summary['status_code_distribution'].items():
        status_dist_html += f"<tr><td>{int(code) if isinstance(code, float) else code}</td><td>{count}</td></tr>"


    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Performance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
            .container {{ max-width: 900px; margin: auto; border: 1px solid #ddd; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }}
            h1, h2 {{ color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .summary-card {{ background-color: #f8f9fa; border-left: 5px solid #0056b3; padding: 15px; margin: 20px 0; }}
            .print-button {{
                display: block; width: 150px; margin: 20px auto; padding: 10px 15px;
                background-color: #007bff; color: white; text-align: center;
                border: none; border-radius: 5px; cursor: pointer; font-size: 16px;
            }}
            @media print {{
                .print-button {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>KGX3 Performance Report - PW Shared Endpoint</h1>
            <p><strong>Report Generated On:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <button class="print-button" onclick="window.print()">Save as PDF</button>

            <h2>Overall Summary</h2>
            <div class="summary-card">
                <p><strong>Total Tests:</strong> {summary['total_requests']}</p>
                <p><strong>Tests Passed:</strong> {summary['successful_requests']}</p>
                <p><strong>Tests Failed:</strong> {summary['failed_requests']}</p>
                <p><strong>Success Rate:</strong> {summary['success_rate']:.2f}%</p>
                <p><strong>Total Duration:</strong> {summary['total_duration']:.2f} seconds</p>
                <p><strong>Requests Per Second (RPS):</strong> {summary['requests_per_second']:.2f}</p>
            </div>

            <h2>Response Time Statistics (seconds)</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Minimum</td><td>{summary['min_response_time']:.4f}s</td></tr>
                <tr><td>Maximum</td><td>{summary['max_response_time']:.4f}s</td></tr>
                <tr><td>Average</td><td>{summary['avg_response_time']:.4f}s</td></tr>
            </table>

            <h2>Status Code Distribution</h2>
            <table>
                <tr><th>Status Code</th><th>Count</th></tr>
                {status_dist_html}
            </table>

            <h2>Detailed Test Results</h2>
            <table>
                <tr><th>Test Case Name</th><th>Status Code</th><th>Response Time</th><th>Result</th></tr>
                {results_rows_html}
            </table>
        </div>
    </body>
    </html>
    """
    try:
        with open(REPORT_FILE_PATH, 'w') as f:
            f.write(html_content)
        log_message(f"Successfully generated HTML report: {REPORT_FILE_PATH}", level="SUCCESS")
        # Automatically open the report in a new browser tab
        webbrowser.open('file://' + os.path.realpath(REPORT_FILE_PATH))
    except Exception as e:
        log_message(f"Error generating HTML report: {e}", level="ERROR")


# --- Main Test Function ---
def run_tests():
    if os.path.exists(OUTPUT_LOG_FILE):
        os.remove(OUTPUT_LOG_FILE)
    with open(OUTPUT_LOG_FILE, "w") as f:
        f.write(f"--- API Test Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")

    log_message(f"Starting API tests against: {WP_API_BASE_URL}")

    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except FileNotFoundError:
        log_message(f"Error: CSV file not found at {CSV_FILE_PATH}. Please upload it.", level="ERROR")
        return

    total_tests = len(df)
    results_collector = []
    suite_start_time = time.time()

    for index, row in df.iterrows():
        test_case_name = row.get('test_case_name', f"Test Case {index + 1}")
        # ... (rest of the test execution logic is the same)
        api_key = row['api_key']
        title = row['title']
        pdf_url = row['pdf_url']
        email = row['email'] if pd.notna(row['email']) else ""
        expected_status = int(row['expected_status']) if pd.notna(row['expected_status']) else None

        log_message(f"Running Test: {test_case_name} (Row {index + 1}/{total_tests})")

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": str(api_key)
        }
        if not api_key:
            headers.pop("X-API-Key", None)

        payload = {"title": title, "pdf_url": pdf_url, "email": email}

        response_time = None
        actual_status = None
        test_passed = False

        try:
            start_time = time.time()
            response = requests.post(WP_API_BASE_URL, headers=headers, data=json.dumps(payload), timeout=200)
            end_time = time.time()
            response_time = end_time - start_time
            actual_status = response.status_code
            test_passed = (actual_status == expected_status)
            if test_passed:
                 log_message(f"  PASS: Status code matches for '{test_case_name}'", level="SUCCESS")
            else:
                 log_message(f"  FAIL: Status code MISMATCH for '{test_case_name}'", level="ERROR")
                 try:
                      log_message(f"    Response Body: {json.dumps(response.json(), indent=2)}", level="ERROR")
                 except json.JSONDecodeError:
                      log_message(f"    Raw Response Body: {response.text[:500]}", level="ERROR")


        except requests.exceptions.Timeout:
            log_message(f"  FAIL: Request timed out for '{test_case_name}'", level="ERROR")
            actual_status = "Timeout"
        except requests.exceptions.RequestException as e:
            log_message(f"  FAIL: Request error for '{test_case_name}': {e}", level="ERROR")
            actual_status = "Request Error"

        results_collector.append({
            'test_case': test_case_name,
            'status_code': actual_status,
            'response_time': response_time,
            'passed': test_passed
        })
        time.sleep(1)

    total_suite_duration = time.time() - suite_start_time

    # --- Analysis and Reporting ---
    results_df = pd.DataFrame(results_collector)
    total_requests = len(results_df)
    successful_requests = results_df['passed'].sum()
    response_times = results_df[results_df['response_time'].notna()]['response_time']

    summary_data = {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": total_requests - successful_requests,
        "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
        "total_duration": total_suite_duration,
        "requests_per_second": total_requests / total_suite_duration if total_suite_duration > 0 else 0,
        "min_response_time": response_times.min() if not response_times.empty else 0,
        "max_response_time": response_times.max() if not response_times.empty else 0,
        "avg_response_time": response_times.mean() if not response_times.empty else 0,
        "status_code_distribution": results_df['status_code'].value_counts().to_dict()
    }

    # --- Generate and save the HTML report ---
    generate_html_report(results_collector, summary_data)


# Run the tests
run_tests()
