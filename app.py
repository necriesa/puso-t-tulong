from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///information.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users' : 'sqlite:///users.db',
    'drives' : 'sqlite:///drives.db'
}

db = SQLAlchemy(app)

#TODO: create the databases within the app using the python shell 
#TODO ``` from app import app, db 
#TODO     with app.app_context:
#TODO          db.create_all()
#TODO ```
class Information(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(30), nullable = False)
    title = db.Column(db.String(100), nullable = False)
    body = db.Column(db.String(2000), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.now)
    contact_details = db.Column(db.String(50), nullable = False)

class User(db.Model):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer)
    birthday = db.Column(db.DateTime)
    email = db.Column(db.String(30), nullable = False)

class Drive(db.Model):
    __bind_key__ = 'drives'
    id = db.Column(db.Integer, primary_key=True)
    drive_name = db.Column(db.String(20), nullable = False)
    location = db.Column(db.String(100), nullable = False)
    drive_details = db.Column(db.String(1000))
    drive_date = db.Column(db.DateTime)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True) #remember to set to False when publishing i think