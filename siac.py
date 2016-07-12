from flask import Flask
from controllers.home import home
from controllers.portal import portal
import secrets
app = Flask(__name__)
app.secret_key = secrets.secret_key

app.register_blueprint(home)
app.register_blueprint(portal, url_prefix='/portal')

if __name__ == "__main__":
    app.run()