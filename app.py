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
           "usd_to_lbp": avg_usd_to_lbp,
            "lbp_to_usd": avg_lbp_to_usd
    })



