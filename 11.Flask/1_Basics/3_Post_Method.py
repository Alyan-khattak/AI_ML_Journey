"""

POST: "Hey server, here is some data → do something with it"
You give order to waiter → "Make this food"


| Feature       | GET        | POST         |
| ------------- | ---------- | ------------ |
| Purpose       | Fetch data | Send data    |
| Data location | URL        | Request body |
| Visibility    | Visible    | Hidden       |
| Use case      | Query      | Forms / APIs |


"""


from flask import Flask, request, render_template, jsonify

app = Flask(__name__)


@app.route("/")
def Home():
    return "This is Home Page"

@app.route("/page1")
def page1():
    return "<html> <H1> Home PAge Using HTML Tags <H!> <html>"

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

"""
request.form.get("username")  # returns None if missing ✅
request.form["username"]      # KeyError if missing ❌

request.form["Name of field"]

form  tag in html sends data in the from of Dictional

###############################################3

name in input field act as key

key = "username"
value = whatever user types

User types:  Alyan
HTML sends:
{
   "username": "Alyan"
}

Flask receives:
request.form = {
   "username": "Alyan"
}

You do:
username = request.form.get("username")

Result:
username = "Alyan"


"""

##form.html
@app.route("/form", methods = ["GET", "POST"])
def form():
    if request.method=="POST":
        name = request.form["name"] # retieving name from form.html input field
        return f"Hello {name} "     # request.html page name["id of field"]
    else:
        return render_template("form.html")

## form1.html
@app.route("/form1", methods = ["Get","POST"])
def submit(): # request = everything client sent
    if request.method == "POST":
        # rettieve text input from form1
        name = request.form.get("name")
        email = request.form.get("email")

        # retrive Radio Buutons
        gender = request.form.get("gender")

        # retrieve check boxes MUltiple

        hobbies = request.form.getlist("hobbies")

        # retrieve drop down
        country = request.form.get("country")

        # Retrieve textarea
        feedback = request.form.get("feedback")
        
        # You can process/save this data, here we just return it
        return f"""
        <h1>Survey Submitted</h1>
        <p>Name: {name}</p>
        <p>Email: {email}</p>
        <p>Gender: {gender}</p>
        <p>Hobbies: {', '.join(hobbies)}</p>
        <p>Country: {country}</p>
        <p>Feedback: {feedback}</p>
        """
    
    else:
        return render_template("form1.html")




if __name__ == "__main__":

    app.run(debug=True)