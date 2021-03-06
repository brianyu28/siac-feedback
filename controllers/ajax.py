from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from model import helpers, dbmain
from bson import ObjectId
import bson
import time
import secrets
import mailer

ajax = Blueprint('ajax', __name__,
                        template_folder='../templates/portal')

@ajax.route('/teacher_info/', methods=['POST'])
def teacher_info():
    teacher_id = ObjectId(request.form['teacher_id'])
    teacher = dbmain.userById(teacher_id)
    return jsonify(first=teacher["first"], last=teacher["last"])
    
@ajax.route('/submit_general_feedback/', methods=['POST'])
def submit_general_feedback():
    teacher_id = ObjectId(request.form['teacher_id'])
    author_id = ObjectId(request.form['author_id'])
    feedback = request.form['feedback']
    filterlist = secrets.filterlist
    for item in filterlist:
        if item in feedback.lower():
            return jsonify(result="Failure")
    dbmain.addGeneralFeedback(author_id, teacher_id, int(time.time()), feedback)
    return jsonify(result="Success")

@ajax.route('/approve_general_feedback/', methods=['POST'])
def approve_general_feedback():
    feedback_id = ObjectId(request.form['feedback_id'])
    dbmain.approveGeneralFeedback(feedback_id)
    return jsonify(result="Success")

@ajax.route('/reject_general_feedback/', methods=['POST'])
def reject_general_feedback():
    feedback_id = ObjectId(request.form['feedback_id'])
    dbmain.deleteGeneralFeedback(feedback_id)
    return jsonify(result="Success")

@ajax.route('/toggle_filter/', methods=['POST'])
def toggle_filter():
    teacher_id = ObjectId(request.form['teacher_id'])
    dbmain.toggleFilter(teacher_id)
    return jsonify(result="Success")

@ajax.route('/add_course/', methods=['POST'])
def add_course():
    name = request.form['name']
    password = request.form['password']
    dbmain.addCourse(ObjectId(session['id']), name, password)
    return jsonify(result="Success")

@ajax.route('/add_question/', methods=['POST'])
def add_question():
    name = request.form['name']
    course_id = ObjectId(request.form['course'])
    dbmain.addQuestion(course_id, "Text", int(time.time()), name)
    course = dbmain.courseById(course_id)
    teacher = dbmain.userById(course["teacher_id"])
    users = dbmain.mailtoStudentsInCourse(course_id)
    send_new_question_email(users, course, teacher, name)
    return jsonify(result="Success")

@ajax.route('/delete_question/', methods=['POST'])
def delete_question():
    question_id = ObjectId(request.form['question_id'])
    dbmain.deleteQuestion(question_id)
    return jsonify(success=True)

@ajax.route('/toggle_question_open/', methods=['POST'])
def toggle_question_open():
    question_id = ObjectId(request.form['question_id'])
    open_status = request.form['open_status'] == "true"
    dbmain.toggleQuestionOpen(question_id, open_status)
    return jsonify(result="Success")

@ajax.route('/delete_response/', methods=['POST'])
def delete_response():
    response_id = ObjectId(request.form['response_id'])
    dbmain.deleteResponse(response_id)
    return jsonify(result="Success")

@ajax.route('/join_course/', methods=['POST'])
def join_course():
    course_id = request.form['course_id']
    if (course_id == ""):
        return jsonify(result="None Selected")
    course_id = ObjectId(course_id)
    course = dbmain.courseById(course_id)
    if (course['password'] != request.form['course_password']):
        return jsonify(result="Authentication Failed")
    dbmain.addRegistration(ObjectId(session['id']), course_id)
    return jsonify(result="Success")

@ajax.route('/question_details/', methods=['POST'])
def question_details():
    question_id = ObjectId(request.form['question_id'])
    question = dbmain.questionById(question_id)
    question['_id'] = str(question['_id'])
    question['course_id'] = str(question['course_id'])
    return jsonify(question=question)

@ajax.route('/submit_response/', methods=['POST'])
def submit_response():
    question_id = ObjectId(request.form['question_id'])
    author_id = ObjectId(request.form['author_id'])
    feedback = request.form['feedback']
    filterlist = secrets.filterlist
    for item in filterlist:
        if item in feedback.lower():
            return jsonify(result="Failure")
    dbmain.addResponse(author_id, question_id, int(time.time()), feedback)
    return jsonify(result="Success")

@ajax.route('/change_password/', methods=['POST'])
def change_password():
    user = dbmain.currentUser()
    old_pass = request.form['old_pass']
    new_pass = request.form['new_pass']
    confirm_pass = request.form['confirm_pass']
    if not helpers.check_password(old_pass, user['password']):
        return jsonify(success=False, credentials=False)
    if new_pass != confirm_pass:
        return jsonify(success=False, credentials=True)
    dbmain.changeUserAttribute(user['_id'], "password", helpers.get_hashed_password(new_pass))
    return jsonify(success=True)

@ajax.route('/send_general_reply/', methods=['POST'])
def send_general_reply():
    user = dbmain.currentUser()
    user_id = user['_id']
    feedback_id = ObjectId(request.form['feedback_id'])
    author_id = dbmain.authorOfGeneralFeedback(feedback_id)
    reply = request.form['contents']
    dbmain.addReply(user_id, author_id, feedback_id, int(time.time()), reply)
    return jsonify(success=True)
    
# used for a teacher to send a reply to a student's response to a teacher's question
@ajax.route('/send_question_reply/', methods=['POST'])
def send_question_reply():
    user = dbmain.currentUser()
    user_id = user['_id']
    feedback_id = ObjectId(request.form['feedback_id'])
    author_id = dbmain.authorOfResponse(feedback_id)
    reply = request.form['contents']
    dbmain.addReply(user_id, author_id, feedback_id, int(time.time()), reply)
    return jsonify(success=True)


@ajax.route('/delete_reply/', methods=['POST'])
def delete_reply():
    reply_id = ObjectId(request.form['reply_id']) 
    dbmain.deleteReply(reply_id)
    return jsonify(success=True)

@ajax.route('/toggle_emails/', methods=['POST'])
def toggle_emails():
    user_id = ObjectId(request.form['user_id'])
    dbmain.toggleEmails(user_id)
    return jsonify(success=True)

@ajax.route('/contact_us/', methods=['POST'])
def contact_us():
    name = request.form['name']
    email = request.form['email']
    feedback = request.form['feedback']
    submit_contact_us(name, email, feedback)
    return jsonify(success=True)

def send_new_question_email(users, course, teacher, question):
    for user in users:
        msg_body = "Dear " + user["first"] + ",<br/><br/>"
        msg_body += "A new question was posted on SIAC Feedback by <b>" + teacher["first"] + " " + teacher["last"] + "</b> in the course: <b>" + course['name'] + "</b>. "
        msg_body += "<br/><br/>"
        msg_body += "Question: <b>" + question + "</b>"
        msg_body += "<br/><br/>"
        msg_body += 'Log in to SIAC Feedback <a href="http://siacfeedback.org/">here</a> to view the question.'
        mailer.send([user['email']], "New Question on SIAC Feedback", msg_body)

def submit_contact_us(name, email, feedback):
    msg_body = "New Message via SIAC Feedback:<br/><br/>"
    msg_body += "<b>Name:</b> " + name + "<br/><br/>"
    msg_body += "<b>Email: </b>" + email + "<br/><br/>"
    msg_body += feedback
    mailer.send(['brianyu28@gmail.com'], "New SIAC Feedback Message", msg_body)