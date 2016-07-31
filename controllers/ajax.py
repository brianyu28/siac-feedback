from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from model import helpers, dbmain
from bson import ObjectId
import bson
import time
import secrets

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
    return jsonify(result="Success")

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