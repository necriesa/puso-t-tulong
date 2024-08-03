from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, Length, ValidationError

#create the app and connect to the dbs
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///information.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users' : 'sqlite:///users.db',
    'drives' : 'sqlite:///drives.db',
    'comments' : 'sqlite:///comments.db'
}
app.config['SECRET_KEY'] = 'this_is_the_secretKey'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#login Manager for logins 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#TODO: create the databases within the app using the python shell
#TODO ``` from app import app, db
#TODO     with app.app_context:
#TODO          db.create_all()
#TODO ```
#Tables
class Information(db.Model):
    __tablename__ = "information"
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

    

class Comment(db.Model):
    __bind_key__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    post_id = db.Column(db.Integer, db.ForeignKey(Information.id), nullable = False)
    user = db.Column(db.String(30), nullable = False)
    body = db.Column(db.String(2000), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.now)

    post = db.relationship('Information', back_populates='comments')
Information.comments = db.relationship('Comment', order_by=Comment.date_created, back_populates='post')

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

class PostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min=1, max=100)], render_kw={"placeholder": "Post Title"})
    body = StringField('Body', validators=[InputRequired(), Length(min=1, max=2000)], render_kw={"placeholder": "Post Body"})
    contact_details = StringField('Contact Details', validators=[InputRequired(), Length(min=1, max=50)], render_kw={"placeholder": "Contact Details"})
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    body = StringField('Comment', validators=[InputRequired(), Length(min=1, max=1000)], render_kw={"placeholder": "Add a comment..."})
    submit = SubmitField('Comment')


    submit = SubmitField("Post Comment")
#Routes 

#home page
@app.route('/')
def index():
    return render_template('index.html', current_user=current_user)

#login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    loginForm = Login()
    
    if loginForm.validate_on_submit():
        user = User.query.filter_by(username=loginForm.username.data).first()
        if user and bcrypt.check_password_hash(user.password, loginForm.password.data):
            login_user(user)
            return redirect('/main')

    return render_template('auth.html', form=loginForm, form_type='login')

#logout function
@app.route('/logout', methods=['POST', 'GET'])
@login_required #login is required for this
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

        return redirect('/')

    return render_template('auth.html', form=registerForm, form_type='register')

@app.route('/forum')
def forum():
    posts = Information.query.order_by(Information.date_created.desc()).all()
    return render_template('forum.html', posts=posts)



@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Information(
            user=current_user.username,
            title=form.title.data,
            body=form.body.data,
            contact_details=form.contact_details.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect('/forum')
    return render_template('add_post.html', form=form)


@app.route('/forum/view/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = Information.query.get_or_404(post_id)
    comment_form = CommentForm()
    
    if comment_form.validate_on_submit():
        new_comment = Comment(
            post_id=post.id,
            user=current_user.username,
            body=comment_form.body.data
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(f'/forum/view/{post_id}')
    
    return render_template('view_post.html', post=post, form=comment_form)



#after logging in
@app.route('/main')
def main():
   postInfo = Information.query.order_by(Information.date_created).all()
   return render_template('forum.html', posts = postInfo)

if __name__ == "__main__":
    app.run(debug=True) #remember to set to False when publishing i think