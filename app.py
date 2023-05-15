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
from flask_mail import Mail, Message
# from itsdangerous.jws import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import sshtunnel
from webforms import *



app = Flask(__name__)

# tunneling for pythonanywhere
# tunnel = sshtunnel.SSHTunnelForwarder(
#     ('ssh.pythonanywhere.com'), ssh_username='qbenstow47', ssh_password='Anastasya7',
#     remote_bind_address=('qbenstow47.mysql.pythonanywhere-services.com', 3306)
# )
# tunnel.start()

# add ck editor
ckeditor = CKEditor(app)
       
# add data base
# old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# MYSQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/our_users'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://qbenstow47:Anastasya7@qbenstow47.mysql.pythonanywhere-services.com/qbenstow47$default'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://qbenstow47:Anastasya7@127.0.0.1:{}/qbenstow47$default'.format(tunnel.local_bind_port)

# Gmail smtp setting
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'filousom@gmail.com'
app.config['MAIL_USERNAME'] = 'indonesianobserver0@gmail.com'
# app.config['MAIL_PASSWORD'] = 'ttjqpeyydwwfxjwp'
app.config['MAIL_PASSWORD'] = 'slllzvasokkrqkre'
mail=Mail(app)
    
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
    
    if id == 27 or current_user.admin:
        our_users = Users.query.order_by(Users.date_added)
        return render_template('admin.html', our_users=our_users)
    else:
        flash('Maaf, anda harus menjadi admin untuk mengakses halaman ini')
        return redirect( url_for('dashboard'))
    

def send_mail(user):
    token = user.get_token()
    msg = Message('Password Reset Request',recipients=[user.email], sender='filousom@gmail.com')
    msg.body = f''' To Reset your password. Please follow the link below
    {url_for('reset_token', token=token, _external=True)}
    
    If you didnt send a password reset request. Please Ignore this message
    '''
    mail.send(msg)

 
