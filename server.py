import re, sys, bcrypt
from flask import Flask, session, request, redirect, render_template, flash, url_for
from db.data_layer import get_user_by_email, get_user_by_id, create_user
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = '8118d0875ad5b6b3ad830b956b111fb0'
csrf = CSRFProtect(app)

EMAIL_REGEX = re.compile(r'^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/authenticate')
def authenticate():
    return render_template('authenticate.html')

def is_blank(name, field):
    if len(field) == 0:
        flash('{} cannot be blank'.format(name))
        return True
    return False

@app.route('/register', methods=['POST'])
def register():
    fullname = request.form['html_fullname']
    email = request.form['html_email']
    password = request.form['html_password']
    confirm = request.form['html_confirm']
    sys.stdout.flush()


    is_valid = not is_blank('name', fullname)
    is_valid = not is_blank('email', email)
    is_valid = not is_blank('password', password)
    is_valid = not is_blank('confirm', confirm)

    if password != confirm:
        flash('Passwords do not match.')
        is_valid = False
    if len(password) < 6:
        flash('Password should be longer than 6 characters.')
        is_valid = False
    if not EMAIL_REGEX.match(email):
        flash('Invalid email.')
        is_valid = False
    
    if is_valid:
        try:
            encoded = password.encode('UTF-8')
            encrypted = bcrypt.hashpw(encoded, bcrypt.gensalt())
            user = create_user(email, fullname, encrypted)
            session['name'] = user.name
            session['email'] = user.email
            return redirect(url_for('index'))
        except:
            flash('E-mail already regsistered.')

    return redirect(url_for('authenticate'))

    

@app.route('/login', methods=['POST'])
def login():
    email = request.form['html_email']
    password = request.form['html_password']
    sys.stdout.flush()

    try:
        user = get_user_by_email(email)
        encoded = password.encode('UTF-8')
        if bcrypt.checkpw(encoded, user.password):
            session['user_id'] = user.id      
            session['name'] = user.name
            return redirect(url_for('index'))
        else:
            flash('Passwords do not match.')
            
    except:
        flash('User does not exist.')

    return redirect(url_for('authenticate'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

app.jinja_env.auto_reload = True
app.config['TEMPLATE_AUTO_RELOAD'] = True

app.run(debug=True, use_reloader=True)