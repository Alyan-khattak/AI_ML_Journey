## TO DO APP 

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------- In-memory database ----------------
tasks = [
    {"id": 1, "title": "Learn Flask", "completed": False},
    {"id": 2, "title": "Build API", "completed": False}
]


@app.route("/")
def home():
    return f"Todo App APIs"



# ---------------- GET all tasks ----------------

@app.route("/tasks", methods = ["GET"])
def get_tasks():
    return jsonify(tasks)


# ---------------- GET single task ----------------
@app.route("/tasks/<int:task_id>", methods = ["GET"])
def get_task(task_id):
    task = next((t for t in tasks if tasks["id"] == task_id), None)

    if task:
        return jsonify(task)
    else:
        return jsonify({"error": "Task NO found"}), 404
    


# ---------------- POST create new task ----------------
@app.route("/tasks", methods = ["POST"])
def create_task():

    data = request.get_json()

    new_task = {

        "id" : len(tasks) + 1,
        "title": data.get("title"),
        "completed": False 
    }

    tasks.append(new_task)
    return jsonify(new_task), 201



# ---------------- PUT update task ----------------

@app.route("/tasks/<int:task_id>", methods = "PUT")
def update_task(task_id):

    task = next((t for t in tasks if tasks["id"] == task_id), None)

    if not task:
        return jsonify({"error": "Task Not Found"})
    
    data = request.get_json()

    tasks["title"] = data.get("title" , tasks["title"])
    tasks["completed"] = data.get("completed", tasks["completed"])

    return jsonify(tasks)

# ---------------- DELETE task ----------------
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    DELETE /tasks/<task_id>
    Delete a task
    """
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]

    return jsonify({"message": f"Task {task_id} deleted"})



    

if __name__ == "__main__":

    app.run(debug=True)