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
            return render_template('homepage.html')
        elif not dbmain.currentUserActive():
            return render_template('inactive.html')
    
@portal.route('/')
def portal_page():
    return render_template('portal.html')

@portal.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('home.homepage'))