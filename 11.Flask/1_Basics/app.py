"""

## SkeleTon

- initailize flask:

It creates Instace of flask calss, which will be our wsgi application

app = flask(__name__)                               ###WSGI APPlication     

                                ## why __name__ ? It tell Flask "Where is this app located?"

##Basic ROuet 

@app.route("/")         # it means “When someone visits '/' → call this function”
def home(): 
    return "This is home page"


if __name__ == "main"       # Entry point of any .py file ( 1st go ahead and cheack this and execution will start from here)

    app.run()  # run flask app


    #in app.run() there is debug perameter

    app.run(debug=True) # Now when Change function we dont need to run app.py again and again to refresh page


"""

from flask import Flask

# Initialize Flask app (WSGI application)
app = Flask(__name__)  # __name__ tells Flask where this app is located

# Basic route
@app.route("/")# Entry point of any .py file ( 1st go ahead and cheack this and execution will start from here)
def home():
    return "THIS IS HOME PAGE!"

@app.route("/page1")
def page1():
    return "This is Page 1"

@app.route("/page2")
def Page2():
    return "This is Page 2"

@app.route("/page3")
def page3():
    return "This is Page 3"

# Entry point
if __name__ == "__main__": # Entry point of any .py file ( 1st go ahead and cheack this and execution will start from here)

    app.run(debug=True)  # debug=True reloads app on changes automatically