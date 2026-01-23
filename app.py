from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")


app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@localhost:3306/exchange"

db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usd_amount = db.Column(db.Float, nullable=False)
    lbp_amount = db.Column(db.Float, nullable=False)
    usd_to_lbp = db.Column(db.Boolean, nullable=False)



@app.route("/transaction", methods=["POST"])
@limiter.limit("10 per minute")
def add_transaction():
    usd_amount = float(request.json.get("usd_amount"))
    lbp_amount = float(request.json.get("lbp_amount"))
    usd_to_lbp = request.json.get("usd_to_lbp")

    if usd_amount <= 0:
        return jsonify({"error": "Invalid usd_amount"}), 400

    if  lbp_amount <= 0:
        return jsonify({"error": "Invalid lbp_amount"}), 400

    if type(usd_to_lbp) is not bool:
        return jsonify({"error": "Invalid usd_to_lbp"}), 400

    transaction = Transaction(
        usd_amount=usd_amount,
        lbp_amount=lbp_amount,
        usd_to_lbp=usd_to_lbp
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({"message": "Transaction added"}), 201


@app.route("/exchangeRate", methods=["GET"])
def get_exchange_rate():
    tu_to_l = Transaction.query.filter_by(usd_to_lbp=True).all()
    tl_to_u = Transaction.query.filter_by(usd_to_lbp=False).all()

    if len(tu_to_l) > 0:
        total_lbp = sum(t.lbp_amount for t in tu_to_l)
        total_usd = sum(t.usd_amount for t in tu_to_l)
        avg_usd_to_lbp = total_lbp / total_usd
    else:
        avg_usd_to_lbp = None

    if len(tl_to_u) > 0:
        total_usd = sum(t.usd_amount for t in tl_to_u)
        total_lbp = sum(t.lbp_amount for t in tl_to_u)
        avg_lbp_to_usd = total_usd / total_lbp
    else:
        avg_lbp_to_usd = None

    return jsonify({
        "usd_to_lbp_rate": avg_usd_to_lbp,
        "lbp_to_usd_rate": avg_lbp_to_usd
    })


if __name__ == "__main__":
    app.run(debug=False)


