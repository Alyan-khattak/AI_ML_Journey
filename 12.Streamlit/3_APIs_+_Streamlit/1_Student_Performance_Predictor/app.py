from flask import Flask, request, jsonify

app = Flask(__name__)

# 1st run Flask so Its API are Online then Run Streamlit

# ---------------- MODEL ----------------
def predict_student(hours, sleep):

    """
        marks = (8 * hours) + (2 * sleep) + 10
    """

    marks = ( 8 * hours ) + ( 2 * sleep ) + 10
    return min(int(marks), 100)


# ---------------- VALIDATION ----------------
def validate_input(data):
    if not data:
        return False, "No Data Provided"
    
    if "hours" not in data:
        return False, "Study Hours Required"
    
    if "sleep" not in data:
        return False, "Sleep Hours required"
    
    hours = data["hours"]
    sleep = data["sleep"]

    if not isinstance(hours, (int, float)):
        return False, "Hours Must be Numver"
    
    if not isinstance(sleep, (int, float)):
        return False, "Sleep must be Numver"
    
    if hours < 0 or hours > 16:
        return False, "Hours mst be b/w 0-16"
    
    if sleep < 0 or sleep >12:
        return False, "Sleep must be b/w 0-12"
    
    return True, None



# ---------------- API ----------------
@app.route("/predict", methods = ["POST"])
def predict():

    data = request.get_json()

    valid, error = validate_input(data)
    if not valid:
        return jsonify({"Error", error})
    
    hours = data["hours"]
    sleep = data["sleep"]


    # Model prediction
    marks = predict_student(hours, sleep)

    # Grade + status
    if marks >= 85:
        grade = "A"
    elif marks >= 70:
        grade = "B"
    elif marks >= 50:
        grade = "C"
    else:
        grade = "F"

    status = "Pass" if marks >= 50 else "Fail"

    return jsonify({
        "hours": hours,
        "sleep": sleep,
        "marks": marks,
        "grade": grade,
        "status": status
    })


if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":

    app.run(debug=True)