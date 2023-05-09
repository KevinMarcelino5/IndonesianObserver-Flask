from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, EmailField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

# create searchform
class SearchForm(FlaskForm):
    searched = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Create login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Create reset request form
class ResetRequestForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Kirim')

# Create reset password form
class ResetPasswordForm(FlaskForm):
    password_hash = PasswordField('New Password', validators=[DataRequired(), EqualTo('password_hash2', message='password must match')])
    password_hash2 = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')
    
       
# create LayananForm form
class LayananForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=300, message='Tidak lebih dari 300 karakter')])
    subtitle = StringField('Subtitle', validators=[DataRequired(), Length(max=300, message='Tidak lebih dari 300 karakter')])
    content = StringField('Testimoni', validators=[DataRequired()])
    # content = CKEditorField('Journal', validators=[DataRequired()])
    submit = SubmitField('Submit')
       
# create Testimoni form
class TestimoniForm(FlaskForm):
    content = StringField('Testimoni', validators=[DataRequired(), Length(max=300, message='Tidak lebih dari 300 karakter')])
    # content = CKEditorField('Journal', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
# create journals form
class JournalForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=300, message='Tidak lebih dari 300 karakter')])
    # content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Journal', validators=[DataRequired()])
    author = StringField('Author')
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
 
# create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    organization = StringField("Organization")
    about_author = TextAreaField("About Author")
    profile_pic = FileField("Profile Picture")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='password must match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    admin = BooleanField('Admin')
    submit = SubmitField("Submit")
    
    
# create a password form
class PasswordForm(FlaskForm):
    email = StringField("Whats your email ?", validators=[DataRequired()])
    password_hash = PasswordField("Whats your password ?", validators=[DataRequired()])
    
    submit = SubmitField("Submit")
    
# create a form class
class NamerForm(FlaskForm):
    name = StringField("Whats your name ?", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
