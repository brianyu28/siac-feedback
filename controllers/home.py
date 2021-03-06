from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain
from bson import ObjectId
import siac
import mailer
import threading
import bson

home = Blueprint('home', __name__,
                        template_folder='../templates/home')

@home.before_request
def check_for_login():
    if request.endpoint != "home.activate":
        if 'id' in session:
            return redirect(url_for('portal.portal_page'))

@home.route('/')
def homepage():
        return render_template('homepage.html', user=dbmain.currentUser())

@home.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', user=dbmain.currentUser())
    elif request.method == 'POST':
        authenticated = dbmain.authenticate(request.form['username'], request.form['password'])
        if authenticated:
            user_id = str(dbmain.userByUsername(request.form['username'])['_id'])
            session['id'] = user_id
            return redirect(url_for('home.homepage'))
        else:
            return render_template('login.html', user=dbmain.currentUser(), error='Your login credentials were incorrect.')

@home.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', user=dbmain.currentUser())
    if request.method == 'POST':
        # submitted register form, so register the user
        req_fields = ['first', 'last', 'email', 'username', 'password', 'password_confirm', 'acct_type', 'school']
        for field in req_fields:
            if request.form[field] == '':
                return render_template('register.html', error='All fields must be complete in order to register.')
        if not helpers.valid_email(request.form['email']):
            return render_template('register.html', error='You did not provide a valid Pleasanton Unified School District email.')
        if request.form['password'] != request.form['password_confirm']:
            return render_template('register.html', error='Your passwords did not match.')
        if (request.form['acct_type'] == "None"):
            return render_template('register.html', error='You must select an account type.')
        if (request.form['school'] == "None"):
            return render_template('register.html', error='You must select a school.')
        # need to add username checking to see if username already exists
        if (not dbmain.usernameAvailable(request.form['username'])):
            return render_template('register.html', error='Your requested username is already taken.')
        if (dbmain.userWithEmailExists(request.form['email'])):
            return render_template('register.html', error='An account with this email address already exists.')
        user_id = dbmain.addUser(request.form['username'], helpers.get_hashed_password(request.form['password']), request.form['first'], request.form['last'], request.form['email'], request.form['acct_type'], request.form['school'])
        t = threading.Thread(target=send_verification_email, args=[request.form['first'], request.form['email'], str(user_id)])
        t.setDaemon(False)
        t.start()
            
        session['id'] = str(user_id)
        return redirect(url_for('home.homepage'))

@home.route('/activate/<code>/')
def activate(code):
    if not bson.objectid.ObjectId.is_valid(code):
        return render_template('activation.html', user=dbmain.currentUser(), success=False)
    elif not dbmain.validUserID(ObjectId(code)):
        return render_template('activation.html', user=dbmain.currentUser(), success=False)
    else:
        dbmain.activateUser(ObjectId(code))
        return render_template('activation.html', user=dbmain.currentUser(), success=True)

@home.route('/about/')
def about():
    return render_template('about.html', user=dbmain.currentUser())

@home.route('/contact/')
def contact():
    return render_template('contact.html', user=dbmain.currentUser())

def send_verification_email(first_name, email_address, user_id):
    verify_body = "Dear " + first_name + ",<br /><br />"
    verify_body += "Welcome to SIAC Feedback! In order to complete your registration, please click on the following link:<br /><br />"
    verify_body += '<a href="http://siacfeedback.org/activate/' + user_id + '">http://siacfeedback.org/activate/' + user_id + '</a>'
    verify_body += '<br /><br />'
    verify_body += '-The SIAC Feedback Team'
    mailer.send([email_address], "SIAC Account Verification", verify_body)