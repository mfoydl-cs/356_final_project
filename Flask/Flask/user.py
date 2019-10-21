from flask import Flask, render_template, url_for, request, jsonify, redirect, json, Blueprint
from pymongo import MongoClient
from flask_mail import Mail, Message
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

@user_api.route("/adduser",methods=['POST'])
def addusr():
	name= request.json.get('username', None)
	password= request.json.get('password', None)
	email= request.json.get('email', None)

	client = MongoClient()
	db= client.users
	'''
	json= {"username":name,"password":password,"email":email,"verified":"false"}
	uid = db.users.insert_one(json)
	json2= {"email":email,"key":str(uid)}
	db.verified.insert_one(json2)

	key= "validation key: <"+str(uid.inserted_id)+">\n"
	url="http://cowzilla.cse356.compas.cs.stonybrook.edu/verify?email={}&key={}".format(email,str(uid.inserted_id))
	body="Please verify you email with this code:\n "+key+url
	msg= Message(subject="Verify Email",body=body,sender="ubuntu@wu1.cloud.compas.cs",recipients=[email])
	mail.send(msg)
	json_user = {"username":name,"human":"0","wopr":"0","tie":"0","current":"0","games":[],"gamesinfo":[]}
	db.info.insert_one(json_user)
	'''
	return jsonify({"status":"OK"})

@user_api.route("/unverified")
def unverified():
	return render_template("unverified.html")

@user_api.route("/verify",methods=['POST','GET'])
def verify():
    return "verify"

@user_api.route("/login",methods=["POST"])
def login():
    return 'login'  

@user_api.route('/token/refresh', methods=['POST'])
#@jwt_refresh_token_required
def refresh():
    return "refresh"

@user_api.route("/logout",methods=["POST"])
def logout():
    return "logout"
