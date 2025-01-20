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
from flask import Flask, redirect, request, render_template_string, url_for
from werkzeug.utils import secure_filename
from google.cloud import storage
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Configure app
app = Flask(__name__)

# Initialize Google Cloud Storage client
storage_client = storage.Client(project='project1-448316')
bucket_name = 'project1-447922_cloudbuild'
bucket = storage_client.get_bucket(bucket_name)

ALLOWED_EXTENSIONS = {'jpeg', 'jpg'}

def allowed_file(filename):
   """Check if the file has an allowed extension."""
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def list_files():
   """List all the files in the bucket."""
   blobs = bucket.list_blobs()
   return [blob.name for blob in blobs if blob.name.lower().endswith(('.jpeg', '.jpg'))]

def save_file(file):
   """Save the uploaded file to the specified bucket."""
   filename = secure_filename(file.filename)
   blob = bucket.blob(filename)
   blob.upload_from_file(file)
   
def delete_file(filename):
   """Delete a file from the specified bucket."""
   blob = bucket.blob(filename)
   if blob.exists():
       blob.delete()
       return True
   return False

@app.route('/')
def index():
   """Home page with upload form and list of uploaded files."""
   files = list_files()
   index_html = """
   <html>
   <head><title>Upload Files</title></head>
   <body>
       <h1>Upload Image (JPEG only)</h1>
       <form method="post" enctype="multipart/form-data" action="/upload">
           <div>
               <label for="file">Choose file to upload (* NOTE .jpg photos files ONLY*)</label>
               <input type="file" id="file" name="form_file" accept="image/jpeg">
           </div>
           <div>
               <button>Submit</button>
           </div>
       </form>

       <h2>Uploaded Files:</h2>
       <ul>
       """
   # Display list of files with view and delete options
   for file in files:
       index_html += f"<li>{file} - <a href='/files/{file}'>View</a> | <a href='/delete/{file}'>DELETE</a></li>"
   index_html += """
       </ul>
   </body>
   </html>
   """
   return index_html

@app.route('/upload', methods=["POST"])
def upload():
   """Handles file upload and saves to the specified bucket."""
   file = request.files['form_file']
   if file and allowed_file(file.filename):
       save_file(file)
       return redirect(url_for('index'))
   return 'Invalid file type or upload failed', 400

@app.route('/files/<filename>')
def get_file(filename):
   """Generates a signed URL for accessing a file from Google Cloud Storage."""
   blob = bucket.blob(filename)
   if blob.exists():
       try:
           # Generate a signed URL for the file (valid for 3600 seconds, i.e., 1 hour)
           url = blob.generate_signed_url(expiration=3600, method='GET')
           app.logger.debug(f"Generated signed URL: {url}")  # Log the generated URL for debugging
           # Serve the image directly using the signed URL
           return f'<html><body><img src="{url}" alt="Image"></body></html>'
       except Exception as e:
           app.logger.error(f"Error generating signed URL for {filename}: {e}")
           return f"Error generating signed URL for {filename}: {e}", 500
   return 'File not found', 404

@app.route('/delete/<filename>')
def delete(filename):
   """Deletes a specific file from the specified bucket."""
   if delete_file(filename):
       return redirect(url_for('index'))
   return 'File not found', 404

if __name__ == '__main__':
   # Use PORT environment variable, default to 8080 if not set
   port = int(os.getenv("PORT", 8080))  
   app.run(host='0.0.0.0', port=port)

