from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------- DATABASE ----------------
characters = []
current_id = 1

VALID_CREWS = ["Straw Hat", "Navy", "Revolutionary", "Pirate"]
VALID_ROLES = ["Captain", "Swordsman", "Sniper", "Cook", "Doctor"]

# ---------------- VALIDATION ----------------
def validate_character(data):

    if not data:
        return False, "No JSON provided"

    # Name
    if "name" not in data or not isinstance(data["name"], str):
        return False, "Valid name required"

    # Power
    if "power" not in data or not isinstance(data["power"], int):
        return False, "Power must be integer"

    if data["power"] < 0 or data["power"] > 100:
        return False, "Power must be 0–100"

    # Crew
    if "crew" not in data or data["crew"] not in VALID_CREWS:
        return False, f"Crew must be one of {VALID_CREWS}"

    # Role
    if "role" not in data or data["role"] not in VALID_ROLES:
        return False, f"Role must be one of {VALID_ROLES}"

    # Bounty
    if "bounty" not in data or not isinstance(data["bounty"], int):
        return False, "Bounty must be integer"

    if data["bounty"] < 0:
        return False, "Bounty must be >= 0"

    return True, None


# ---------------- LOGIC ----------------
def calculate_rank(power):
    if power >= 90:
        return "Yonko Level"
    elif power >= 70:
        return "Commander"
    elif power >= 50:
        return "Elite"
    else:
        return "Rookie"


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return "One Piece API Running"

# ---------------- GET ALL ----------------
@app.route("/characters", methods=["GET"])
def get_characters():
    return jsonify(characters)


# ---------------- GET ONE ----------------
@app.route("/characters/<int:char_id>", methods=["GET"])
def get_character(char_id):
    char = next((c for c in characters if c["id"] == char_id), None)

    if not char:
        return jsonify({"error": "Character not found"}), 404

    return jsonify(char)


# ---------------- POST ----------------
@app.route("/characters", methods=["POST"])
def create_character():
    global current_id

    data = request.get_json()

    valid, error = validate_character(data)
    if not valid:
        return jsonify({"error": error}), 400

    char = {
        "id": current_id,
        "name": data["name"],
        "power": data["power"],
        "crew": data["crew"],
        "role": data["role"],
        "bounty": data["bounty"],
        "rank": calculate_rank(data["power"])
    }

    characters.append(char)
    current_id += 1

    return jsonify(char), 201


# ---------------- PUT ----------------
@app.route("/characters/<int:char_id>", methods=["PUT"])
def update_character(char_id):
    char = next((c for c in characters if c["id"] == char_id), None)

    if not char:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()

    # Partial updates
    if "power" in data:
        if not isinstance(data["power"], int):
            return jsonify({"error": "Power must be int"}), 400
        char["power"] = data["power"]
        char["rank"] = calculate_rank(data["power"])

    if "bounty" in data:
        if data["bounty"] < 0:
            return jsonify({"error": "Invalid bounty"}), 400
        char["bounty"] = data["bounty"]

    return jsonify(char)


# ---------------- DELETE ----------------
@app.route("/characters/<int:char_id>", methods=["DELETE"])
def delete_character(char_id):
    global characters

    char = next((c for c in characters if c["id"] == char_id), None)

    if not char:
        return jsonify({"error": "Not found"}), 404

    characters = [c for c in characters if c["id"] != char_id]

    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    app.run(debug=True)