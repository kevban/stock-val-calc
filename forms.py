from flask_wtf import FlaskForm
from wtforms import *

class StockValQuestionaire(FlaskForm):
    growth = IntegerField("What is your expected revenue growth rate? (%)")
    margin = IntegerField("What is your expected gross margin on sales? (%)")
    pe = FloatField("What is your expected P/E ratio in the future?")

class LoginForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField("Password")

class SaveForecastForm(FlaskForm):
    name = StringField("Forecast Title")
    description = StringField("Forecast Description (optional)")
    