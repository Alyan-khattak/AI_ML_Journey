"""""
│
├─ 5.1Jinj2.py.py
├─ templates/
│   ├─ products.html
│   └─ product_detail.html
"""
from flask import Flask, render_template

app = Flask(__name__)

# Sample product data
products = [
    {"id": 1, "name": "Laptop", "price": 1200},
    {"id": 2, "name": "Phone", "price": 800},
    {"id": 3, "name": "Headphones", "price": 150},
]

# Route 1: Show all products
@app.route("/products")
def show_products():
    return render_template("products.html", products=products)

# Route 2: Product details
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    return render_template("product_detail.html", product=product)

if __name__ == "__main__":
    app.run(debug=True)