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


class DeleteEmployerForm(FlaskForm):
    employer_name = StringField("Employer Name", validators=[DataRequired()])
    submit = SubmitField('Delete Employer')

class AddEmployeeForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number", validators=[Optional(), Length(min=10, max=15)])
    submit = SubmitField('Add Employee')

class EditEmployeeForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number", validators=[Optional(), Length(min=10, max=15)])
    submit = SubmitField('Edit Employee')

class DeleteEmployeeForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    submit = SubmitField('Delete Employee')

class AddInstitutionForm(FlaskForm):
    institution_name = StringField("Institution Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    description = StringField("Description", validators=[Optional()])
    submit = SubmitField('Add Institution')

class EditInstitutionForm(FlaskForm):
    institution_name = StringField("Institution Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    description = StringField("Description", validators=[Optional()])
    submit = SubmitField('Edit Institution')

class DeleteInstitutionForm(FlaskForm):
    institution_name = StringField("Institution Name", validators=[DataRequired()])
    submit = SubmitField('Delete Institution')

class EmployerRelationForm(FlaskForm):
    parent_name = StringField("Parent Name", validators=[DataRequired()])
    child_name = StringField('Child Name', validators=[DataRequired()])
    submit = SubmitField('Add Employer Relation')

class EmployeeRelationForm(FlaskForm):
    first_name = StringField("Employee First Name", validators=[DataRequired()])
    last_name = StringField("Employee Last Name", validators=[DataRequired()])
    employer_name = StringField("Employer Name", validators=[DataRequired()])
    job_title = StringField("Job Title", validators=[DataRequired()])
    start_date = DateField("Start Date", validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField("End Date (Optional)", format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Add Employee Relation')

class InstitutionRelationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    granting_institution = StringField('Institution', validators=[DataRequired()])
    granted_certification = StringField('Granted Certification', validators=[DataRequired()])
    award_date = DateField('Award Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddAdminForm(FlaskForm):
    email_address = StringField("Email Address", validators=[DataRequired()])
    submit = SubmitField("Create Admin")