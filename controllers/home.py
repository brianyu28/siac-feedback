from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain

home = Blueprint('home', __name__,
                        template_folder='../templates/home')

@home.route('/')
def homepage():
    return render_template('homepage.html')