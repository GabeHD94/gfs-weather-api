from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
import io

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://cusebgzelwxcoz:d1965231c24ca93521e9e8c4ffa9a545bed04b9025065c23afaa43ae6d5496fe@ec2-34-225-162-157.compute-1.amazonaws.com:5432/d3kj5thujanvjs"

db = SQLAlchemy(app)
ma = Marshmallow(app)

heroku = Heroku(app)
CORS(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(), nullable=True)

    def __init__(self, username, password, location):
        self.username = username
        self.password = password
        self.location = location

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password", "location")

user_schema = UserSchema()
many_users_schema = UserSchema(many=True)

@app.route("/user/create", methods=["POST"])
def create_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")
    location = post_data.get("location")

    username_check = db.session.query(User.username).filter(User.username == username).first()
    if username_check is not None:
        return jsonify("Username Taken")
        
    record = User(username, password, location)
    db.session.add(record)
    db.session.commit()

    return jsonify("User Created Successfully")

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(many_users_schema.dump(all_users))



# @app.route("/user/get/<id>", methods=["GET"])
# def get_user_by_id(id):
#     user = db.session.query(User).filter(User.id == id).first()
#     return jsonify(user_schema.dump(user))

# @app.route("/location/get/data/<username>", methods=["GET"])
# def get_location_by_username(username):
#     user_id = db.session.query(User.id).filter(User.username == username).first()[0]
#     user_location = db.session.query(User).filter(User.user_id == username).first()[0]
#     return jsonify(user_schema.dump(user_location))

@app.route("/user/get/<username>", methods=["GET"])
def get_user_by_id(username):
    user = db.session.query(User).filter(User.username == username).first()
    return jsonify(user_schema.dump(user))



@app.route("/user/verification", methods=["POST"])
def verify_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")
    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")
    location = post_data.get("location")


    stored_password = db.session.query(User.password).filter(User.username == username).first()

    if stored_password is None:
        return jsonify("User Not Verified")

    if stored_password[0] != password:
        return jsonify("User Not Verified")
 
    return jsonify("User Verified")


if __name__ == "__main__":
    app.run(debug=True)
