import pymongo
from pymongo import MongoClient
from bson import ObjectId
from flask import session
from helpers import *
client = MongoClient('mongodb://siac:debate3651!@ds023442.mlab.com:23442/siac')
db = client.siac

def addUser(username, hashed_pass, first, last, email, acct_type, school):
    users = db.users
    user = {
        "username": username,
        "password": hashed_pass,
        "first": first,
        "last": last,
        "email": email,
        "acct_type": acct_type,
        "school": school,
        "activated": False
    }
    user_id = users.insert_one(user).inserted_id
    return user_id

def user(id):
    return db.users.find_one({"_id" : ObjectId(id)})

def userByUsername(username):
    return db.users.find_one({"username" : username})

def currentUser():
    return db.users.find_one({"_id" : ObjectId(session["id"])})

def authenticate(username, password):
    user = userByUsername(username)
    hashed_pass = user["password"]
    return check_password(password, hashed_pass)

def usernameAvailable(username):
    matches = db.users.find({"username" : username}).count()
    return True if matches == 0 else False

def userActivated(user):
    return db.users.find_one({"_id" : user})['activated']

def activateUser(user):
    result = db.users.update_one({"_id":user}, {"$set":{"activated":True}}).count()
    return (result == 1)

def validUserID(id):
    result = db.users.find({"_id":id}).count()
    return (result == 1)

def currentUserActive():
    return userActivated(session['id'])