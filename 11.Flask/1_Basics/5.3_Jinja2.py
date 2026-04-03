"""

Form (marks input)
        ↓ POST
Flask function (/submit)
        ↓
Redirect → /result/<marks>
        ↓
Jinja2 template decides:
   Pass or Fail
        ↓
Displays result




├── 5.3_Jinja2.py
├── templates/
│   ├── form_jinja5.3.html
│   ├── result.html
│   ├── pass.html
│   ├── fail.html



"""

from flask import Flask, render_template, redirect, request, url_for

app = Flask(__name__)

# ---------------- Form Route ----------------
@app.route("/" , methods = ["GET", "POST"])
def form():

    if request.method == "POST":
        marks = int(request.form.get("marks"))

        # Redirect using dynamic URL
        return redirect(url_for("result", score = marks))
    return render_template("form_jinja5.3.html")

# ---------------- Result Route ----------------
@app.route("/result/<int:score>")
def result(score):
    status = "pass" if score >= 50 else "fail"

    return render_template("result.html" , score = score, status = status)


# ---------------- Pass Page ----------------
@app.route("/pass/<int:score>")
def pass_page(score):
    return render_template("pass.html", score=score)


# ---------------- Fail Page ----------------
@app.route("/fail/<int:score>")
def fail_page(score):
    return render_template("fail.html" , score = score)





if __name__ == "__main__":
    app.run(debug=True)