from flask import Flask, render_template

app = Flask(__name__)

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