from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------- In-memory database ----------------
students = []
current_id = 1


# ---------------- Utility: Validation ----------------
def validate_student(data):
    """
    Validate incoming JSON data
    Returns (True, None) if valid
    Else returns (False, error_message)
    """

    # Check if JSON exists
    if not data:
        return False, "No JSON data provided"

    # Validate name
    if "name" not in data:
        return False, "Name is required"

    if not isinstance(data["name"], str):
        return False, "Name must be a string"

    # Validate marks
    if "marks" not in data:
        return False, "Marks are required"

    if not isinstance(data["marks"], int):
        return False, "Marks must be an integer"

    if data["marks"] < 0 or data["marks"] > 100:
        return False, "Marks must be between 0 and 100"

    return True, None


# ---------------- Utility: Grade Logic ----------------
def calculate_grade(marks):
    if marks >= 85:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 50:
        return "C"
    else:
        return "F"


@app.route("/")
def Home():
    return """ Student APIs , No Data By default is Given Create it using Postman via POST

    Valid POST: 
             {
	"name" : "Alyan",
    "marks" : 98 "some int here b/w 0 and 100" } 
    """


# ---------------- GET all students ----------------
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students)


# ---------------- GET one student ----------------
@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = next((s for s in students if s["id"] == student_id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student)


# ---------------- POST create student ----------------
@app.route("/students", methods=["POST"])
def create_student():
    global current_id

    data = request.get_json()

    # Validate input
    valid, error = validate_student(data)
    if not valid:
        return jsonify({"error": error}), 400

    marks = data["marks"]

    new_student = {
        "id": current_id,
        "name": data["name"],
        "marks": marks,
        "grade": calculate_grade(marks),
        "status": "pass" if marks >= 50 else "fail"
    }

    students.append(new_student)
    current_id += 1

    return jsonify(new_student), 201


# ---------------- PUT update student ----------------
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


# ---------------- DELETE student ----------------
@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    global students

    student = next((s for s in students if s["id"] == student_id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    students = [s for s in students if s["id"] != student_id]

    return jsonify({"message": f"Student {student_id} deleted"})


# ---------------- Run app ----------------
if __name__ == "__main__":
    app.run(debug=True)