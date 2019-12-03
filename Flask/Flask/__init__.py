from flask import Flask, render_template, url_for, request, jsonify, redirect, json, abort, make_response
import pymongo
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
from werkzeug import generate_password_hash, check_password_hash, secure_filename
import elasticsearch
from elasticsearch import Elasticsearch, RequestsHttpConnection, serializer, compat, exceptions
from gridfs import GridFS
import mimetypes
import logging


#from werkzeug.contrib.profiler import ProfilerMiddleware

app = Flask(__name__)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
mail = Mail(app)

app.register_blueprint(user_api)
fs = GridFS(MongoClient('localhost',27017,maxPoolSize=100).media)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','mp4'}

#app.config['DEBUG'] = True
#app.config['PROFILE'] = True
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[800])

client = MongoClient('localhost',27017,maxPoolSize=100)

es = Elasticsearch('http://localhost:9200')

@app.route("/")
@jwt_optional
def home():
    #try:
    c_user= get_jwt_identity()
    if c_user:
        #client = MongoClient()
        db= client.naft
        #items = db.items.find()
        return render_template('main.html',items=[])
    else:
        return render_template('all.html')
    #except Exception as e:
@app.route("/loginpage")
def loginpage():
    return render_template('login.html')

@app.route("/additem",methods=["POST"])
@jwt_required
def additem():
    c_user=get_jwt_identity()
    content = request.json.get("content",None)
    childType = request.json.get("childType",None)
    parent = request.json.get("parent",None)
    media = request.json.get("media",None)
    ctime= time.time()
    mid = c_user+str(ctime)
    mid = mid.replace(".","_")
    
    db= client.naft
    if media:
        for item in list(media):
            if item != "":
                m = db.media.find_one({"oid":item})
                if m and m['attatched'] == "false" and m['user']==c_user:
                    db.media.update_one({"oid":item},{"$set":{"attatched":"true"}})
                else:
                    return jsonify({"status":"error","error":"Media Upload Not Allowed"}),409
            
    item_json={
        "id":mid,
        "username":c_user,
        "property":{
            "likes":0
        },
        "retweeted":0,
        "content": content,
        "childType": childType,
        "parent": parent,
        "media":media,
        "timestamp":ctime
    }

    #SEND RETWEET TO ASYNC
    if(childType=="retweet"):
        q = {
                "script": {
                    "inline": "ctx._source.retweeted+=1"
                }
        }
        es.update(index='posts',id=parent,body=q)
    
    #SEND POST TO ASYNC
    es.index(index="posts",id=mid,body=item_json)
    db.users.update_one({"username":c_user},{"$push":{"posts":mid}})

    return jsonify({"status":"OK","id":mid})

@app.route("/item/<mid>", methods=["GET","DELETE"])
@jwt_optional
def getitem(mid):
    try:
        item = es.get(index="posts",id=mid)
        if(request.method == 'DELETE'):
            user =  get_jwt_identity()
            if user:
                #client = MongoClient()
                db= client.naft
                if mid in db.users.find_one({"username":user})['posts']:
                    media = item['_source']['media']
                    if media != None:
                        for m in media:
                            iid = db.fs.files.find_one({"oid":m})['_id']
                            fs.delete(iid)
                    es.delete(index="posts",id=mid)
                    return jsonify({"status":"OK"})
                else:
                    return jsonify({"status":"error","error":"User does not own post"}),401
            else:
                return jsonify({"status":"error","error":"User is not logged in"}),401
        else:
            #item = es.get(index="posts",doc_type='post',id=mid)
            return jsonify({"status":"OK","item":item['_source']})
    except Exception as e:
        return jsonify({"status":"error","error":str(e)}),409

