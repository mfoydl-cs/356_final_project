from flask import Flask, render_template, url_for, request, jsonify, redirect, json
from datetime import date
import sys
from user import user_api

app = Flask(__name__)
app.register_blueprint(user_api)

@app.route("/")
def hello():
    return "Hello World"
