from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Log in")


class SearchForm(FlaskForm):
    search = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Search")

class NewEmployerForm(FlaskForm):
    employer_name = StringField("Employer Name", validators=[DataRequired()])
    headquarters_address = StringField('Headquarters Address', validators=[DataRequired()])
    submit = SubmitField('Add Employer')
