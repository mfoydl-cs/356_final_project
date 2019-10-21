from flask import Flask, render_template, url_for, request, jsonify, redirect, json, Blueprint
from pymongo import MongoClient
from flask_mail import Mail, Message
from flask_jwt_extended import (
	JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

user_api = Blueprint('user_api','user_api')

@app.route("/adduser",methods=['POST'])
def addusr():
    return "addusr"

@app.route("/unverified")
def unverified():
	return render_template("unverified.html")

@app.route("/verify",methods=['POST','GET'])
def verify():
    return "verify"

	

@app.route("/login",methods=["POST"])
def login():
    return 'login'  

@app.route('/token/refresh', methods=['POST'])
#@jwt_refresh_token_required
def refresh():
    return "refresh"

@app.route("/logout",methods=["POST"])
def logout():
    return "logout"