@app.route("/item/<mid>/like",methods=["POST"])
@jwt_required
def likeitem(mid):
    user = get_jwt_identity()
    try:
        like= request.json.get("like",bool)
        #client = MongoClient()
        db= client.naft
        if like == None:
            like = True
        if like ==True:
            if mid in db.users.find_one({"username":user})['likes']:
                return jsonify({"status":"OK"})
            line="ctx._source.property.likes+=1"
            db.users.update_one({"username":user},{"$push":{"likes":mid}})
        elif like == False:
            if mid in db.users.find_one({"username":user})['likes']:
                line="ctx._source.property.likes-=1"
                db.users.update_one({"username":user},{"$pull":{"likes":mid}})
            else:
                return jsonify({"status":"OK"})
        q = {
                "script": {
                    "inline": line
                }
        }
        es.update(index='posts',id=mid,body=q)
        return jsonify({"status":"OK"})
    except Exception as e:
        return jsonify({"status":"error","error":str(e)}),409


@app.route("/user/<username>",methods=["GET"])
def getUser(username):
    try:
        #client = MongoClient()
        db= client.naft
        user= db.users.find_one({"username":username})
        if user is None:
            return jsonify({"status":"error","error":"User not found"}),404
        return jsonify({"status":"OK","user":{"email":user['email'],"followers":len(user['followers']),"following":len(user['following'])}})
    except Exception as e:
        return jsonify({"status":"error","error":str(e)})

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
        #client = MongoClient()
        db = client.naft
        user = db.users.find_one({"username":username})
        posts= user['posts'][:limit]
        return jsonify({"status":"OK","items":posts})
    except Exception as e:
        return jsonify({"status":"error","error":str(e)}),409

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
        #client = MongoClient()
        db = client.naft
        user = db.users.find_one({"username":username})
        users= user['followers'][:limit]
        return jsonify({"status":"OK","users":users})
    except Exception as e:
        return jsonify({"status":"error","error":str(e)})

@app.route("/user/<username>/following",methods=["GET"])
def getUserFollowing(username):
    try:
        limit = request.args.get("limit")
        if limit:
            limit= int(limit)
            if(limit > 200):
                limit = 200
        else:
            limit = 50
        #client = MongoClient()
        db = client.naft
        user = db.users.find_one({"username":username})
        users= user['following'][:limit]
        return jsonify({"status":"OK","users":users})
    except Exception as e:
        return jsonify({"status":"error","error":str(e)}),409

@app.route("/follow",methods=["POST"])
@jwt_required
def follow():
    try:
        user = get_jwt_identity()
        username= request.json.get("username",None)
        follow= request.json.get("follow",bool)
        if(username):
            #client = MongoClient()
            db = client.naft
            user1= db.users.find_one({"username":username})
            user2= db.users.find_one({"username":user})
            if user1 is None:
                return jsonify({"status":"error","error":"User1 not found","user":username}),404
            if user2 is None:
                return jsonify({"status":"error","error":"User2 Not Found"}),404
            if(follow ==  True):
                db.users.update_one({"username":user},{"$push":{"following":username}})
                db.users.update_one({"username":username},{"$push":{"followers":user}})
                return jsonify({"status":"OK"})
            else:
                db.users.update_one({"username":user},{"$pull":{"following":username}})
                db.users.update_one({"username":username},{"$pull":{"followers":user}})
            return jsonify({"status":"OK"})
    except Exception as e:
        return jsonify({"status":"error","error":str(e)}),409

@app.route("/user/<username>/show")
@jwt_optional
def showUser(username):
    query = {"query":{'match':{'username':username}}}
    search = es.search(index="posts",body=query, size=25)
    items = getPosts(search)
    #client = MongoClient()
    db = client.naft
    user= get_jwt_identity()
    follow=False
    logged=False
    if user:
        logged=True
        user1= db.users.find_one({"username":user})
        if user1:
            following = user1['following']
            if username in following:
                follow=True
    return render_template('user.html',username=username,items=items,follow=follow,logged=logged,user=user)

