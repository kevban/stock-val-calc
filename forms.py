from flask_wtf import FlaskForm
from wtforms import *

class LoginForm(FlaskForm):
    """Form used for login and signup"""

    username = StringField("Username", validators=[validators.Length(min=4, max=25, message="Username must be between 4 and  25 characters")])
    password = PasswordField("Password",validators=[validators.Length(min=6, max=25, message="Password must be between 6 and  25 characters")])

class SaveForecastForm(FlaskForm):
    """Form used for saving forecasts"""
    
    name = StringField("Forecast Title", validators=[validators.Length(min=1, max=25, message="Title must be between 1 and  25 characters")])
    description = StringField("Forecast Description (optional)")
    