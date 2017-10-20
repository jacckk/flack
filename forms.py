from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField

class LoginForm(Form):
    username = StringField('User')
    password = PasswordField('Password')
    submit = SubmitField("Login")
