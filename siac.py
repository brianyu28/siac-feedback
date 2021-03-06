from flask import Flask, session
from flask_mail import Mail, Message
from datetime import timedelta
from controllers.home import home
from controllers.portal import portal
from controllers.ajax import ajax
import secrets
app = Flask(__name__)
app.secret_key = secrets.secret_key
app.config.update(
    DEBUG = True,
    MAIL_SERVER = 'mail.siacfeedback.org',
    MAIL_USERNAME = secrets.mailusername,
    MAIL_PASSWORD = secrets.mailpassword
)
app.config.from_object(__name__)

mail = Mail(app)

@app.before_request
def session_checker():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=4)
    session.modified = True

app.register_blueprint(home)
app.register_blueprint(portal, url_prefix='/portal')
app.register_blueprint(ajax, url_prefix='/ajax')


    
if __name__ == "__main__":
    app.run()

def sendmail(subject, recipient, body):
    msg = Message(subject,
                  sender="no-reply@siacfeedback.com",
                  recipients=[recipient])
    msg.html = body
    mail.send(msg)