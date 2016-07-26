from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain
from bson import ObjectId
import bson

portal = Blueprint('portal', __name__,
                        template_folder='../templates/portal')

@portal.before_request
def verify_activation():
    if request.endpoint != "portal.logout":
        if 'id' not in session:
            return render_template('homepage.html', user=dbmain.currentUser())
        elif not dbmain.currentUserActive():
            return render_template('inactive.html', user=dbmain.currentUser())
    
@portal.route('/')
def portal_page():
    return render_template('portal.html', user=dbmain.currentUser())

@portal.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('home.homepage'))

@portal.route('/students/general/')
def student_general():
    user = dbmain.currentUser()
    if user["acct_type"] != "Student":
        return redirect(url_for('home.homepage'))
    teachers = dbmain.teachersInSchool(user["school"])
    return render_template('student_general.html', user=user, teachers=teachers)

@portal.route('/teachers/general/')
def teacher_general():
    user = dbmain.currentUser()
    if user["acct_type"] != "Teacher":
        return redirect(url_for('home.homepage'))
    feedback = dbmain.generalFeedbackForTeacher(user["_id"])
    return render_template('teacher_general.html', user=user, feedback=feedback)
    

@portal.route('/siac/pending/')
def pending():
    user = dbmain.currentUser()
    if user["acct_type"] != "SIAC":
        return redirect(url_for('home.hompeage'))
    pending = dbmain.pendingFeedback()
    return render_template('pending_feedback.html', user=user, pending=pending)