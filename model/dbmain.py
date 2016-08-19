import pymongo
from datetime import datetime
from pytz import timezone
from pymongo import MongoClient
from bson import ObjectId
from flask import session
from helpers import *
client = MongoClient('mongodb://siac:debate3651!@ds023442.mlab.com:23442/siac')
db = client.siac

def timestampString(timestamp):
    return datetime.fromtimestamp(timestamp, timezone('US/Pacific')).strftime("%m/%d/%Y %I:%M:%S %p")

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
        "siac_filter": False,
        "settings": {
            "send_emails": True
        }
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

def userWithEmailExists(email):
    query = db.users.find({"email" : email})
    return query.count() > 0

def changeUserAttribute(user_id, attribute, value):
    query = db.users.update_one({"_id":user_id}, {"$set":{attribute:value}})
    return query

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

# teachers can manage Courses that students can join
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

def courseIfExists(course_id):
    query = db.courses.find({"_id":course_id})
    return query[0] if query.count() > 0 else None

def coursesForTeacher(teacher_id):
    query = db.courses.find({"teacher_id":teacher_id})
    result = []
    for course in query:
        course["count"] = numStudentsInCourse(course["_id"])
        result.append(course)
    return result

# a "Question" is posed by a teacher within a particular course
def addQuestion(course_id, qtype, timestamp, name):
    question = {
        "course_id": course_id,
        "qtype": qtype,
        "timestamp": timestamp,
        "name": name,
        "open":True
    }
    question_id = db.questions.insert_one(question).inserted_id
    return question_id

def questionById(question_id):
    return db.questions.find_one({"_id":question_id})

def removeQuestion(question_id):
    result = db.questions.delete_one({"_id":question_id})
    return result

def questionIfExists(question_id):
    query = db.questions.find({"_id":question_id})
    return query[0] if query.count() > 0 else None

def questionsForCourse(course_id):
    query = db.questions.find({"course_id":course_id})
    result = []
    for question in query:
        question["response_count"] = responseCountForQuestion(question["_id"])
        result.append(question)
    return result

def openQuestionsForCourse(course_id):
    query = db.questions.find({"course_id":course_id, "open":True})
    result = []
    for question in query:
        question["timestamp"] = timestampString(question["timestamp"])
        result.append(question)
    return result

# a "Response" is a student's answer to a teacher's question in a course
def addResponse(author_id, question_id, timestamp, contents):
    response = {
        "author_id": author_id,
        "question_id": question_id,
        "timestamp": timestamp,
        "contents": contents
    }
    response_id = db.responses.insert_one(response).inserted_id
    return response_id

# determines whether a student has already responded to a question
def responseExists(author_id, question_id):
    query = db.responses.find({"author_id":author_id, "question_id":question_id})
    return query.count() > 0
    

def responseCountForQuestion(question_id):
    return db.responses.find({"question_id":question_id}).count()

def responsesForQuestion(question_id):
    query = db.responses.find({"question_id":question_id})
    result = []
    for response in query:
        response["timestamp"] = timestampString(response["timestamp"])
        result.append(response)
    return result

def toggleQuestionOpen(question_id, open_status):
    result = db.questions.update_one({"_id":question_id}, {"$set":{"open":open_status}})
    return result

def deleteResponse(response_id):
    result = db.responses.delete_one({"_id":response_id})
    return result

def addRegistration(user_id, course_id):
    registration = {
        "user_id": user_id,
        "course_id": course_id
    }
    reg_id = db.registration.insert_one(registration).inserted_id
    return reg_id

def removeCourseRegistration(registration_id):
    result = db.registration.delete_one(registration_id)
    return result

def coursesForStudent(user_id):
    regs = db.registration.find({"user_id":user_id})
    result = []
    for reg in regs:
        course = db.courses.find_one({"_id":reg["course_id"]})
        course['teacher'] = userById(course['teacher_id'])
        result.append(course)
    return result

def studentsInCourse(course_id):
    regs = db.registration.find({"course_id":course_id})
    result = []
    for reg in regs:
        student = db.users.find_one({"_id":reg["user_id"]})
        result.append(student)
    return result

# get students who want to be mailed
def mailtoStudentsInCourse(course_id):
    regs = db.registration.find({"course_id":course_id})
    result = []
    for reg in regs:
        student = db.users.find_one({"_id":reg["user_id"]})
        if student['settings']['send_emails']:
            result.append(student)
    return result

def studentIsRegisteredForCourse(user_id, course_id):
    query = db.registration.find({"user_id":user_id, "course_id":course_id})
    return query.count() > 0

def numStudentsInCourse(course_id):
    query = db.registration.find({"course_id":course_id})
    return query.count()
    
def unregisteredCoursesForStudent(user_id):
    user = userById(user_id)
    courses = db.courses.find({}).sort('name', 1)
    result = []
    for course in courses:
        course['teacher'] = userById(course['teacher_id'])
        if not studentIsRegisteredForCourse(user_id, course['_id']) and course['teacher']['school'] == user['school']:
            result.append(course)
    return result

def authorOfGeneralFeedback(feedback_id):
    feedback = db.general.find_one({"_id":feedback_id})
    return feedback['author']

def authorOfResponse(feedback_id):
    feedback = db.responses.find_one({"_id":feedback_id})
    return feedback['author_id']

# function that adds a response from teacher to student
def addReply(teacher_id, student_id, timestamp, contents):
    reply = {
        "teacher_id": teacher_id,
        "student_id": student_id,
        "timestamp": timestamp,
        "contents": contents
    }
    reply_id = db.replies.insert_one(reply).inserted_id
    return reply_id

def repliesForStudent(student_id):
    query = db.replies.find({"student_id":student_id})
    result = []
    for reply in query:
        reply["timestamp"] = timestampString(reply["timestamp"])
        reply["teacher"] = userById(reply['teacher_id'])
        result.append(reply)
    return result

def deleteReply(reply_id):
    query = db.replies.delete_one({"_id":reply_id})
    return query

def toggleEmails(user_id):
    user = db.users.find_one({"_id":user_id})
    result = db.users.update_one({"_id":user_id}, {"$set":{"settings.send_emails":not user["settings"]["send_emails"]}})
    return result

def deleteQuestion(question_id):
    # delete the question itself
    query = db.questions.delete_one({"_id":question_id})
    # delete any responses to the question
    query2 = db.responses.delete_many({"question_id":question_id})
    return query