import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET")

@app.route("/", methods=["POST"])
def handle_gcs_event():
    event = request.get_json()
    print(event)

    if not event or "name" not in event or "bucket" not in event:
        return "Invalid event payload", 400

    filename = event["name"]
    input_bucket = event["bucket"]

    local_input_path = f"/tmp/{filename}"
    local_output_path = f"/tmp/{filename}.pdf"
    remote_output_path = f"gs://{OUTPUT_BUCKET}/{filename}.pdf"

    print("local_input_path:", local_input_path)
    print("local_output_path:", local_output_path)
    print("remote_output_path:",remote_output_path)

    print("Download the uploaded file from the input bucket")
    try:
        gs_path = f"gs://{input_bucket}/{filename}"
        subprocess.run(["gsutil", "cp", gs_path, local_input_path], check=True)
        print(f"Downloaded {gs_path} to {local_input_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading file: {e}")
        return "Failed to download file", 500

    print("Generate PDF using wkhtmltopdf")
    try:
        subprocess.run(f"wkhtmltopdf {local_input_path} {local_output_path}", shell=True)
        print(f"Generated PDF at {local_output_path}")
    except subprocess.CalledProcessError as e:
        print(f"wkhtmltopdf error: {e}")
        return "PDF generation failed", 500

    print("Upload the PDF to the output bucket")
    try:
        subprocess.run(["gsutil", "cp", local_output_path, remote_output_path], check=True)
        print(f"Uploaded PDF to {remote_output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Upload error: {e}")
        return "Upload failed", 500

    return f"Successfully processed {filename}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
