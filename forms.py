from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


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
    description = StringField('Description', validators=[Optional()])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Add Employer')


class EditEmployerForm(FlaskForm):
    employer_name = StringField("Employer Name", validators=[DataRequired()])
    headquarters_address = StringField('Headquarters Address', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    start_date = DateField('Start Date', validators=[Optional()], format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Edit Employer')


class RelationForm(FlaskForm):
    parent_name = StringField("Parent Name", validators=[DataRequired()])
    child_name = StringField('Child Name', validators=[DataRequired()])
    submit = SubmitField('Add Relation')
