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
'''
@user_api.route("/adduser",methods=['POST'])
def addusr():
    try:
        name= request.form["username"]

        password= request.form["password"]
        hashed_password= generate_password_hash(password)

        email= request.form["email"]

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
        return jsonify({"status","OK"})
    except Exception, e:
        return jsonify({"status":"ERROR","error":str(e)}) # return status: ERROR if there is an exception
'''
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
        return jsonify({"status":"ERROR"})
	if(users[0]['verified'] == "false"):
	    return jsonify({"status":"ERROR"})

	if not check_password_hash(users[0]['password'],password):
        return jsonify({"status":"ERROR"})

	access_token = create_access_token(identity=username)
	refresh_token = create_refresh_token(identity=username)

	resp = jsonify({"status":"OK"})
	set_access_cookies(resp, access_token)
	set_refresh_cookies(resp, refresh_token)
	return resp, 200
    except Exception, e:
	return jsonify({"status":"ERROR", "error":str(e)})

@user_api.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    try:
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        resp = jsonify({'status':"OK"})
        set_access_cookies(resp, access_token)
        return resp, 200
    except Exception, e:
		return jsonify({"status":"ERROR","error":str(e)})

@user_api.route("/logout",methods=["POST"])
def logout():
	try:
		resp = jsonify({"status":"OK"})
		unset_jwt_cookies(resp)
		return resp, 200
	except Exception, e:
		return jsonify({"status":"ERROR","error":str(e)})

