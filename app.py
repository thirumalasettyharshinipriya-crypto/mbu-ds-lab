
import os
import json
import uuid

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory
)

from werkzeug.utils import secure_filename


# =========================================
# FLASK APPLICATION
# =========================================

app = Flask(__name__)
app.secret_key = "mbu_ds_lab_secret_key"


# =========================================
# FOLDERS
# =========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_FOLDER = os.path.join(BASE_DIR, "static")

PDF_FOLDER = os.path.join(
    STATIC_FOLDER,
    "pdfs"
)

UPLOAD_FOLDER = os.path.join(
    STATIC_FOLDER,
    "uploads"
)

MODULES_DATA_FILE = os.path.join(
    BASE_DIR,
    "modules_data.json"
)
UPLOADS_DATA_FILE = os.path.join(
    BASE_DIR,
    "uploads_data.json"
)
PROFILE_DATA_FILE = os.path.join(
    BASE_DIR,
    "student_profile.json"
)


# =========================================
# SUBJECTS
# =========================================

SUBJECTS = [
    "DS",
    "LRRE",
    "CRDT",
    "CAO",
    "IoT"
]


# =========================================
# CREATE FOLDERS
# =========================================

# If static/pdfs already exists as a file,
# use static/pdfs_uploads instead.

if os.path.exists(PDF_FOLDER) and not os.path.isdir(PDF_FOLDER):

    PDF_FOLDER = os.path.join(
        STATIC_FOLDER,
        "pdfs_uploads"
    )

os.makedirs(PDF_FOLDER, exist_ok=True)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================
# PROFILE IMAGE SETTINGS
# =========================================

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

DEFAULT_PROFILE_IMAGE = "default-profile.jpeg"


