import pymongo
from datetime import datetime
from pytz import timezone
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
        "activated": False,
        "siac_filter": False
    }
    user_id = users.insert_one(user).inserted_id
    return user_id

def addGeneralFeedback(author_id, teacher_id, timestamp, contents):
    # get the teacher to see if they want to filter through SIAC Admin first
    teacher = db.users.find_one({"_id":teacher_id})
    siac_filter = teacher["siac_filter"]
    
    # create feedback, if siac_filter is on, then don't automatically approve
    feedback = {
        "author": author_id,
        "teacher": teacher_id,
        "timestamp": timestamp,
        "contents": contents,
        "approved": not siac_filter
    }
    feedback_id = db.general.insert_one(feedback).inserted_id
    return feedback_id

def user(id):
    return db.users.find_one({"_id" : ObjectId(id)})

def userById(user_id):
    return db.users.find_one({"_id":user_id})

def userByUsername(username):
    return db.users.find_one({"username" : username})

def currentUser():
    result = db.users.find({"_id" : ObjectId(session["id"]) if "id" in session else 0})
    if result.count() == 1:
        return result[0]
    else:
        return None

def authenticate(username, password):
    user = userByUsername(username)
    if user == None:
        return False
    hashed_pass = user["password"]
    return check_password(password, hashed_pass)

def usernameAvailable(username):
    matches = db.users.find({"username" : username}).count()
    return True if matches == 0 else False

def userActivated(user):
    return db.users.find_one({"_id" : user})['activated']

def activateUser(user):
    result = db.users.update_one({"_id":user}, {"$set":{"activated":True}})
    return (result == 1)

def validUserID(id):
    result = db.users.find({"_id":id}).count()
    return (result == 1)

def currentUserActive():
    return userActivated(ObjectId(session['id']))

def teachersInSchool(school):
    query = db.users.find({"acct_type":"Teacher", "school":school})
    return query

def pendingFeedback():
    query = db.general.find({"approved":False})
    result = []
    for feedback in query:
        feedback["timestamp"] = datetime.fromtimestamp(feedback['timestamp'], timezone('US/Pacific')).strftime("%m/%d/%Y %I:%M:%S %p")
        result.append(feedback)
    return result

def approveGeneralFeedback(feedback_id):
    result = db.general.update_one({"_id":feedback_id}, {"$set":{"approved":True}})
    return result

def deleteGeneralFeedback(feedback_id):
    result = db.general.delete_one({"_id":feedback_id})
    return result

def generalFeedbackForTeacher(teacher_id):
    query = db.general.find({"teacher":teacher_id, "approved":True})
    result = []
    for feedback in query:
        feedback["timestamp"] = datetime.fromtimestamp(feedback['timestamp'], timezone('US/Pacific')).strftime("%m/%d/%Y %I:%M:%S %p")
        result.append(feedback)
    return result

def toggleFilter(teacher_id):
    teacher = db.users.find_one({"_id":teacher_id})
    result = db.users.update_one({"_id":teacher_id}, {"$set":{"siac_filter": not teacher["siac_filter"]}})
    return result

def addCourse(teacher_id, name, password):
    course = {
        "teacher_id": teacher_id,
        "name": name,
        "password": password
    }
    course_id = db.courses.insert_one(course).inserted_id
    return course_id

def courseById(course_id):
    return db.courses.find_one({"_id":course_id})

def coursesForTeacher(teacher_id):
    query = db.courses.find({"teacher_id":teacher_id})
    result = []
    for course in query:
        result.append(course)
    return result
