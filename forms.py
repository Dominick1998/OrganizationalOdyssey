from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

# Form for new user registration with validation checks
class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
        # Validates that the email field is not empty and contains a valid email
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
        # Password must be at least 8 characters long
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
        # Confirms that the password matches the field above
    submit = SubmitField('Sign Up')

# Form for existing user login
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Log in")

# Form for searching within the application
class SearchForm(FlaskForm):
    search = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Search")

# Form for adding a new employer record
class NewEmployerForm(FlaskForm):
    employer_name = StringField("Employer Name", validators=[DataRequired()])
    headquarters_address = StringField('Headquarters Address', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional()])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Add Employer')

# Form for editing existing employer details
class EditEmployerForm(FlaskForm):
    employer_name = StringField("Employer Name", validators=[DataRequired()])
    headquarters_address = StringField('Headquarters Address', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    start_date = DateField('Start Date', validators=[Optional()], format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Edit Employer')

# Form for deleting an employer from the database
class DeleteEmployerForm(FlaskForm):
    employer_name = StringField("Employer Name", validators=[DataRequired()])
    submit = SubmitField('Delete Employer')

# Form for adding a new employee record
class AddEmployeeForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number", validators=[Optional(), Length(min=10, max=15)])
    submit = SubmitField('Add Employee')

# Form for editing existing employee details
class EditEmployeeForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number", validators=[Optional(), Length(min=10, max=15)])
    submit = SubmitField('Edit Employee')

# Form for deleting an employee record
class DeleteEmployeeForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    submit = SubmitField('Delete Employee')

# Form for adding new institutions
class AddInstitutionForm(FlaskForm):
    institution_name = StringField("Institution Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    description = StringField("Description", validators=[Optional()])
    submit = SubmitField('Add Institution')

# Form for editing institution details
class EditInstitutionForm(FlaskForm):
    institution_name = StringField("Institution Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    description = StringField("Description", validators=[Optional()])
    submit = SubmitField('Edit Institution')

# Form for deleting an institution
class DeleteInstitutionForm(FlaskForm):
    institution_name = StringField("Institution Name", validators=[DataRequired()])
    submit = SubmitField('Delete Institution')

# Form for establishing employer relationships
class EmployerRelationForm(FlaskForm):
    parent_name = StringField("Parent Company Name", validators=[DataRequired()])
    child_name = StringField('Child Company Name', validators=[DataRequired()])
    submit = SubmitField('Add Employer Relation')

# Form for establishing employee relations with an employer
class EmployeeRelationForm(FlaskForm):
    first_name = StringField("Employee First Name", validators=[DataRequired()])
    last_name = StringField("Employee Last Name", validators=[DataRequired()])
    employer_name = StringField("Employer Name", validators=[DataRequired()])
    job_title = StringField("Job Title", validators=[DataRequired()])
    start_date = DateField("Start Date", validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField("End Date (Optional)", format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Add Employee Relation')

# Form establishing relations between institutions and individuals
class InstitutionRelationForm(FlaskForm):
    first_name = StringField('Employee First Name', validators=[DataRequired()])
    last_name = StringField('Employee Last Name', validators=[DataRequired()])
    granting_institution = StringField('Institution Name', validators=[DataRequired()])
    granted_certification = StringField('Granted Certification', validators=[DataRequired()])
    award_date = DateField('Award Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Form for deleting an employer-employer relation
class DeleteEmployerRelationForm(FlaskForm):
    parent_name = StringField('Parent Employer Name', validators=[DataRequired()])
    child_name = StringField('Child Employer Name', validators=[DataRequired()])
    submit = SubmitField('Delete Relation')

# Form for deleting an employee-employer relation
class DeleteEmployeeRelationForm(FlaskForm):
    first_name = StringField('Employee First Name', validators=[DataRequired()])
    last_name = StringField('Employee Last Name', validators=[DataRequired()])
    employer_name = StringField('Employer Name', validators=[DataRequired()])
    submit = SubmitField('Delete Relation')

# Form for deleting an institution-employee relation
class DeleteInstitutionRelationForm(FlaskForm):
    first_name = StringField('Employee First Name', validators=[DataRequired()])
    last_name = StringField('Employee Last Name', validators=[DataRequired()])
    institution_name = StringField('Institution Name', validators=[DataRequired()])
    submit = SubmitField('Delete Relation')

# Form for adding administrative privileges to an existing user
class AddAdminForm(FlaskForm):
    email_address = StringField("Email Address", validators=[DataRequired()])
    submit = SubmitField("Create Admin")