def allowed_image(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


# =========================================
# LOAD MODULE DATA
# =========================================

def load_modules():

    if not os.path.isfile(MODULES_DATA_FILE):
        return {}

    try:

        with open(
            MODULES_DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, dict):
                return data

            return {}

    except (json.JSONDecodeError, OSError):

        return {}


# =========================================
# SAVE MODULE DATA
# =========================================

def save_modules(data):

    with open(
        MODULES_DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================
# LOAD STUDENT PROFILE
# =========================================

def load_profile():

    default_profile = {
        "name": "",
        "roll_number": "",
        "branch": "CSE - Data Science",
        "batch": "2028",
        "email": "",
        "phone": "",
        "profile_image": DEFAULT_PROFILE_IMAGE
    }

    if not os.path.isfile(PROFILE_DATA_FILE):
        return default_profile

    try:

        with open(
            PROFILE_DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            saved_profile = json.load(file)

            if isinstance(saved_profile, dict):
                default_profile.update(saved_profile)

    except (json.JSONDecodeError, OSError):
        pass

    return default_profile



# =========================================
# SAVE STUDENT PROFILE
# =========================================

def save_profile(profile):

    with open(
        PROFILE_DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=4,
            ensure_ascii=False
        )
        # =========================================
# STUDENT PROFILE AVAILABLE IN ALL PAGES
# =========================================

@app.context_processor
def inject_student_profile():
    return {
        "student": load_profile()
    }


# =========================================
# HOME
# =========================================

@app.route("/")
def index():

    # Load saved student profile
    student = load_profile()

    # Get profile image
    image_name = student.get(
        "profile_image",
        DEFAULT_PROFILE_IMAGE
    )

    # Display homepage with student ID card data
    return render_template(
        "index.html",
        student=student,
        image_name=image_name
    )
# =========================================
# MODULES
# =========================================

@app.route("/modules", methods=["GET", "POST"])
def modules():

    saved_modules = load_modules()

    # PDF UPLOAD

    if request.method == "POST":

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        module_title = request.form.get(
            "module_title",
            ""
        ).strip()

        unit_name = request.form.get(
            "unit_name",
            ""
        ).strip()

        pdf_file = request.files.get("pdf_file")

        if subject not in SUBJECTS:

            flash(
                "Please select a valid subject.",
                "error"
            )

            return redirect(url_for("modules"))

        if not module_title or not unit_name:

            flash(
                "Please enter module title and unit name.",
                "error"
            )

            return redirect(url_for("modules"))

        if not pdf_file or not pdf_file.filename:

            flash(
                "Please select a PDF file.",
                "error"
            )

            return redirect(url_for("modules"))

        original_filename = secure_filename(
            pdf_file.filename
        )

        if not original_filename.lower().endswith(".pdf"):

            flash(
                "Only PDF files are allowed.",
                "error"
            )

            return redirect(url_for("modules"))

        subject_folder = os.path.join(
            PDF_FOLDER,
            subject
        )

        os.makedirs(
            subject_folder,
            exist_ok=True
        )

        unique_filename = (
            uuid.uuid4().hex[:8]
            + "_"
            + original_filename
        )

        file_path = os.path.join(
            subject_folder,
            unique_filename
        )

        try:

            pdf_file.save(file_path)

        except OSError:

            flash(
                "Unable to save PDF. Please check folder permissions.",
                "error"
            )

            return redirect(url_for("modules"))

        if subject not in saved_modules:
            saved_modules[subject] = []

        saved_modules[subject].append({

            "id": uuid.uuid4().hex,

            "title": module_title,

            "unit": unit_name,

            "filename": original_filename,

            "path": (
                f"{os.path.basename(PDF_FOLDER)}/"
                f"{subject}/{unique_filename}"
            )

        })

        try:

            save_modules(saved_modules)

        except OSError:

            flash(
                "PDF uploaded, but module details could not be saved.",
                "error"
            )

            return redirect(url_for("modules"))

        flash(
            "PDF uploaded successfully!",
            "success"
        )

        return redirect(url_for("modules"))

    # DISPLAY MODULES

    modules_data = {}

    total_pdfs = 0

    for subject in SUBJECTS:

        modules_data[subject] = saved_modules.get(
            subject,
            []
        )

        total_pdfs += len(
            modules_data[subject]
        )

    return render_template(
        "modules.html",
        subjects=SUBJECTS,
        modules_data=modules_data,
        total_pdfs=total_pdfs
    )

# =========================================
# VIEW / DOWNLOAD UPLOADED FILES
# =========================================

@app.route("/uploads/<category>/<filename>")
def uploaded_file(category, filename):

    if category not in UPLOAD_CATEGORIES:
        return "Invalid category", 404

    category_folder = os.path.join(
        UPLOAD_FOLDER,
        category
    )

    return send_from_directory(
        category_folder,
        filename
    )


@app.route("/download/<category>/<filename>")
def download_uploaded_file(category, filename):

    if category not in UPLOAD_CATEGORIES:
        return "Invalid category", 404

    category_folder = os.path.join(
        UPLOAD_FOLDER,
        category
    )

    return send_from_directory(
        category_folder,
        filename,
        as_attachment=True
    )

@app.route("/delete/tools/<filename>", methods=["POST"])
def delete_tool_file(filename):

    data = load_uploads()

    tool_files = data.get("tools", [])

    file_to_delete = next(
        (file for file in tool_files
         if file["filename"] == filename),
        None
    )

    if file_to_delete:

        file_path = os.path.join(
            UPLOAD_FOLDER,
            "tools",
            filename
        )

        if os.path.exists(file_path):
            os.remove(file_path)

            data["tools"] = [
            file for file in tool_files
            if file["filename"] != filename
        ]

        save_uploads(data)

        flash("File deleted successfully!", "success")

    return redirect(url_for("tools_page"))
@app.route("/delete/projects/<filename>", methods=["POST"])
def delete_project_file(filename):

    data = load_uploads()

    project_files = data.get("projects", [])

    file_to_delete = next(
        (file for file in project_files
         if file["filename"] == filename),
        None
    )

    if file_to_delete:

        file_path = os.path.join(
            UPLOAD_FOLDER,
            "projects",
            filename
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        data["projects"] = [
            file for file in project_files
            if file["filename"] != filename
        ]

        save_uploads(data)

        flash("Project file deleted successfully!", "success")

    return redirect(url_for("projects"))
@app.route("/delete/assignments/<filename>", methods=["POST"])
def delete_assignment_file(filename):

    data = load_uploads()

    assignment_files = data.get("assignments", [])

    file_to_delete = next(
        (file for file in assignment_files
         if file["filename"] == filename),
        None
    )

    if file_to_delete:

        file_path = os.path.join(
            UPLOAD_FOLDER,
            "assignments",
            filename
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        data["assignments"] = [
            file for file in assignment_files
            if file["filename"] != filename
        ]

        save_uploads(data)

        flash("Assignment file deleted successfully!", "success")

    return redirect(url_for("assignments"))
@app.route("/delete/experiments/<filename>", methods=["POST"])
def delete_experiment_file(filename):

    data = load_uploads()

    experiment_files = data.get("experiments", [])

    file_to_delete = next(
        (
            file for file in experiment_files
            if file["filename"] == filename
        ),
        None
    )

    if file_to_delete:

        file_path = os.path.join(
            UPLOAD_FOLDER,
            "experiments",
            filename
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        data["experiments"] = [
            file for file in experiment_files
            if file["filename"] != filename
        ]

        save_uploads(data)

        flash(
            "Lab experiment file deleted successfully!",
            "success"
        )

    return redirect(url_for("experiments"))

# =========================================
# FILE UPLOAD HANDLING FUNCTION
# =========================================
UPLOAD_CATEGORIES = {
    "assignments": [
        "Data Science", "LRRE", "CRDT", "CAO", "IoT"
    ],
    "projects": [
        "Machine Learning", "Data Analysis",
        "Artificial Intelligence", "Web Development", "IoT"
    ],
    "tools": [
        "Python", "Jupyter Notebook", "Google Colab",
        "NumPy", "Pandas", "Matplotlib"
    ],
    "resources": [
        "Lecture Notes", "PDF Materials", "Study Guides",
        "Video Tutorials", "Reference Books", "Practice Materials"
    ],
    "experiments": [
        "Python Basics",
        "Data Analysis",
        "Data Visualization",
        "Machine Learning",
        "SQL"
    ]
}


ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "ppt", "pptx",
    "txt", "zip", "py", "ipynb", "csv",
    "mp4", "jpg", "jpeg", "png"
}


def load_uploads():
    if os.path.exists(UPLOADS_DATA_FILE):
        with open(UPLOADS_DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    return {
    "assignments": [],
    "projects": [],
    "tools": [],
    "resources": [],
    "experiments": []
}


def save_uploads(data):
    with open(UPLOADS_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def handle_upload_page(category, template):

    data = load_uploads()
    endpoint = "tools_page" if category == "tools" else category

    if request.method == "POST":

        card_name = request.form.get("card_name", "").strip()
        uploaded_file = request.files.get("file")

        if card_name not in UPLOAD_CATEGORIES[category]:
            flash("Please select a valid category.", "error")
            return redirect(url_for(endpoint))

        if not uploaded_file or uploaded_file.filename == "":
            flash("Please select a file.", "error")
            return redirect(url_for(endpoint))

        if not allowed_file(uploaded_file.filename):
            flash("File type is not allowed.", "error")
            return redirect(url_for(endpoint))

        original_filename = secure_filename(uploaded_file.filename)

        category_folder = os.path.join(
            UPLOAD_FOLDER,
            category
        )

        os.makedirs(category_folder, exist_ok=True)

        unique_filename = (
            uuid.uuid4().hex + "_" + original_filename
        )

        file_path = os.path.join(
            category_folder,
            unique_filename
        )

        uploaded_file.save(file_path)

        file_data = {
            "id": uuid.uuid4().hex,
            "card_name": card_name,
            "original_filename": original_filename,
            "filename": unique_filename
        }

        data.setdefault(category, []).append(file_data)

        save_uploads(data)

        flash("File uploaded successfully!", "success")

        return redirect(url_for(endpoint))

    return render_template(
        template,
        categories=UPLOAD_CATEGORIES[category],
        files=data.get(category, [])
    )
# =========================================
# ASSIGNMENTS
# =========================================

@app.route("/assignments", methods=["GET", "POST"])
def assignments():

    return handle_upload_page(
        "assignments",
        "assignments.html"
    )
# =========================================
# PROJECTS
# =========================================

@app.route("/projects", methods=["GET", "POST"])
def projects():

    return handle_upload_page(
        "projects",
        "projects.html"
    )


# =========================================
# LAB EXPERIMENTS
# =========================================

@app.route("/experiments", methods=["GET", "POST"])
def experiments():

    return handle_upload_page(
        "experiments",
        "experiments.html"
    )

# =========================================
# TOOLS
# =========================================

@app.route("/tools", methods=["GET", "POST"])
def tools_page():

    return handle_upload_page(
        "tools",
        "tools.html"
    )

# =========================================
# RESOURCES
# =========================================
@app.route("/resources", methods=["GET", "POST"])
def resources():

    return handle_upload_page(
        "resources",
        "resources.html"
    )

# =========================================
# STUDENT PROFILE
# =========================================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    # Load existing student information
    student = load_profile()

    # -------------------------------------
    # SAVE PROFILE
    # -------------------------------------

    if request.method == "POST":

        student["name"] = request.form.get(
            "name",
            ""
        ).strip()

        student["roll_number"] = request.form.get(
            "roll_number",
            ""
        ).strip()

        student["branch"] = request.form.get(
            "branch",
            "CSE - Data Science"
        ).strip()

        student["batch"] = request.form.get(
            "batch",
            "2028"
        ).strip()

        student["email"] = request.form.get(
            "email",
            ""
        ).strip()

        student["phone"] = request.form.get(
            "phone",
            ""
        ).strip()

        # ---------------------------------
        # PROFILE IMAGE UPLOAD
        # ---------------------------------

        profile_image = request.files.get(
            "profile_image"
        )

        if profile_image and profile_image.filename:

            if not allowed_image(profile_image.filename):

                flash(
                    "Please upload JPG, JPEG, PNG or WEBP image.",
                    "error"
                )

                return redirect(url_for("profile"))

            image_filename = (
                uuid.uuid4().hex[:8]
                + "_"
                + secure_filename(profile_image.filename)
            )

            image_path = os.path.join(
                UPLOAD_FOLDER,
                image_filename
            )

            try:

                profile_image.save(image_path)

                student["profile_image"] = (
                    "uploads/" + image_filename
                )

            except OSError:

                flash(
                    "Unable to upload profile image.",
                    "error"
                )

                return redirect(url_for("profile"))

        # ---------------------------------
        # SAVE PROFILE DATA
        # ---------------------------------

        try:

            save_profile(student)

        except OSError:

            flash(
                "Unable to save student profile.",
                "error"
            )

            return redirect(url_for("profile"))

        flash(
            "Student profile updated successfully!",
            "success"
        )

        return redirect(url_for("profile"))

    # -------------------------------------
    # DISPLAY PROFILE
    # -------------------------------------

    image_name = student.get(
        "profile_image",
        DEFAULT_PROFILE_IMAGE
    )

    return render_template(
        "profile.html",
        student=student,
        image_name=image_name
    )


# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(debug=True)
