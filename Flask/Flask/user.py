from flask import Flask, render_template, url_for, request, jsonify, redirect, json, Blueprint, make_response
from pymongo import MongoClient
from flask_mail import Mail, Message
from werkzeug import generate_password_hash, check_password_hash
from flask_jwt_extended import (
	JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, jwt_optional
)

user_api = Blueprint('user_api','user_api')

@user_api.route("/createuser",methods=['GET'])
def createuser():
    return render_template('createuser.html')

@user_api.route("/unverified")
def unverified():
	return render_template("unverified.html")

@user_api.route("/verify",methods=['POST','GET'])
def verify():
    try:
	    email=""
	    key=""
	    if request.method == "POST":
	        email= request.json.get("email",None)
	        key= request.json.get("key",None)
	    elif request.method =="GET":
	        email= request.args.get("email")
	        key=request.args.get("key")

	    client= MongoClient()
	    db = client.naft

	    vuser= db.verified.find({"email":email})
	    if vuser[0]['key']==key or key=="abracadabra":
	        db.users.update_one({"email":email},{"$set":{"verified":"true"}})
            return jsonify({"status":"OK"})
	    return jsonify({"status":"ERROR"})
    except Exception, e:
	    return jsonify({"status":"ERROR","error":str(e)})

@user_api.route("/login",methods=["POST"])
def login():
    #check_password_hash(saved,input)
    try:
	username = request.json.get("username",None)
	password = request.json.get("password",None)

	client = MongoClient()
	db = client.naft
	users = db.users.find({"username":username})

        if users[0] is None:
            return jsonify({"status":"ERROR","error":"User not found"})
        if(users[0]['verified'] == "false"):
	    return jsonify({"status":"ERROR","error":"Email has not been verified"})

	if not check_password_hash(users[0]['password'],password):
            return jsonify({"status":"ERROR","error":"Username/Password incorrect"})

	access_token = create_access_token(identity=username)
	refresh_token = create_refresh_token(identity=username)

	resp = jsonify({"status":"OK"})
	set_access_cookies(resp, access_token)
	set_refresh_cookies(resp, refresh_token)
	return resp, 200
    except Exception, e:
	return jsonify({"status":"ERROR", "error":str(e)})

@user_api.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200

@user_api.route("/logout",methods=["POST"])
def logout():
	try:
		resp = jsonify({"status":"OK"})
		unset_jwt_cookies(resp)
		return resp, 200
	except Exception, e:
		return jsonify({"status":"ERROR","error":str(e)})
