from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain
from bson import ObjectId
import bson
import mailer

portal = Blueprint('portal', __name__,
                        template_folder='../templates/portal')

@portal.before_request
def verify_activation():
    if request.endpoint != "portal.logout":
        if 'id' not in session:
            return render_template('homepage.html', user=dbmain.currentUser())
        elif not dbmain.currentUserActive():
            return render_template('inactive.html', user=dbmain.currentUser())

@portal.route('/siac/')
@portal.route('/students/')
@portal.route('/teachers/')
@portal.route('/')
def portal_page():
    user = dbmain.currentUser()
    siac_filter = user["siac_filter"]
    return render_template('portal.html', user=user, siac_filter=siac_filter)

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
    raw_feedback = dbmain.generalFeedbackForTeacher(user["_id"])
    feedback = []
    for item in raw_feedback:
        feedback['responded_yet'] = "Yes" if dbmain.replyExists(user['_id'], item['_id']) else "No"
        feedback.append(item)
    return render_template('teacher_general.html', user=user, feedback=feedback)

@portal.route('/siac/pending/')
def pending():
    user = dbmain.currentUser()
    if user["acct_type"] != "SIAC":
        return redirect(url_for('home.hompeage'))
    pending = dbmain.pendingFeedback()
    return render_template('pending_feedback.html', user=user, pending=pending)

@portal.route('/teachers/classes/')
def teacher_courses():
    user = dbmain.currentUser()
    if user["acct_type"] != "Teacher":
        return redirect(url_for('home.homepage'))
    courses = dbmain.coursesForTeacher(user["_id"])
    return render_template('teacher_classes.html', user=user, courses=courses)

# for a specific course
@portal.route('/teachers/classes/<string:course_id>')
def teacher_course(course_id):
    user = dbmain.currentUser()
    # check to see if class actually exists and belongs to teacher
    course = dbmain.courseIfExists(ObjectId(course_id))
    if course == None or course["teacher_id"] != user["_id"]:
        return redirect('portal.teacher_courses')
    # get the questions
    course['count'] = dbmain.numStudentsInCourse(course['_id'])
    questions = dbmain.questionsForCourse(course["_id"])
    return render_template('teacher_class.html', user=user, course=course, questions=questions)

@portal.route('/teacher/questions/<string:question_id>')
def question_responses(question_id):
    user = dbmain.currentUser()
    question = dbmain.questionIfExists(ObjectId(question_id))
    course = dbmain.courseIfExists(question["course_id"])
    raw_responses = dbmain.responsesForQuestion(question["_id"])
    responses = []
    for item in raw_responses:
        item['responded_yet'] = "Yes" if dbmain.replyExists(user['_id'], item['_id']) else "No"
        responses.append(item)
    return render_template('question_responses.html', user=user, question=question, course=course, responses=responses)

@portal.route('/students/classes/')
def student_courses():
    user = dbmain.currentUser()
    courses = dbmain.coursesForStudent(user['_id'])
    unregistered = dbmain.unregisteredCoursesForStudent(user['_id'])
    return render_template('student_classes.html', user=user, courses=courses, unregistered=unregistered)

@portal.route('/students/classes/<string:course_id>')
def student_course(course_id):
    user = dbmain.currentUser()
    course = dbmain.courseIfExists(ObjectId(course_id))
    course['teacher'] = dbmain.userById(course['teacher_id'])
    if course == None or not dbmain.studentIsRegisteredForCourse(user['_id'], ObjectId(course_id)):
        return redirect('portal.student_courses')
    old_questions = dbmain.openQuestionsForCourse(course['_id'])
    questions = []
    for question in old_questions:
        question["responded_yet"] = "Yes" if dbmain.responseExists(user['_id'], question['_id']) else "No"
        questions.append(question)
    return render_template('student_class.html', user=user, course=course, questions=questions)

@portal.route('/settings/')
def settings():
    user = dbmain.currentUser()
    return render_template('settings.html', user=user)

# views teacher messages to student (not anonymized)
@portal.route('/students/responses/')
def student_responses():
    user = dbmain.currentUser()
    replies = dbmain.repliesForStudent(user['_id'])
    return render_template('student_responses.html', user=user, replies=replies)

@portal.route('/contact/')
def contact():
    return render_template('contact.html', user=dbmain.currentUser())