from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea



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

# Create a Journal model
class Journals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    
# create journals form
class JournalForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
# Delete Journal
@app.route('/journals/delete/<int:id>')
def delete_journal(id):
    journal_to_delete = Journals.query.get_or_404(id)
    
    try:
        db.session.delete(journal_to_delete)
        db.session.commit()
        
        flash('jurnal sudah dihapus')
        journals = Journals.query.order_by(Journals.id)
        return render_template('journals.html', journals=journals)
        
    except:
        flash('whoops, ada masalah untuk menghapus jurnal, cobalagi')
        journals = Journals.query.order_by(Journals.id)
        return render_template('journals.html', journals=journals)

# create journal page
@app.route('/add_journal', methods=['GET','POST'])
def add_journal():
    form = JournalForm()
    
    if form.validate_on_submit():
        journal = Journals(title=form.title.data, 
                     content=form.content.data,
                     author=form.author.data,
                     slug=form.slug.data)
        # Clear form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        # add to db
        db.session.add(journal)
        db.session.commit()
        
        flash("Journal submitted successfully")
        
    return render_template('add_journal.html', form=form, judul='Add Journal')

@app.route('/journals')
def journals():
    journals = Journals.query.order_by(Journals.date_posted)
    # grab all journals from db
    return render_template('journals.html', journals=journals, judul='Journals')

@app.route('/journals/<int:id>')
def journal(id):
    journal = Journals.query.get_or_404(id)
    return render_template('journal.html', journal=journal, judul='Journal')

# update journal
@app.route('/journals/edit/<int:id>', methods=['GET','POST'])
def edit_journal(id):
    journal = Journals.query.get_or_404(id)
    form = JournalForm()
    if form.validate_on_submit():
        journal.title = form.title.data
        journal.author = form.author.data
        journal.slug = form.slug.data
        journal.content = form.content.data
        # update database
        db.session.add(journal)
        db.session.commit()
        flash('Journal has been edited')
        return redirect( url_for('journal', id=journal.id) )
    form.title.data = journal.title
    form.author.data = journal.author
    form.slug.data = journal.slug
    form.content.data = journal.content
    return render_template('edit_journal.html', form=form)

# Jdon thing
@app.route('/date')
def get_current_date():
    Pekerjaan = {
        "Kevin" : "programmer",
        "Efan" : "Karyawan",
        "Philip":"Koki"
    }
    
    return Pekerjaan


# create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_food = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Password stuff
    password_hash = db.Column(db.String(128))
    
    @property
    def password(self):
        raise AttributeError('password is not readable attribute !')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
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
                            judul='Add User',
                            form=form,
                            name=name,
                            our_users=our_users)
        
    except:
        flash('There was a problem deleting user')
        return render_template('add_user.html',
                            judul='Add User',
                            form=form,
                            name=name,
                            our_users=our_users)
    
# create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_food = StringField("Favorite Food")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='password must match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
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
                                   judul='Update User',
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash('Error! looks like there a problem, try again (#except)')
            return render_template('update.html',
                                   judul='Update User',
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template('update.html',
                                judul='Update User',
                                form=form,
                                name_to_update=name_to_update,
                                id=id)
    
# create a password form
class PasswordForm(FlaskForm):
    email = StringField("Whats your email ?", validators=[DataRequired()])
    password_hash = PasswordField("Whats your password ?", validators=[DataRequired()])
    
    submit = SubmitField("Submit")
    
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
            # hash password
            hashed_pw= generate_password_hash(form.password_hash.data, 'sha256')
            user =  Users(name=form.name.data,
                          email=form.email.data,
                          favorite_food=form.favorite_food.data,
                          password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_food.data = ''
        form.password_hash.data = ''
        flash('User Added successfully')
    
    return render_template('add_user.html',
                           judul='Add User',
                           form=form,
                           name=name,)
                        
@app.route('/users')
def users():
    our_users = Users.query.order_by(Users.date_added)
    return render_template('users.html', our_users=our_users)


# route decorateor
@app.route('/')
def index():
    first_name = "kevin"
    stuff = "This is <strong>Bold</strong> text"
    favorite_martabak = ['Coklat','Kacang','Keju','Susu',47]
    return render_template('index.html',
                           judul='Home',
                           first_name=first_name,
                           stuff=stuff,
                           favorite_martabak=favorite_martabak)

# @app.route('/user/<name>')
# def user(name):
#     name='golojo'
#     return render_template("user.html", name=name, judul='user name')

# custom error page

# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', judul='404'), 404

# Internal Server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html', judul='500'), 500

# password test page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    
    # validator form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # clear form
        form.email.data = ''
        form.password_hash.data = ''
        
        # lookup user by email
        pw_to_check = Users.query.filter_by(email=email).first()
        
        # check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)
        
    return render_template('test_pw.html',
                           email = email,
                           password = password,
                           pw_to_check=pw_to_check,
                           passed = passed,
                           form = form)

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
                           judul='Name',
                           name = name,
                           form = form)