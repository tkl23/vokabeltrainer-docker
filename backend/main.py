
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder="public")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@vokabeltrainer-db/vokabeltrainer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(16), default="student")

class Vokabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deutsch = db.Column(db.String(64), nullable=False)
    englisch = db.Column(db.String(64), nullable=False)
    schwierigkeitsgrad = db.Column(db.String(16), nullable=False)

class Fortschritt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    vokabel_id = db.Column(db.Integer, nullable=False)
    korrekt = db.Column(db.Integer, default=0)

@app.route("/")
def home():
    return "Vokabeltrainer Backend läuft!"

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "Benutzer existiert bereits"}), 409
    u = User(username=data["username"], password=data["password"], role=data.get("role", "student"))
    db.session.add(u)
    db.session.commit()
    return jsonify({"msg": "Erfolgreich registriert"})

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"], password=data["password"]).first()
    if user:
        token = create_access_token(identity={"id": user.id, "username": user.username, "role": user.role})
        return jsonify(access_token=token)
    return jsonify({"msg": "Login fehlgeschlagen"}), 401

@app.route("/vokabeln", methods=["GET"])
@jwt_required()
def get_vokabeln():
    return jsonify([{"id": v.id, "de": v.deutsch, "en": v.englisch, "level": v.schwierigkeitsgrad} for v in Vokabel.query.all()])

@app.route("/fortschritt", methods=["GET"])
@jwt_required()
def fortschritt():
    user = get_jwt_identity()
    eintraege = Fortschritt.query.filter_by(user_id=user["id"]).all()
    gelernt = sum(1 for e in eintraege if e.korrekt >= 5)
    total = Vokabel.query.count()
    return jsonify({
        "gelernt": gelernt,
        "gesamt": total,
        "prozent": round(100 * gelernt / total, 1) if total else 0
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
