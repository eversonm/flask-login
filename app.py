from flask import Flask
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from mysqldb1 import mysql
# init SQLAlchemy so we can use it later in our models

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % mysql
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

auth = Blueprint('auth', __name__)
app.register_blueprint(auth)

@app.before_first_request
def create_tables():
    db.create_all()

class User(UserMixin,db.Model):
    # ...
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(128))
    password = db.Column(db.String(128))


@app.route('/login', methods=['POST', 'GET'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return render_template('login.html')

    if email and password:
        login_user(user, remember=remember)
        return render_template('profile.html')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if email and user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return render_template('signup.html')

    new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    #return redirect(url_for('.index'))
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug =True)