@app.route('/reset_request', methods=['GET','POST'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user:
            send_mail(user)
            flash('Reset request sent, Check Your Email','success')
            return redirect( url_for('login') )
        else:
            flash('Email tidak ditemukan !','error')
    return render_template('reset_request.html', judul='Reset Password', form=form)

@app.route('/reset_request/<token>', methods=['GET','POST'])
def reset_token(token):
    user = Users.verify_token(token)
    if user is None:
        flash('Invalid or expired token, please try again')
        return redirect(url_for('reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw= generate_password_hash(form.password_hash.data, 'sha256')
        # user.password = hashed_pw
        user.password_hash = hashed_pw
        db.session.commit()
        flash('Password changed, Please login')
        return redirect(url_for('login'))
    return render_template('change_password.html', judul='Change Password', form=form)
   
# create search function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    journals = Journals.query
    testimoni = Testimonials.query
    
    if form.validate_on_submit():
        # get data from submit form
        journal.searched = form.searched.data
        # query the database
        journals = journals.filter(Journals.content.like('%' + journal.searched + '%'))
        journals = journals.order_by(Journals.date_posted).all()
        # get data from submit form
        testimonials.searched = form.searched.data
        # query the database
        testimoni = testimoni.filter(Testimonials.content.like('%' + testimonials.searched + '%'))
        testimoni = testimoni.order_by(Testimonials.date_posted).all()
        return render_template('search.html',
                               form=form,
                               searched=journal.searched,
                               journals=journals,
                               searched_testimoni=testimonials.searched,
                               testimoni=testimoni,
                               judul='Mencari "'+form.searched.data+'"')

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
    return render_template('login.html', form=form, judul='Login')

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
    return render_template('dashboard.html', judul='Dashboard')
 
     
# update edukasi
@app.route('/edukasi/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_edukasi(id):
    edukasi = Edukasi.query.get_or_404(id)
    form = EdukasiForm()
    
    if form.validate_on_submit():
        edukasi.title = form.title.data
        edukasi.subtitle = form.subtitle.data
        edukasi.content = form.content.data
        # update database
        db.session.add(edukasi)
        db.session.commit()
        flash('Layanan has been edited')
        return redirect( url_for('edukasi', id=edukasi.id) )
    
    if current_user.admin:
        form.title.data = edukasi.title
        form.subtitle.data = edukasi.subtitle
        form.content.data = edukasi.content
        return render_template('edit_edukasi.html', form=form)
    else:
        flash('Anda tidak berwenang untuk menyunting halaman ini')
        return redirect(url_for('edukasi'))
  
# Delete Layanan
@app.route('/edukasi/delete/<int:id>')
@login_required
def delete_edukasi(id):
    edukasi_to_delete = Edukasi.query.get_or_404(id)
    
    if current_user.admin:
        try:
            db.session.delete(edukasi_to_delete)
            db.session.commit()
            
            flash('Edukasi sudah dihapus')
            return redirect( url_for('edukasi'))
            
        except:
            flash('whoops, ada masalah untuk menghapus edukasi, cobalagi')
            return redirect( url_for('edukasi'))
    else:
        flash('Anda tidak berwenang untuk menghapus journal ini')
        return redirect( url_for('edukasi'))

# lihat edukasi
@app.route('/edukasi/<int:id>')
def poinEdukasi(id):
    edukasi = Edukasi.query.get_or_404(id)
    return render_template('poinEdukasi.html', edukasi=edukasi, judul=edukasi.title)
 
# Show edukasi
@app.route('/edukasi', methods=['GET','POST'])
def edukasi():
    edukasi = Edukasi.query.order_by(Edukasi.id.desc())
    return render_template('edukasi.html', edukasi=edukasi, judul='Edukasi')

# create add edukasi page
@app.route('/add_edukasi', methods=['GET','POST'])
@login_required
def add_edukasi():
    form = EdukasiForm()
    
    if form.validate_on_submit():
        edukasi = Edukasi(title=form.title.data, subtitle=form.subtitle.data, content=form.content.data)
        # Clear form
        form.title.data = ''
        form.subtitle.data = ''
        form.content.data = ''
        # add to db
        db.session.add(edukasi)
        db.session.commit()
        
        flash("Layanan submitted successfully")
        return redirect( url_for('index'))
        
    return render_template('add_Edukasi.html', form=form, judul='Tambah Edukasi')

    
    
# update layanan
@app.route('/layanan/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_layanan(id):
    layanan = LayananKami.query.get_or_404(id)
    form = LayananForm()
    
    if form.validate_on_submit():
        layanan.title = form.title.data
        layanan.subtitle = form.subtitle.data
        layanan.content = form.content.data
        # update database
        db.session.add(layanan)
        db.session.commit()
        flash('Layanan has been edited')
        return redirect( url_for('layanan', id=layanan.id) )
    
    if current_user.admin:
        form.title.data = layanan.title
        form.subtitle.data = layanan.subtitle
        form.content.data = layanan.content
        return render_template('edit_layanan.html', form=form)
    else:
        flash('Anda tidak berwenang untuk menyunting halaman ini')
        return redirect(url_for('layananKami'))
  
# Delete Layanan
@app.route('/layanan/delete/<int:id>')
@login_required
def delete_layanan(id):
    layanan_to_delete = LayananKami.query.get_or_404(id)
    
    if current_user.admin:
        try:
            db.session.delete(layanan_to_delete)
            db.session.commit()
            
            flash('layanan sudah dihapus')
            return redirect( url_for('layanan'))
            
        except:
            flash('whoops, ada masalah untuk menghapus layanan, cobalagi')
            return redirect( url_for('layanan'))
    else:
        flash('Anda tidak berwenang untuk menghapus journal ini')
        return redirect( url_for('layanan'))

# lihat layanan
@app.route('/layanan/<int:id>')
def layanan(id):
    layanan = LayananKami.query.get_or_404(id)
    return render_template('layanan.html', layanan=layanan, judul=layanan.title)
 
# Show Layanan
@app.route('/layanan', methods=['GET','POST'])
def layananKami():
    layanan = LayananKami.query.order_by(LayananKami.id.desc())
    return render_template('layananKami.html', layanan=layanan, judul='Layanan Kami')

# create add layanan page
@app.route('/add_layanan', methods=['GET','POST'])
@login_required
def add_layanan():
    form = LayananForm()
    
    if form.validate_on_submit():
        layanan = LayananKami(title=form.title.data, subtitle=form.subtitle.data, content=form.content.data)
        # Clear form
        form.title.data = ''
        form.subtitle.data = ''
        form.content.data = ''
        # add to db
        db.session.add(layanan)
        db.session.commit()
        
        flash("Layanan submitted successfully")
        return redirect( url_for('layananKami'))
        
    return render_template('add_layanan.html', form=form, judul='Tambah Layanan')


# Delete Testimonial
@app.route('/testimonials/delete/<int:id>')
@login_required
def delete_testimonials(id):
    testimoni_to_delete = Testimonials.query.get_or_404(id)
    id = current_user.id
    
    if id == testimoni_to_delete.penulis.id:
        try:
            db.session.delete(testimoni_to_delete)
            db.session.commit()
            
            flash('Testimoni sudah dihapus')
            return redirect(url_for('testimonials'))
            # return render_template('testimoni.html')
            
        except:
            flash('whoops, ada masalah untuk menghapus Testimoni, cobalagi')
            # return render_template('testimoni.html')
            return redirect(url_for('testimonials'))
    else:
        flash('Anda tidak berwenang untuk menghapus Testimoni ini')
        # return render_template('testimoni.html')
        # return redirect(url_for('testimonials'))


# Show Testimoni
@app.route('/testimonials', methods=['GET','POST'])
def testimonials():
    testimoni = Testimonials.query.order_by(Testimonials.date_posted.desc())
    form = TestimoniForm()
    
    if form.validate_on_submit():
        penulis = current_user.id
        tambahTestimoni = Testimonials(content=form.content.data, penulis_id=penulis)
        # Clear form
        form.content.data = ''
        # add to db
        db.session.add(tambahTestimoni)
        db.session.commit()
            
        flash("Testimoni submitted successfully")
        redirect (url_for('testimonials'))
        # return render_template('testimoni.html',form=form, testimoni=testimoni, judul='Testimonial')
        
    # grab all journals from db
    return render_template('testimoni.html',form=form, testimoni=testimoni, judul='Testimonial')

# create add testimonial page
@app.route('/add_testimoni', methods=['GET','POST'])
@login_required
def add_testimoni():
    form = TestimoniForm()
    
    if form.validate_on_submit():
        penulis = current_user.id
        testimoni = Testimonials(content=form.content.data, penulis_id=penulis)
        # Clear form
        form.content.data = ''
        # add to db
        db.session.add(testimoni)
        db.session.commit()
        
        flash("Testimoni submitted successfully")
        return redirect( url_for('testimonials'))
        
    return render_template('add_testimoni.html', form=form, judul='Tambah Testimoni')

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
    journals = Journals.query.order_by(Journals.date_posted.desc())
    # grab all journals from db
    return render_template('journals.html', journals=journals, judul='Journals')

@app.route('/journals/<int:id>')
def journal(id):
    journal = Journals.query.get_or_404(id)
    return render_template('journal.html', journal=journal, judul='Journal')
    
# Delete Journal
@app.route('/journals/delete/<int:id>')
@login_required
def delete_journal(id):
    journal_to_delete = Journals.query.get_or_404(id)
    id = current_user.id
    
    if id == journal_to_delete.penulis.id or current_user.admin:
        try:
            db.session.delete(journal_to_delete)
            db.session.commit()
            
            flash('jurnal sudah dihapus')
            return redirect( url_for('journals'))
            
        except:
            flash('whoops, ada masalah untuk menghapus jurnal, cobalagi')
            return redirect( url_for('journals'))
    else:
        flash('Anda tidak berwenang untuk menghapus journal ini')
        return redirect( url_for('journals'))

    
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
    
    if current_user.id == journal.penulis_id or current_user.admin:
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
        name_to_update.admin = form.admin.data
        # print(request.form['admin'])
        
        if request.files['profile_pic']:
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
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
                db.session.commit()
                flash('User updated successfully')
                # return render_template('dashboard.html', judul='Dashboard')
                return redirect( url_for('dashboard'))
            except:
                flash('Error! looks like there a problem, try again (#except)')
                return render_template('dashboard.html',
                                    judul='Dashboard',
                                    form=form,
                                    name_to_update=name_to_update)
        else:
            db.session.commit()
            flash('User updated successfully')
            return redirect( url_for('dashboard'))
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
                          password_hash=hashed_pw,
                          admin=form.admin.data)
            print(form.admin.data)
            db.session.add(user)
            db.session.commit()
        
        else:
            flash('tambah user gagal, ada email atau username yang sama')
            return render_template('add_user.html', judul='Add User',)
        
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
                        
# @app.route('/users')
# def users():
#     our_users = Users.query.order_by(Users.date_added)
#     return render_template('users.html', our_users=our_users)


# route decorateor
@app.route('/')
def index():
    testimoni = Testimonials.query.order_by(Testimonials.date_posted.desc())

    first_name = "kevin"
    stuff = "This is <strong>Bold</strong> text"
    favorite_martabak = ['Coklat','Kacang','Keju','Susu',47]
    return render_template('index.html',
                           judul='Home',
                           testimoni=testimoni,
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
    
# Create a Edukasi model
class Edukasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    title = db.Column(db.String(255))
    subtitle = db.Column(db.String(255))
    
    
# Create a Layanan model
class LayananKami(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    title = db.Column(db.String(255))
    subtitle = db.Column(db.String(255))
    
# Create a Journal model
class Testimonials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    # foreign key to link users , refer to primary key from users
    penulis_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
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
    admin = db.Column(db.Boolean, nullable=True)
    
    # Password stuff
    password_hash = db.Column(db.String(128))
    
    # user can have many journals
    journals = db.relationship('Journals', backref='penulis')
    testimonials = db.relationship('Testimonials', backref='penulis')
    
    # Token for reset
    def get_token(self):
        serial = Serializer(app.config['SECRET_KEY'])
        return serial.dumps({'user_id':self.id})
    
    @staticmethod
    def verify_token(token):
        serial = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)
        
        
    
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