@app.route("/getuser",methods=["POST"])
@jwt_required
def getusername():
    try:
        username = get_jwt_identity()
        return jsonify({"status":"OK","user":username})
    except Exception as e:
        return jsonify({"status":"error","error":str(e)}),409

@app.route("/adduser",methods=['POST'])
def addusr():
    try:
        name=request.json.get("username",None)
        password=request.json.get("password",None)
        email=request.json.get("email",None)

        #hashed_password= generate_password_hash(password)

        #client = MongoClient('localhost',27017,maxPoolSize=100)
        db= client.naft
        if db.users.find_one({"username":name},{"username":1,"_id":0}) != None:
            return jsonify({"status":"error","error":"Username taken"}),409
        if db.users.find_one({"email":email},{"email":1,"_id":0}) != None:
            return jsonify({"status":"error","error":"Email already in use"}),409
        json={
            "username":name,
            "email":email,
            "password":password,
            "posts":[],
            "likes":[],
            "reposts":[],
            "following":[],
            "followers":[],
            "verified":"false"
            }

        # SEND VERIFY AND EMAIL TO ASYNC TASK

        #Add new user to database
        uid = db.users.insert_one(json)
        key = str(uid.inserted_id)
        json2= {"email":email,"key":key}
        db.verified.insert_one(json2)

        # send verification email
        key= "validation key: <"+str(uid.inserted_id)+">\n"
        url="http://cowzilla.cse356.compas.cs.stonybrook.edu/verify?email={}&key={}".format(email,key)
        body="Please verify you email with this code:\n "+key+url
        msg= Message(subject="Verify Email",body=body,sender="ubuntu@wu1.cloud.compas.cs",recipients=[email])
        mail.send(msg)

        #return status: OK
        return jsonify({"status":"OK"})
    except Exception as e:
        return jsonify({"status":"error","error":str(e)}),409 # return status: error if there is an exception

@app.route("/search",methods=["POST"])
@jwt_optional
def search():
    try:
        timestamp = request.json.get('timestamp',None)
        limit = request.json.get('limit',None)
        q = request.json.get('q',None)
        username = request.json.get('username',None)
        following = request.json.get('following',bool)
        rank = request.json.get('rank',None)
        parent = request.json.get('parent',None)
        replies = request.json.get('replies',bool)
        hasMedia = request.json.get('hasMedia',bool)
        

        query = {"query":{'bool':{'must':[],'must_not':[],'filter':[]}},'sort':[]}
        if q and str(q) != "":
            query['query']['bool']['must'].append({'match':{'content':q}})
        else:
            query['query']['bool']['must'].append({'match_all':{}})

        if timestamp:
            query['query']['bool']['must'].append({'range':{'timestamp':{'lte':timestamp}}})
        if username:
            query['query']['bool']['filter'].append({'match':{'username':username}})
        if following == True:
            fusers=[]
            #client = MongoClient()
            db = client.naft
            if get_jwt_identity():
                user = db.users.find_one({"username":get_jwt_identity()})
                fusers= user['following']
                query['query']['bool']['filter'].append({'match':{'username':fusers}})
        
        
        if rank != 'time':
            query['sort'].append({'_script':{"type":"number","script":" return doc['retweeted'].value + doc['property.likes'].value","order":'desc'}})
        if replies == False:
            query['query']['bool']['must_not'].append({'match':{'childType':'reply'}})
        if parent:
            if replies != False:
                query['query']['bool']['filter'].append({'match':{'parent':parent}})
        if hasMedia and hasMedia == True:
            query['query']['bool']['filter'].append({'exists':{'field':"media"}})
        if limit:
            if limit > 100:
                search = es.search(index="posts",body=query, size=100)
            else:
                search = es.search(index="posts",body=query, size=limit)
        else:
            search = es.search(index="posts",body=query, size=25)
        posts=[]
        for item in search['hits']['hits']:
            posts.append(item['_source'])
        if rank == 'time':
            #query['sort'].append({"timestamp":{'order':'desc'}})
            posts.sort(key=etimestamp,reverse=True)

        return jsonify({"status":"OK","items":posts,"q":query})
    except elasticsearch.RequestError as es1:
        return jsonify({"status":"OK","items":[]})

    except Exception as e:
        app.logger.error('    SearchError:   '+str(e))
        return jsonify({"status":"error","error":str(e)}),409
