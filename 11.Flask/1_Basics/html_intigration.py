"""

___ 

# Intigrating HTML 
 
1. one way is just using *HTML* tags in string of route Function

```python   
def page1():
    return " <html> <html>" # write html in this tag

```

___ 

## standard way 

    Redirect to HTML page

> use Libaray: render_template 

- this render_temple is responsible for redirecting to *HTML* page


        SO create a Seprate HTML page and redirect to it using render_temple



___ 

## steps 

> Create templates Folder 

> create html pages there

> rouute them using app.route

> user render_template to redirct ther 

- so we use render_temple for redirection it 1st seaches for template foler ( in parent Folder ) and in there look for page 



```python 

from flask iport Flask


app = flask(__name__)

@app.route("/")
def html_page():
    return render_template("index.html") # here we are redrecting to index.html page using render_template


if __name__ == "__main__"

    app.run(debug = True)


11.Flask/
│
├── app.py                  <-- your main Flask file
├── templates/              <-- MUST be named exactly "templates"
│   ├── index.html
│   ├── dashboard.html
│   ├── contact.html
│   └── about.html


"""

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def Home():
    return "This is Home Page"

@app.route("/page1")
def page1():
    return "<html> <H1> Home PAge Using HTML Tags <H!> <html>"



#### Intigrating HTML 
## Create templtes folder 1st 
## Write Html codes there
# Intigare them using render_temple("page_name")

@app.route("/index")
def index():
    return  render_template("index.html")

@app.route("/d") # we can have multiple routes
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")



if __name__ == "__main__":

    app.run(debug=True)