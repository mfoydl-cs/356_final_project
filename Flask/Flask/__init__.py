from flask import Flask, render_template, url_for, request, jsonify, redirect, json
from datetime import date
import sys

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World"