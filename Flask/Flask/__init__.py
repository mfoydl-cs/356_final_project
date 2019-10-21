from flask import Flask, render_template, url_for, request, jsonify, redirect, json
from datetime import date
import sys
from user import user_api
from flask_jwt_extended import (
	JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

app = Flask(__name__)
app.register_blueprint(user_api)

@app.route("/")
@jwt_optional
def home():
    c_user= get_jwt_identity()
    if c_user:
        return render_template('main.html')
    else:
        return render_template('login.html')
    