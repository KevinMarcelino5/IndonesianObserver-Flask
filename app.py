from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from webforms import *



app = Flask(__name__)

# add ck editor
ckeditor = CKEditor(app)
       
# add data base
# old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# MYSQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/our_users'
    
# secret key
app.config['SECRET_KEY'] = "Indonesia raya merdeka merdeka, tanahku negeriku yang kucinta"

UPLOAD_FOLDER = 'static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# flask login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# pass stuff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# admin page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    
    if id == 27:
        return render_template('admin.html')
    else:
        flash('Maaf, anda harus menjadi admin untuk mengakses halaman ini')
        return redirect( url_for('dashboard'))
        
    

# create search function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    journals = Journals.query
    
    if form.validate_on_submit():
        # get data from submit form
        journal.searched = form.searched.data
        # query the database
        journals = journals.filter(Journals.content.like('%' + journal.searched + '%'))
        journals = journals.order_by(Journals.date_posted).all()
        return render_template('search.html',
                               form=form,
                               searched=journal.searched,
                               journals=journals)

# create login page
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login successfully')
                return redirect( url_for('dashboard') )
            else:
                flash('Wrong password - try again')
        else:
            flash('that user doesnt exist, try again')
    return render_template('login.html', form=form)

# Create logout
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('you have been logged out! Terima kasih sudah mampir')
    return redirect(url_for('login'))

# create dashboard page
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

    
# Delete Journal
@app.route('/journals/delete/<int:id>')
@login_required
def delete_journal(id):
    journal_to_delete = Journals.query.get_or_404(id)
    id = current_user.id
    
    if id == journal_to_delete.penulis.id:
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
    else:
        flash('Anda tidak berwenang untuk menghapus journal ini')
        journals = Journals.query.order_by(Journals.id)
        return render_template('journals.html', journals=journals)

# create journal page
@app.route('/add_journal', methods=['GET','POST'])
@login_required
def add_journal():
    form = JournalForm()
    
    if form.validate_on_submit():
        penulis = current_user.id
        journal = Journals(title=form.title.data, 
                     content=form.content.data,
                     penulis_id=penulis,
                     slug=form.slug.data)
        # Clear form
        form.title.data = ''
        form.content.data = ''
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
@login_required
def edit_journal(id):
    journal = Journals.query.get_or_404(id)
    form = JournalForm()
    
    if form.validate_on_submit():
        journal.title = form.title.data
        # journal.author = form.author.data
        journal.slug = form.slug.data
        journal.content = form.content.data
        # update database
        db.session.add(journal)
        db.session.commit()
        flash('Journal has been edited')
        return redirect( url_for('journal', id=journal.id) )
    
    if current_user.id == journal.penulis_id:
        form.title.data = journal.title
        # form.author.data = journal.author
        form.slug.data = journal.slug
        form.content.data = journal.content
        return render_template('edit_journal.html', form=form)
    else:
        flash('Anda tidak berwenang untuk menyunting halaman ini')
        journals = Journals.query.order_by(Journals.date_posted)
        return render_template('journals.html', journals=journals)
    
    
# Jdon thing
@app.route('/date')
def get_current_date():
    Pekerjaan = {
        "Kevin" : "programmer",
        "Efan" : "Karyawan",
        "Philip":"Koki"
    }
    
    return Pekerjaan

    
@app.route('/delete/<int:id>')
@login_required
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
   

# update database record
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.organization = request.form['organization']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']
        # grap image name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        # set uuif
        pic_name = str(uuid.uuid1()) + '_' + pic_filename
        # save that image
        saver = request.files['profile_pic']
        # change to a string to save to db
        name_to_update.profile_pic = pic_name
        try:
            saver.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_name)
            db.session.commit()
            flash('User updated successfully')
            return render_template('dashboard.html',
                                   judul='Dashboard',
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash('Error! looks like there a problem, try again (#except)')
            return render_template('dashboard.html',
                                   judul='Dashboard',
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template('update.html',
                                judul='Update User',
                                form=form,
                                name_to_update=name_to_update,
                                id=id)
    
    
@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        username = Users.query.filter_by(username=form.username.data).first()
        if (user or username) is None:
            # hash password
            hashed_pw= generate_password_hash(form.password_hash.data, 'sha256')
            user =  Users(name=form.name.data,
                          username=form.username.data,
                          email=form.email.data,
                          organization=form.organization.data,
                          about_author=form.about_author.data,
                          password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        
        else:
            flash('tambah user gagal, ada email atau username yang sama')
            return redirect( url_for('users') )
        
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.organization.data = ''
        form.about_author.data = ''
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
    
# Create a Journal model
class Journals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # foreign key to link users , refer to primary key from users
    penulis_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    

# create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    organization = db.Column(db.String(200))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(200), nullable=True)
    
    # Password stuff
    password_hash = db.Column(db.String(128))
    
    # user can have many journals
    journals = db.relationship('Journals', backref='penulis')
    
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
