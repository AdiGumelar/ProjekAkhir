from flask import Flask, jsonify, render_template, redirect, url_for, request, session
import hashlib

from pymongo import MongoClient

MONGODB_CONNECTION_STRING = "mongodb+srv://test:sparta@cluster0.w9suhru.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.Sekolah

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST" :
        email_receive = request.form["email_give"]
        pw_receive = request.form["pw_give"]

        pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

        findUser = db.user.find_one({"email": email_receive, "pw": pw_hash})
        
        if findUser:
            return jsonify({"result": "success"})
        else :
            return jsonify({"result": "error"})

    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST" :
        email_receive = request.form["email_give"]
        pw_receive = request.form["pw_give"]
        name_receive = request.form["name_give"]
        
        pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

        findEmail = db.user.find_one({"email": email_receive})

        if findEmail:
            return jsonify({"result": "error"})

        else:
            db.user.insert_one({"name" : name_receive, "email": email_receive, "pw": pw_hash})

    return render_template('register.html') 

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)