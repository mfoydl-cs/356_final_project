from flask import Flask, render_template, url_for, request, jsonify, redirect, json
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
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
from elasticsearch import Elasticsearch

app = Flask(__name__)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
#app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
mail = Mail(app)
es = Elasticsearch('http://localhost:9200')
app.register_blueprint(user_api)

@app.route("/")
@jwt_optional
def home():
    #try:
    c_user= get_jwt_identity()
    if c_user:
        client = MongoClient()
        db= client.naft
        #items = db.items.find()
        return render_template('main.html',items=getfeed())
    else:
        return render_template('login.html')
    #except Exception, e:


@app.route("/additem",methods=["POST"])
@jwt_required
def additem():
    c_user=get_jwt_identity()
    content = request.json.get("content",None)
    ctime= time.time()
    mid = c_user+str(ctime)
    item_json={
        "id":mid,
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

    #db.items.insert_one(item_json)
    es.index(index="posts",id=mid,doc_type="post",body=item_json)
    db.users.update_one({"username":c_user},{"$push":{"posts":mid}})
    return jsonify({"status":"OK"})

@app.route("/item/<mid>", methods=["GET","DELETE"])
def getitem(mid):
    try:
        #client = MongoClient()
        #db=client.naft

        if(request.method == 'DELETE'):
            #db.items.update_one({"$pull":{"mid":mid}})
            es.delete(index="posts",doc_type="post",id=mid)
            return jsonify({"status":"OK"})
        else:
            #item = db.items.find_one({"mid":mid},{"_id":0})
            item = es.get(index="posts",doc_type='post',id=mid)
            return jsonify({"status":"OK","item":dumps(item['_source'])})
    except Exception, e:
        return jsonify({"status":"ERROR","error":str(e)})

@app.route("/user/<username>",methods=["GET"])
def getUser(username):
    try:
        client = MongoClient()
        db= client.naft
        user= db.users.find_one({"username":username})
        return jsonify({"status":"OK","user":{"email":user['email'],"followers":len(user['followers']),"following":len(user['following'])}})
    except Exception, e:
        return jsonify({"status":"ERROR","error":str(e)})

@app.route("/user/<username>/posts",methods=["GET"])
def getUserPosts(username):
    try:
        limit = request.args.get("limit")
        if(limit):
            limit= int(limit)
            if(limit > 200):
                limit = 200
        else:
            limit = 50
        client = MongoClient()
        db = client.naft
        user = db.users.find_one({"username":username})
        posts= user['posts'][:limit]
        return jsonify({"status":"OK","items":posts})
    except Exception, e:
        return jsonify({"status":"ERROR","error":str(e)})

@app.route("/user/<username>/followers",methods=["GET"])
def getUserFollowers(username):
    try:
        limit = request.args.get("limit")
        if(limit):
            limit= int(limit)
            if(limit > 200):
                limit = 200
        else:
            limit = 50
        client = MongoClient()
        db = client.naft
        user = db.users.find_one({"username":username})
        users= user['followers'][:limit]
        return jsonify({"status":"OK","users":users})
    except Exception, e:
        return jsonify({"status":"ERROR","error":str(e)})

@app.route("/user/<username>/following",methods=["GET"])
def getUserFollowing(username):
    try:
        limit = request.args.get("limit")
        if(limit):
            limit= int(limit)
            if(limit > 200):
                limit = 200
        else:
            limit = 50
        client = MongoClient()
        db = client.naft
        user = db.users.find_one({"username":username})
        users= user['following'][:limit]
        return jsonify({"status":"OK","users":users})
    except Exception, e:
        return jsonify({"status":"ERROR","error":str(e)})

@app.route("/follow")
@jwt_required
def follow():
    try:
        user = get_jwt_identity()
        username= request.json.get("username",None)
        follow= request.json.get("follow",None)
        if(username):
            client = MongoClient()
            db = client.naft
            if(follow):
                db.users.update_one({"username":user},{"$push":{"following":username}})
                db.users.update_one({"username":username},{"$push":{"followers":user}})
            else:
                db.users.update_one({"username":user},{"$pull":{"following":username}})
                db.users.update_one({"username":username},{"$pull":{"followers":user}})
            return jsonify("status","OK")
    except Exception, e:
        return jsonify({"status":"ERROR","error":str(e)})

@app.route("/user/<username>/show")
def showUser(username):
    return render_template('user.html')



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

@app.route("/search",methods=["POST"])
def search():
    timestamp = request.json.get('timestamp',None)
    limit = int(request.json.get('limit',None))
    q = request.json.get('q',None)
    username = request.json.get('username',None)
    following = bool(request.json.get('following',None))
    query = {'query':{}}
    if q and q not "":
        match = {"match":{'text':q}}
        query['query']+=match
    if timestamp:
        time = {'timestamp':{'gte':timestamp}}
        query['query']+=time
    if username:
        user = {'username':username}
        query['query']+=user
    return query

@app.route("/reset",methods=["GET"])
def reset():
    client = MongoClient()
    db= client.naft

    db.users.drop()
    db.verified.drop()
    db.items.drop()
    return "All tables reset"

def getfeed():
    #client = MongoClient()
    #db= client.naft
    posts=[]
    q = es.search(index="posts",size=25)
    items = q['hits']['hits']
    for i in items: #db.items.find()
        item=i['_source']
        username=item["username"]
        content=item["content"]
        timestamp=(time.time()-item["timestamp"])
        if timestamp/3600 < 1:
            timestamp=str(truncate(timestamp/60))+"m"
        elif timestamp/3600 > 24:
            timestamp=str(truncate(timestamp/86400))+"d"
        else:
            timestamp=str(truncate(timestamp/3600))+"h"
        _id= i["_id"]
        post=[username,content,timestamp,_id]
        posts.append(post)
    return posts

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

@app.errorhandler(401)
def custom_401(error):
    return "hi this is a 401 error"

# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def my_expired_token_callback():
	try:
		resp = jsonify({"status":"OK","msg":"User was logged out"})
		unset_jwt_cookies(resp)
		return resp, 200
	except Exception, e:
		return jsonify({"status":"ERROR","error":str(e)})



