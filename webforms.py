from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea

# Create login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
       
# create journals form
class JournalForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author')
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
 
# create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    organization = StringField("Organization")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='password must match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
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
    