def etimestamp(json):
    try:
        return float(json['timestamp'])
    except KeyError:
        return 0


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

def getPosts(s):
    #client = MongoClient()
    #db= client.naft
    posts=[]
    items = s['hits']['hits']
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
    return jsonify({"status":"error","error":"User must log in"}),401

# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def my_expired_token_callback():
	try:
		resp = jsonify({"status":"error","error":"User was logged out"})
		unset_jwt_cookies(resp)
		return resp, 200
	except Exception as e:
		return jsonify({"status":"error","error":str(e)}),401
@jwt.unauthorized_loader
def my_unauthorized_loader_callback(callback):
    return jsonify({"status":"error","error":"User not logged in"}),401


@app.route("/reset",methods=["GET"])
def reset():
    #client = MongoClient()
    db= client.naft

    db.users.drop()
    db.verified.drop()
    es.indices.delete(index="posts",ignore=[400,404])
    
    db.fs.files.drop()

    db.users.create_index([('username', pymongo.ASCENDING)],unique=True)
    db.media.create_index([('oid', pymongo.ASCENDING)],unique=True)
    mapping={
        "mappings": {
            "properties":{
                "id":{"type":"keyword"},
                "username":{"type":"keyword"},
                
                "retweeted":{"type":"integer"},
                "content":{"type":"text"},
                "childType":{"type":"keyword"},
                "parent":{"type":"keyword"},
                "media":{"type":"keyword"},
                "timestamp":{"type":"float"},
                "property":{"type":"object","properties":{"likes":{"type":"integer"}}}
            }
        }
    }
    response = es.indices.create(index="posts",body=mapping,ignore=400)
    return jsonify({"status":"OK","response":response})


@app.route("/addmedia",methods=["POST"])
@jwt_required
def addmedia():
    try:
        c_user = get_jwt_identity()
        if 'content' not in request.files:
            return jsonify({"status":"error","error":"no content provided"}),409
        file = request.files['content']
        if not file.filename:
            return jsonify({"status":"error","error":"no filename provided"}),409
        if file and allowed_file(file.filename) and c_user:
            filename= secure_filename(file.filename)
            oid = c_user+str(time.time())
            fs.put(file, content_type=file.content_type, filename=filename,oid=oid)
            #client = MongoClient()
            db= client.naft
            db.media.insert_one({"user":c_user,"oid":oid,"attatched":"false"})
            return jsonify({"status":"OK","id":oid})
        else:
            return jsonify({"status":"error","error":"file type not allowed"}),405
    except Exception as e:
        return jsonify({"status":"error","error":str(e)}),409


@app.route("/media/<oid>", methods=["GET"])
def getmedia(oid):
    try:
        file = fs.find_one({"oid":oid})
        response = make_response(file.read())
        response.mimetype = file.content_type
        return response, 200
    except:
        return jsonify({"status":"error","error":"file not found"}),404
    

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user(username):
    #while True:
        #result,cas = mclient.get(username)
    result = mc.get(username)
    if result == "None":
        #client = MongoClient()
        db= client.naft
        result = db.users.find_one({"username":username},{"username":1,"_id":0})
        mc.set(username,result)
        return result
    #    if mclient.cas(username,result,cas):
    #        break
    return result
    

@app.route("/test",methods=["GET"])
def test():
    try:
        app.logger.error('TestLog'+str(5))
        return jsonify({"status":"OK"})
    except Exception as e:
        return jsonify({"Error":str(e)})





