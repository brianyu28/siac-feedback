from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from model import helpers, dbmain
from bson import ObjectId
import bson
import time

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