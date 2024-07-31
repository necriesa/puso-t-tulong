from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, Length, ValidationError

#create the app and connect to the dbs
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///information.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users' : 'sqlite:///users.db',
    'drives' : 'sqlite:///drives.db'
}
app.config['SECRET_KEY'] = 'this_is_the_secretKey'

db = SQLAlchemy(app)

#login Manager for logins 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Table Schemas
class Information(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(30), nullable = False)
    title = db.Column(db.String(100), nullable = False)
    body = db.Column(db.String(2000), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.now)
    contact_details = db.Column(db.String(50), nullable = False)

class User(db.Model, UserMixin):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique = True)
    password = db.Column(db.String(80), nullable = False)
    email = db.Column(db.String(30), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    birthday = db.Column(db.Date, nullable=False)
    
class Drive(db.Model):
    __bind_key__ = 'drives'
    id = db.Column(db.Integer, primary_key=True)
    drive_name = db.Column(db.String(20), nullable = False)
    location = db.Column(db.String(100), nullable = False)
    drive_details = db.Column(db.String(1000))
    drive_date = db.Column(db.DateTime)

# Registration Form class
class Registration(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder" : "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder" : "Password"})
    email = StringField(validators=[InputRequired(), Length(min=5, max=20)], render_kw={"placeholder" : "email"})
    age = IntegerField(validators=[InputRequired()])
    birthday = DateField(validators=[InputRequired()], format='%Y-%m-%d', render_kw={"placeholder" : "YYYY-MM-DD"})

    submit = SubmitField("Register")

    def checkUsername(self, username):
        existing_username = User.query.filter_by(
            username = username.data
        ).first()

        if existing_username:
            raise ValidationError("The username already exists. Please choose another.")
        
# Login Form class
class Login(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder" : "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder" : "Password"})

    submit = SubmitField("Login")

#Create Post Class
class UserPost(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder" : "Post title"})
    body = StringField(validators=[InputRequired(), Length(min=5, max = 2000)], render_kw={"placeholder" : "Details..."})
    contact_details = StringField(validators=[InputRequired(), Length(max=50)], render_kw={"placeholder" : "contact details"})

    submit = SubmitField("UserPost")
#Routes 

#home page
@app.route('/')
def index():
    return render_template(index.html)

#login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    loginForm = Login()
    
    if loginForm.validate_on_submit():
        user = User.query.filter_by(username=loginForm.username.data).first()
        if user and bcrypt.check_password_hash(user.password, loginForm.password.data):
            login_user(user)
            return redirect('/main')

    return render_template('login.html', form=loginForm)

#logout function
@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect('/login')

#register page
@app.route('/register', methods=['POST', 'GET'])
def register():
    registerForm = Registration()

    if registerForm.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(registerForm.password.data)
        new_user = User(
            username = registerForm.username.data,
            password = hashed_pass,
            email = registerForm.email.data,
            age = registerForm.age.data, 
            birthday = registerForm.birthday.data
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html', form=registerForm)

#after logging in
@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/goPost')
def goPost():
    if current_user.is_authenticated:
        return redirect("{{ url_for('createPost') }}")
    else:
        return redirect("{{ url_for('login') }}")
    
@app.route('/createPost', methods = ['POST', 'GET'])
@login_required
def createPost():
    PostForm = UserPost()

    if PostForm.validate_on_submit():
        new_post = Information(
            user = current_user.username,
            title = PostForm.title.data,
            body = PostForm.body.data,
            contact_details = PostForm.contact_details.data
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect("{{ url_for('main') }}")

@app.route('/drives')
def drives():
    drives_info = Drive.query.all()
    return render_template('drives', info = drives_info)

if __name__ == "__main__":
    app.run(debug=True) #remember to set to False when publishing i think