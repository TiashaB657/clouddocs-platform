from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

@app.route("/")
def home():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    file.save(
        os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )
    )
    return "File uploaded successfully!"
@app.route("/files")
def files():
    
    
    return render_template(
        "files.html",
        files=os.listdir("uploads")
    )
    
@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        "uploads",
        filename
    )
    

if __name__ == "__main__":
    app.run(debug=True)