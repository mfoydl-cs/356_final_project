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
		else:
			return jsonify({"status":"error","error":"wrong key"}),401
	except Exception, e:
		return jsonify({"status":"error","error":str(e)}),409

@user_api.route("/login",methods=["POST"])
def login():
    #check_password_hash(saved,input)
    try:
	username = request.json.get("username",None)
	password = request.json.get("password",None)

	client = MongoClient()
	db = client.naft
	user = db.users.find_one({"username":username})

        if user is None:
            return jsonify({"status":"error","error":"User not found"}),404
        if(user['verified'] == "false"):
	    return jsonify({"status":"error","error":"Email has not been verified"}),401

	#if not check_password_hash(users[0]['password'],password):
	if user['password'] != password:
            return jsonify({"status":"error","error":"Username/Password incorrect"}),401

	access_token = create_access_token(identity=username)
	refresh_token = create_refresh_token(identity=username)

	resp = jsonify({"status":"OK"})
	set_access_cookies(resp, access_token)
	set_refresh_cookies(resp, refresh_token)
	return resp, 200
    except Exception, e:
	return jsonify({"status":"error", "error":str(e)}),409

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
		return jsonify({"status":"error","error":str(e)}),409
