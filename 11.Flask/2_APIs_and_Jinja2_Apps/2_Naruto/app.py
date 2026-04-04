from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

# ---------------- Data ----------------
ninjas = []
missions = []
ninja_id_counter = 1
mission_id_counter = 1

# ---------------- Validation ----------------
def validate_ninja(data):
    if not data:
        return False, "No data"

    if "name" not in data:
        return False, "Name required"

    if "rank" not in data:
        return False, "Rank required"

    if data["rank"] not in ["Genin", "Chunin", "Jonin", "Kage"]:
        return False, "Invalid rank"

    if "chakra" not in data or not isinstance(data["chakra"], int):
        return False, "Chakra must be integer"

    return True, None


# ---------------- API: Create Ninja ----------------
@app.route("/api/ninjas", methods=["POST"])
def create_ninja():
    global ninja_id_counter

    data = request.get_json()

    valid, error = validate_ninja(data)
    if not valid:
        return jsonify({"error": error}), 400

    ninja = {
        "id": ninja_id_counter,
        "name": data["name"],
        "village": data.get("village", "Leaf"),
        "rank": data["rank"],
        "chakra": data["chakra"]
    }

    ninjas.append(ninja)
    ninja_id_counter += 1

    return jsonify(ninja), 201


# ---------------- API: Get All Ninjas ----------------
@app.route("/api/ninjas", methods=["GET"])
def get_ninjas():
    return jsonify(ninjas)


# ---------------- API: Assign Mission ----------------
@app.route("/api/missions", methods=["POST"])
def create_mission():
    global mission_id_counter

    data = request.get_json()

    """
    When Creating Data for  missions using post always create an attribut ninja_id so so by that we get ninja from ninjas

    data:
    {
        "ninja_id": 1,
        "title": "Rescue Sasuke",
        "difficulty": "A"
    }
    """

    ninja = next((n for n in ninjas if n["id"] == data.get("ninja_id")), None)
    if not ninja:
        return jsonify({"error": "Ninja not found"}), 404

    mission = {
        "id": mission_id_counter,
        "title": data.get("title"),
        "difficulty": data.get("difficulty"),
        "ninja": ninja # the ninja we fetched using id
    }

    missions.append(mission)
    mission_id_counter += 1

    return jsonify(mission), 201

# ----------------API: Update Ninja Info ----------------
@app.route("/api/ninjas/<int:ninja_id>", methods=["PUT"])
def update_ninja(ninja_id):
    data = request.get_json()
    ninja = next((n for n in ninjas if n["id"] == ninja_id), None)
    
    if not ninja:
        return jsonify({"error": "Ninja not found"}), 404

    # Validation
    valid, error = validate_ninja(data)
    if not valid:
        return jsonify({"error": error}), 400

    # Update ninja info
    ninja["name"] = data["name"]
    ninja["rank"] = data["rank"]
    ninja["chakra"] = data["chakra"]
    ninja["village"] = data.get("village", ninja["village"])

    return jsonify(ninja), 200


# ----------------API: Update Mission Info ----------------
@app.route("/api/missions/<int:mission_id>", methods=["PUT"])
def update_mission(mission_id):
    data = request.get_json()
    mission = next((m for m in missions if m["id"] == mission_id), None)

    if not mission:
        return jsonify({"error": "Mission not found"}), 404

    # Update mission info
    if "title" in data:
        mission["title"] = data["title"]

    if "difficulty" in data:
        mission["difficulty"] = data["difficulty"]

    if "ninja_id" in data:
        ninja = next((n for n in ninjas if n["id"] == data["ninja_id"]), None)
        if not ninja:
            return jsonify({"error": "Ninja not found"}), 404
        mission["ninja"] = ninja

    return jsonify(mission), 200
    



# ---------------- Frontend: Form ----------------
@app.route("/")
def form():
    return render_template("form.html")


# ---------------- Handle Form (Create Ninja) ----------------
@app.route("/create", methods=["POST"])
def create():
    global ninja_id_counter

    name = request.form.get("name")
    rank = request.form.get("rank")
    chakra = int(request.form.get("chakra"))

    data = {"name": name, "rank": rank, "chakra": chakra}

    valid, error = validate_ninja(data)
    if not valid:
        return f"<h1>Error: {error}</h1>"

    ninja = {
        "id": ninja_id_counter,
        "name": name,
        "rank": rank,
        "chakra": chakra,
        "village": "Leaf"
    }

    ninjas.append(ninja)
    ninja_id_counter += 1

    return redirect(url_for("show_ninja", ninja_id=ninja["id"]))


# ---------------- Show Single Ninja ----------------
@app.route("/ninja/<int:ninja_id>")
def show_ninja(ninja_id):
    ninja = next((n for n in ninjas if n["id"] == ninja_id), None)
    return render_template("ninja.html", ninja=ninja)


# ---------------- Show All Ninjas ----------------
@app.route("/ninjas")
def show_ninjas():
    return render_template("ninjas.html", ninjas=ninjas)


# ---------------- Show Missions ----------------
@app.route("/missions")
def show_missions():
    return render_template("missions.html", missions=missions)


if __name__ == "__main__":
    app.run(debug=True)