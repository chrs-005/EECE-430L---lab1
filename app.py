from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root01@localhost:3306/exchange'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usd_amount = db.Column(db.Float, nullable=False)
    lbp_amount = db.Column(db.Float, nullable=False)
    usd_to_lbp = db.Column(db.Boolean, nullable=False)


@app.route("/hello", methods=["GET"])
def hello_world():
    return "Hello World!"

@app.route("/transaction", methods=["POST"])
def add_transaction():
    transaction = Transaction(
        usd_amount=request.json["usd_amount"],
        lbp_amount=request.json["lbp_amount"],
        usd_to_lbp=request.json["usd_to_lbp"]
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({"message": "Transaction added"}), 201

