"""
Dynamic URL = URL that contains variable parts

Static URL: @app.route("/user")

Dynamc URL: @app.route("/user/<variable>") : it takes Variable 
                                           : Pass That Variable to a Function

//######################################                                           
//// Example
//########################################3

@app.route("/user/<name>") : url takes varible ( this variale is default so accept anything like int,str etc) , then type cast it if needed
def user(name):            : funtion take that variable as argumnt
    return f"Hello {name}" : print it

-----------------------------------------------
================================================
URL: /user/Alyan
            ↓
Flask extracts:
name = "Alyan"
            ↓
Calls:
user("Alyan")


--------------------------------------------
// Specifying Variable TYPE in URL
-------------------------------------------

---->>>> @app.route("/post/<data_type:variable>") 

---->>>> @app.route("/post/<int:variable>")   # now it accepst only int 

/post/10   ✅  int
/post/abc  ❌ (error)


===================================
// SUMMARY
===================================

<string:name>  → default text
<int:id>       → numbers only
<float:value>  → decimal numbers
<path:path>    → full path with /

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// MULTIPLE VARIABELS IN URL
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

--->>> @app.route("/order/<int:id>/<item>")      int/defult 

/order/101/laptop
"""


from flask import Flask, request

app = Flask(__name__)

#simple String
@app.route("/user/<name>")
def user(name):
    return f"Hello {name}"

#Intiger
@app.route("/age/<int:age>")
def age(age):
    return f"You are {age} Years OLD"

#float
@app.route("/price/<float:Val>")
def price(val):
    return f"price is {val}"

# 4. Multiple variables
@app.route("/add/<int:a>/<int:b>")
def add(a,b):
    return f" Sum = {a + b}"

@app.route("/mul/<float:a>/<int:b>")
def product(a,b):
    return f"Prod: {a*b}"

# repeat String
@app.route("/repeat/<word>/<int:n>")
def repeat(word, n):
    return " ".join([word] * n)



if __name__ == "__main__":

    app.run(debug=True)
