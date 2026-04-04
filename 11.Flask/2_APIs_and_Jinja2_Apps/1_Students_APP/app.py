from flask import Flask, jsonify, request, render_template, redirect, url_for

app = Flask(__name__)

students = []
current_id = 1


# ---------------- Validation ----------------
def validate_student(data):
    if not data:
        return False, "No data provided"

    if "name" not in data:
        return False, "Name is required"

    if "marks" not in data:
        return False, "Marks are required"

    if not isinstance(data["marks"], int):
        return False, "Marks must be integer"

    if data["marks"] < 0 or data["marks"] > 100:
        return False, "Marks must be between 0–100"

    return True, None


# ---------------- Grade Logic ----------------
def calculate_grade(marks):
    if marks >= 85:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 50:
        return "C"
    else:
        return "F"


# ---------------- API: Create Student ----------------
@app.route("/students", methods=["POST"])  # this is used when we want to POST data using Postman
def create_student():
    global current_id

    data = request.get_json()

    valid, error = validate_student(data)
    if not valid:
        return jsonify({"error": error}), 400

    marks = data["marks"]

    student = {
        "id": current_id,
        "name": data["name"],
        "marks": marks,
        "grade": calculate_grade(marks),
        "status": "pass" if marks >= 50 else "fail"
    }

    students.append(student)
    current_id += 1

    return jsonify(student), 201


# ----------------API: GET all students ----------------
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students)


# ----------------API: GET one student ----------------
@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = next((s for s in students if s["id"] == student_id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student)


# ----------------API: PUT update student ----------------
@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = next((s for s in students if s["id"] == student_id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()

    # Partial update allowed
    if "name" in data:
        if not isinstance(data["name"], str):
            return jsonify({"error": "Name must be string"}), 400
        student["name"] = data["name"]

    if "marks" in data:
        if not isinstance(data["marks"], int):
            return jsonify({"error": "Marks must be integer"}), 400

        if data["marks"] < 0 or data["marks"] > 100:
            return jsonify({"error": "Marks must be 0-100"}), 400

        student["marks"] = data["marks"]

        # Recalculate derived fields
        student["grade"] = calculate_grade(data["marks"])
        student["status"] = "pass" if data["marks"] >= 50 else "fail"

    return jsonify(student)


# ----------------API: DELETE student ----------------
@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    global students

    student = next((s for s in students if s["id"] == student_id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    students = [s for s in students if s["id"] != student_id]

    return jsonify({"message": f"Student {student_id} deleted"})


# ---------------- Frontend: Form ----------------
@app.route("/")
def form():
    return render_template("form.html")


# ---------------- Handle Form Submission ----------------
@app.route("/submit", methods=["POST"])  # This is used to POST DATA using HTML 
def submit():      # when submit is clicked form sends data here
    name = request.form.get("name")
    marks = int(request.form.get("marks"))

    # Convert form data → JSON-like dict
    data = {"name": name, "marks": marks}

    # Reuse API logic manually
    valid, error = validate_student(data)
    if not valid:
        return f"<h1>Error: {error}</h1>"

    global current_id

    student = {
        "id": current_id,
        "name": name,
        "marks": marks,
        "grade": calculate_grade(marks),
        "status": "pass" if marks >= 50 else "fail"
    }

    students.append(student)
    current_id += 1

    # Redirect to dynamic result page
    return redirect(url_for("result", student_id=student["id"]))
    # result Page shows result of just one student 

# ---------------- Show Result ----------------
@app.route("/student/<int:student_id>")
def result(student_id):
    student = next((s for s in students if s["id"] == student_id), None)

    if not student:
        return "Student not found"

    return render_template("result.html", student=student)


# ---------------- Show All Students ----------------
@app.route("/all")
def all_students():
    return render_template("students.html", students=students)


# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)