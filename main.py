# This Code has been edited by Mackenzie Falla
# Cloud Native Development
# Skeleton given by Professor Ricardo De Andrade, I also looked to ChatGBT for help as well.

"""
############################
# 1st phase - all in 1 app #
############################
1. flask hello world

2. add other flask endpoints

3. hard code responses

4. look up how to accept only POST (GET is default)

5. return html for GET /
<form method="post" enctype="multipart/form-data" action="/upload" method="post">
  <div>
    <label for="file">Choose file to upload</label>
    <input type="file" id="file" name="form_file" accept="image/jpeg"/>
  </div>
  <div>
    <button>Submit</button>
  </div>
</form>

6. in GET /files return a hardcoded list for initial testing
files = ['file1.jpeg', 'file2.jpeg', 'file3.jpeg']

7. in GET / call the function for GET /files and loop through the list to add to the HTML
GET /
    ...
    for file in list_files():
        index_html += "<li><a href=\"/files/" + file + "\">" + file + "</a></li>"

    return index_html

8. in POST /upload - lookup how to extract uploaded file and save locally to ./files
def upload():
    file = request.files['form_file']  # item name must match name in HTML form
    file.save(os.path.join("./files", file.filename))

    return redirect("/")
#https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/

9. in GET /files - look up how to list files in a directory

    files = os.listdir("./files")
    #TODO: filter jpeg only
    return files

10. filter only .jpeg
@app.route('/files')
def list_files():
    files = os.listdir("./files")
    for file in files:
        if not file.endswith(".jpeg"):
            files.remove(file)
    return files
"""
import os
from flask import Flask, redirect, request, send_file
from google.cloud import storage

os.makedirs('files', exist_ok = True)

app = Flask(__name__)

# Google Cloud Storage Bucket Name
BUCKET_NAME = 'project1-447922_cloudbuild'  # Replace with your actual bucket name

def upload_to_gcs(file, bucket_name):
    """Uploads a file to Google Cloud Storage."""
    client = storage.Client()  # Authenticate using GOOGLE_APPLICATION_CREDENTIALS
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file.filename)  # Create a blob with the file's name
    blob.upload_from_file(file)  # Upload the file
    blob.make_public()  # Make the file publicly accessible
    return blob.public_url  # Return the file's public URL

@app.route('/')
def index():
    """Home page with upload form."""
    form_html = """
    <form method="post" enctype="multipart/form-data" action="/upload">
      <div>
        <label for="file">Choose file to upload</label>
        <input type="file" id="file" name="form_file" accept="image/jpeg"/>
      </div>
      <div>
        <button>Submit</button>
      </div>
    </form>
    """
    return form_html

@app.route('/upload', methods=["POST"])
def upload():
    """Handles file upload and saves to GCS."""
    if 'form_file' not in request.files:
        return "No file part in the request", 400
    
    file = request.files['form_file']
    if file.filename == '':
        return "No selected file", 400

    # Upload file to GCS
    file_url = upload_to_gcs(file, BUCKET_NAME)
    return f"File successfully uploaded! <a href='{file_url}'>View file</a>"

if __name__ == "__main__":
   # Development only: run "python main.py" and open http://localhost:8080
   # When deploying to Cloud Run, a production-grade WSGI HTTP server,
   # such as Gunicorn, will serve the app.
   app.run(host="localhost", port=8080, debug=True)
