from flask import Flask, render_template, url_for, request, jsonify, redirect, json
from pymongo import MongoClient
from flask_mail import Mail, Message
from datetime import date
import time
import sys
from user import user_api
from flask_jwt_extended import (
	JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, jwt_optional
)
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
mail = Mail(app)
app.register_blueprint(user_api)

@app.route("/")
@jwt_optional
def home():
    c_user= get_jwt_identity()
    if c_user:
        return render_template('main.html')
    else:
        return render_template('login.html')

@app.route("/additem",methods=["POST"])
@jwt_required
def additem():
    c_user=get_jwt_identity()
    content = request.json.get("content",None)
    ctime= time.time()
    item_json={
        "username":c_user,
        "property":{
            "likes":0
        },
        "retweeted":0,
        "content": content,
        "timestamp":ctime
    }

    client = MongoClient()
    db= client.naft

    db.items.insert_one(item_json)
    return jsonify({"status":"OK"})

@app.route("/adduser",methods=['POST'])
def addusr():
    try:
	name=request.json.get("username",None)
	password=request.json.get("password",None)
	email=request.json.get("email",None)

        hashed_password= generate_password_hash(password)

        client = MongoClient()
        db= client.naft

        json={
            "username":name,
            "email":email,
            "password":hashed_password,
            "posts":[],
            "likes":[],
            "reposts":[],
            "following":[],
            "followers":[],
            "verified":"false"
            }
        #Add new user to database
        uid = db.users.insert_one(json)
        json2= {"email":email,"key":str(uid.inserted_id)}
        db.verified.insert_one(json2)

        # send verification email
        key= "validation key: <"+str(uid.inserted_id)+">\n"
        url="http://cowzilla.cse356.compas.cs.stonybrook.edu/verify?email={}&key={}".format(email,str(uid.inserted_id))
        body="Please verify you email with this code:\n "+key+url
        msg= Message(subject="Verify Email",body=body,sender="ubuntu@wu1.cloud.compas.cs",recipients=[email])
        mail.send(msg)

        # redirect to verification page and return status: OK
        return jsonify({"status":"OK"})
    except Exception, e:
        return jsonify({"status":"ERROR","error":str(e)}) # return status: ERROR if there is an exception

@app.route("/reset",methods=["GET"])
def reset():
    client = MongoClient()
    db= client.naft

    db.users.drop()
    db.verified.drop()
    db.items.drop()
    return "All tables reset"

