from flask import Flask
from flask import render_template, request, redirect, g
import json
from datetime import datetime
import time
from forms import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'asdjsdosokje23423ksfsd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
from models import db, Message,Channel,User #This must be after the app is created.

@app.route('/')
@login_required
def index():
    channels = Channel.query.all()
    return render_template('default.html', channels=channels)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    m = Message(channel_id=request.form['channel_id'], user_id=g.user.user_id, message=request.form['message'])
    db.session.add(m)
    db.session.commit()
    return('OK')

@app.route('/get_messages')
@login_required
def get_messages():
    since = request.args.get('since', default=None)
    if since == None:
        messages = Message.query.filter_by(channel_id=request.args.get('channel_id')).all()
    else:
        print(datetime.fromtimestamp(int(since)))
        messages = Message.query.filter(Message.channel_id==request.args.get('channel_id')).filter(Message.date > datetime.fromtimestamp(int(since)+2)).all()
    messages_dict_list = []
    for m in messages:
        message_dict = m.as_dict()
        message_dict['name'] = m.user.display_name
        message_dict['timestamp'] = time.mktime(m.date.timetuple())
        messages_dict_list.append(message_dict)

    return(json.dumps(messages_dict_list))

@app.route('/login', methods=["GET", "POST"])
def login():
    """For GET requests, display the login form. For POSTS, login the current user
    by processing the form."""
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=request.form['username']).first()
            if user:
                if user.password == form.password.data:
                    user.authenticated = True
                    g.user_id = user.user_id
                    login_user(user, remember=True)
                    return redirect('/')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@app.before_request
def before_request():
    g.user = current_user
