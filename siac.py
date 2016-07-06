from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "This is SIAC Feedback."

if __name__ == "__main__":
    app.run()