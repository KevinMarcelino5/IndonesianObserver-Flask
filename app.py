from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



app = Flask(__name__)
       
# add data base
# old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# MYSQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/our_users'
    
# secret key
app.config['SECRET_KEY'] = "Indonesia raya merdeka merdeka, tanahku negeriku yang kucinta"
# initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_food = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
        
    # create string
    def __repr__(self):
        return '<Name %r>' % self.name
    
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User deleted successfully')
        
        our_users = Users.query.order_by(Users.date_added)
    
        return render_template('add_user.html',
                            form=form,
                            name=name,
                            our_users=our_users)
        
    except:
        flash('There was a problem deleting user')
        return render_template('add_user.html',
                            form=form,
                            name=name,
                            our_users=our_users)
    
# create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_food = StringField("Favorite Food")
    submit = SubmitField("Submit")

# update database record
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_food = request.form['favorite_food']
        try:
            db.session.commit()
            flash('User updated successfully')
            return render_template('update.html',
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash('Error! looks like there a problem, try again (#except)')
            return render_template('update.html',
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template('update.html',
                                form=form,
                                name_to_update=name_to_update,
                                id=id)
    
# create a form class
class NamerForm(FlaskForm):
    name = StringField("Whats your name ?", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    
@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user =  Users(name=form.name.data, email=form.email.data, favorite_food=form.favorite_food.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_food.data = ''
        flash('User Added successfully')
    our_users = Users.query.order_by(Users.date_added)
    
    return render_template('add_user.html',
                           form=form,
                           name=name,
                           our_users=our_users)


# route decorateor
@app.route('/')
def index():
    first_name = "kevin"
    stuff = "This is <strong>Bold</strong> text"
    favorite_martabak = ['Coklat','Kacang','Keju','Susu',47]
    return render_template('index.html',
                           first_name=first_name,
                           stuff=stuff,
                           favorite_martabak=favorite_martabak)

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name=name)

# custom error page

# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Internal Server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('404.html'), 500

# name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # validator form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("FOrm submitted successfully")
        
    return render_template('name.html',
                           name = name,
                           form = form)