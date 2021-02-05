from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class MamosNetworkForm(FlaskForm):
    ip = StringField('ip')
    name = StringField('name')
