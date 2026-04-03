"""

| Method | Purpose              |
| ------ | -------------------- |
| GET    | Read/fetch data      |
| POST   | Create new data      |
| PUT    | Update existing data |
| DELETE | Delete data          |

Client → HTTP request (GET/POST/PUT/DELETE) → Flask route → Process → Return JSON → Client

+++++++++++++++++++++++++++++++++++++++++++++
----   JSONIFY IN FLASK
+++++++++++++++++++++++++++++++++++++++++++++++

- Convert Python objects (dict, list, etc.) into JSON response that can be sent to clients.



---  jsonify(python objct)

--->> return jsonify(data)  -->> asume data was a list now its an json





"""

from flask import Flask, jsonify, request

# ---------------- Initialize Flask app ----------------
app = Flask(__name__)

# ---------------- In-memory "database" ----------------
# We'll use a list of dictionaries to simulate a database
users = [
    {"id": 1, "name": "Alyan", "age": 25},
    {"id": 2, "name": "Aroosa", "age": 22}
]


@app.route("/")
def home():
    return f"We are using API Here"

# ---------------- GET all users ----------------
@app.route("/users", methods=["GET"])
def get_users():
    """
    GET /users
    Returns a list of all users as JSON
    """
    # jsonify converts Python list/dict to JSON response
    # Also sets Content-Type: application/json
    return jsonify(users)


# ---------------- GET a user by ID ----------------
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    GET /users/<user_id>
    Returns JSON of a specific user by id
    """
    # Search for user in list (in-memory DB)
    user = next((u for u in users if u["id"] == user_id), None)  # -->> Generator 

    """
    (u for u in users if u["id"] == user_id) → generator expression
    Looks like a list comprehension [u for u in users if ...] but uses parentheses () instead of []
    It does not create a list in memory, it yields items one by one — just like a generator function does

    
    #Equivelnt to this 
    def user_gen(users, user_id):
    for u in users:
        if u["id"] == user_id:
            yield u

            
    user = next(user_gen(users, user_id), None)
    """
    
    if user:
        # Found user → return as JSON
        return jsonify(user)
    else:
        # User not found → return error JSON with status 404
        return jsonify({"error": "User not found"}), 404


# ---------------- POST a new user ----------------
@app.route("/users", methods=["POST"])
def create_user():
    """
    POST /users
    Receives JSON in request body and creates a new user
    """
    # request.get_json() parses JSON body sent by client
    data = request.get_json() # the data we sent from post as json comes here and got stored in dcata as dictionary
    # Example data: {"name": "John", "age": 30}

    # Build new user dictionary
    new_user = {
        "id": len(users) + 1,  # auto-increment ID
        "name": data.get("name"),  # use get() to avoid KeyError
        "age": data.get("age")
    }

    # Append new user to in-memory database
    users.append(new_user)

    # Return JSON response with status code 201 (Created)
    return jsonify(new_user), 201


# ---------------- PUT to update a user ----------------
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    PUT /users/<user_id>
    Updates existing user with JSON data in request body
    """
    # Find user
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Parse JSON data from request body
    data = request.get_json()

    # Update user fields if provided
    """
        user = {"id": 1, "name": "Alyan", "age": 25}
        data = {"name": "John"}  # Client only sent name ( i.e for above data client only wants to update name)

        -->> dict.get(key, default)

        -->> data.get("name", user["name"])

        # Try to get the key "name" from data user sent , if we find it so change else keep the current data

        -->>  data.get("age", user["age"]) 

        --->> user["age"] = data.get("age", user["age"])  as age is not sen we take user["age"] which is 25 and save it in user

        # Try to get the key "age" from data user sent , if we find it so change else keep the current data
        # as the user only sent name so only name will be changed, and the age will be kept old one


        user["name"] = data.get("name", user["name"])  # John
        user["age"] = data.get("age", user["age"])    # 25 (unchanged)

    """
    user["name"] = data.get("name", user["name"]) # dict.get(key, default)
    user["age"] = data.get("age", user["age"])

    # Return updated user as JSON
    return jsonify(user)


# ---------------- DELETE a user ----------------
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    DELETE /users/<user_id>
    Deletes user by ID
    """
    global users # indicatinf the glocal users variable outside func to python
    # Keep all users except the one to delete
    users = [u for u in users if u["id"] != user_id]

    # Return confirmation message
    return jsonify({"message": f"User {user_id} deleted"})


# ---------------- Run Flask app ----------------
if __name__ == "__main__":
    app.run(debug=True)