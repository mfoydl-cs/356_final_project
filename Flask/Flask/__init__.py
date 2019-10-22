from flask import Flask, render_template, url_for, request, jsonify, redirect, json
from pymongo import MongoClient
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

app = Flask(__name__)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
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
    content = request.form["content"]
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
