""""
==========================
   - - JINJA 2
--------------------------
Allow Python data to be rendered in HTML dynamically.
You can:
    Show variables
    Run loops
    Do conditions
    Include templates (header/footer)
    Use dynamic URLs

======================================
--  Syntax 
======================================

- in Dynamic URLs we were printing Data in function there was no HTML Page

- Now we can pass those Data ( variable of Dynamic URL ) to HTML file

- to rediret to HTML file se render_template(file.html)

- pass the varible in render_temple(file.html, variable = variable)


@app.route("/user/Variable)
def jinja2(Varible):
    return render_temple("file.html", Variable = Variable) -> pass varible so that it could be used in HTML file


=============================
USING PASSED VARIALE IN HTML
------------------------------

- use double bracket and enclosed variable name in it {{ varibale name }}

--->> {{ variable }}

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
for Conditonals  use this {{ % condition just like normal python code%}}
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

wheere condiion logic ends use {{ % end if % }}

--->>> {% if age > 18 %}

---->>>{% else %}

--->> {% endif %}

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
for LOOPs  use this {{ % loop just like normal python code%}}
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

-- where Loop logic ends use {{ % end loop  % }}

--->> {% for i in range(10)  %}

--->>> {% endfor %}


| Jinja2 syntax                             | Purpose                      |                               |           |
| ----------------------------------------- | ---------------------------- | ----------------------------- | --------- |
| `{{ variable }}`                          | Output Python variable       |                               |           |
| `{% if condition %} ... {% endif %}`      | Conditional logic            |                               |           |
| `{% for item in list %} ... {% endfor %}` | Loop over iterable           |                               |           |
| `{% extends "base.html" %}`               | Template inheritance         |                               |           |
| `{% block name %} ... {% endblock %}`     | Define block for inheritance |                               |           |
| `{{ url_for('route_name', arg=value) }}`  | Dynamic URL building         |                               |           |
| `{{ variable                              | filter }}`                   | Apply filters, e.g., `{{ name | upper }}` |


"""

"""
5_jinja2      # Flask app
├─ templates/
│   ├─ home.html
│   ├─ profile.html
│   ├─ formJinja.html
│   ├─ greet.html
"""

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------- Route 1: Home page ----------------
@app.route("/")
def home():
    # Pass a list and a variable to the template
    items = ["Apple", "Banana", "Cherry"]
    title = "Home Page"
    return render_template("home.html", title=title, items=items)

# ---------------- Route 2: Profile (dynamic URL) ----------------

@app.route("/profile/<name>")
def profile(name):
    # Pass dynamic variable and list to template
    age = 25
    hobbies = ["Reading", "Gaming", "Cooking"]
    return render_template("profile.html", name=name, age=age, hobbies=hobbies)

# ---------------- Route 3: Form page ----------------
@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        # Get data from form input
        username = request.form.get("username")
        # Redirect to greet page with dynamic URL
        return redirect(url_for("greet", username=username))
    # GET request → show the form
    return render_template("formJinja.html")

# ---------------- Route 4: Greet page ----------------
@app.route("/greet/<username>")
def greet(username):
    # Pass username to template
    return render_template("greet.html", username=username)

# ---------------- Route 5: Calculator (dynamic URL) ----------------
@app.route("/calc/<int:a>/<int:b>")
def calc(a, b):
    sum_val = a + b
    product_val = a * b
    return render_template("calc.html", a=a, b=b, sum_val=sum_val, product_val=product_val)

# Run the app
if __name__ == "__main__":

    app.run(debug=True)