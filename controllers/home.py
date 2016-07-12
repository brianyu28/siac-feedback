from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain
from bson import ObjectId
import bson

home = Blueprint('home', __name__,
                        template_folder='../templates/home')

@home.route('/')
def homepage():
    if 'id' not in session:
        return render_template('homepage.html')
    elif not dbmain.currentUserActive():
        return render_template('inactive.html')
    return redirect(url_for('portal.portal_page'))
        

@home.route('/login/')
def login():
    return render_template('login.html')

@home.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
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
        user_id = dbmain.addUser(request.form['username'], helpers.get_hashed_password(request.form['password']), request.form['first'], request.form['last'], request.form['email'], request.form['acct_type'], request.form['school'])
        session['id'] = str(user_id)
        return redirect(url_for('home.homepage'))

@home.route('/activate/<code>/')
def activate(code):
    if not bson.objectid.ObjectId.is_valid(code):
        return render_template('activation.html', success=False)
    elif not dbmain.validUserID(ObjectId(code)):
        return render_template('activation.html', success=False)
    else:
        dbmain.activateUser(ObjectId(code))
        return render_template('activation.html', success=True)

@home.route('/about/')
def about():
    return render_template('about.html')

@home.route('/contact/')
def contact():
    return render_template('contact.html')
