import os

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, SearchForm, NewEmployerForm, EditEmployerForm, EmployerRelationForm, EmployeeRelationForm, InstitutionRelationForm, DeleteEmployerForm, AddAdminForm, AddEmployeeForm, EditEmployeeForm, DeleteEmployeeForm, AddInstitutionForm, EditInstitutionForm, DeleteInstitutionForm, DeleteEmployerRelationForm, DeleteEmployeeRelationForm, DeleteInstitutionRelationForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from cryptography.fernet import Fernet
from sqlalchemy.exc import IntegrityError

# Initialize the Flask application
app = Flask(__name__)

# Configuration settings for the application
app.config["SECRET_KEY"] = "c6d2f9789a32a64e8d12d42d2c955505"#os.environ.get("SECRET_KEY") # Secret key for cryptographic operations
app.config['MAIL_SERVER'] = "smtp.gmail.com." # SMTP server for sending mails
app.config['MAIL_PORT'] = 465 # SMTP port for mail server
app.config['MAIL_USERNAME'] = "organizationalodyssey@gmail.com" # Email username for sending emails
app.config['MAIL_USE_TLS'] = False # Use TLS for email security (set to True if using TLS)
app.config['MAIL_USE_SSL'] = True # Use SSL for email security
app.config['MAIL_PASSWORD'] = "pgjdzozsuadatvzw"#os.environ.get("MAIL_PASSWORD") # Email password for SMTP authentication
app.config["FERNET_KEY"] = "VvPY8Yqf8U42_CyPWJwaDuHu4r-8LKcVwGgTJT3j_NQ="#os.environ.get("FERNET_KEY") # Key for encrypting tokens
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="calebmcquay",
    password="OrganizationalOdyssey",
    hostname="calebmcquay.mysql.pythonanywhere-services.com",
    databasename="calebmcquay$CELDV"
)
# Database URI for SQLAlchemy

# Initialize Flask extensions
db = SQLAlchemy(app) # For ORM capabilities
bcrypt = Bcrypt(app) # For password hashing
mail = Mail(app) # For email operations
fernet = Fernet(app.config["FERNET_KEY"]) # For token encryption
login_manager = LoginManager(app) # For handling user sessions

# Define database relationship tables and models
employer_relation = db.Table("employer_relation",
                             db.Column('parent_id', db.Integer, db.ForeignKey('employer.id')),
                             db.Column('child_id', db.Integer, db.ForeignKey('employer.id'))
                             ) # Relation table for employer hierarchy

employee_relation = db.Table("employee_relation",
                             db.Column('job_id', db.Integer, primary_key=True),
                             db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
                             db.Column('employer_id', db.Integer, db.ForeignKey('employer.id')),
                             db.Column('job_title', db.String(100), nullable=False),
                             db.Column('start_date', db.DateTime, nullable=False),
                             db.Column('end_date', db.DateTime)
                             )

institution_relation = db.Table("institution_relation",
                                         db.Column('id', db.Integer, primary_key=True),
                                         db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
                                         db.Column('institution_id', db.Integer, db.ForeignKey('institution.id')),
                                         db.Column('granted_certification', db.String(100), nullable=False),
                                         db.Column('award_date', db.DateTime, nullable=False)
                                         )
# Models for the ORM
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
        # Model representing a user

class Employer(db.Model):
    __tablename__ = "employer"

    id = db.Column(db.Integer, primary_key=True)
    employer_name = db.Column(db.String(60), nullable=False, unique=True)
    headquarters_address = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(60))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    child_employers = db.relationship("Employer", secondary="employer_relation",
                                      primaryjoin=("employer_relation.c.parent_id == Employer.id"),
                                      secondaryjoin=("employer_relation.c.child_id == Employer.id"),
                                      backref="parent_employers")
         # Model representing an employer, includes self-referencing relationship to handle hierarchical structures
    has_employed = db.relationship("Employee",
                                   secondary="employee_relation",
                                   primaryjoin=("Employer.id == employee_relation.c.employer_id"),
                                   secondaryjoin=("Employee.id == employee_relation.c.employee_id"),
                                   backref="employers_employed",
                                   overlaps="employers_employed")

class Employee(db.Model):
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15))
    employed_by = db.relationship("Employer",
                                  secondary="employee_relation",
                                  primaryjoin=("Employee.id == employee_relation.c.employee_id"),
                                  secondaryjoin=("Employer.id == employee_relation.c.employer_id"),
                                  backref="employees",
                                  overlaps="employers_employed")

class Institution(db.Model):
    __tablename__ = "institution"

    id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

    cert_awarded_to = db.relationship("Employee",
                                             secondary="institution_relation",
                                             backref="certifying_institution")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    # Callback used by Flask-Login to load a user from the session

# Application routes for handling requests
@app.route('/')
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash(f"No account exists with that email", "danger")
            return redirect(url_for("login"))
        if not user.email_confirmed:
            flash(f"Please activate your account before loging in", "danger")
            return redirect(url_for("login"))
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash(f"invalid credentials", "danger")
            return redirect(url_for("login"))
    return render_template("login.html", title="Log in", form=form)
        # Route for handling login functionality

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
        # Route to handle user logout; it clears the user session and redirects to the login page.

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if request.method == "POST" and form.validate():
        email = User.query.filter_by(email=form.email.data).first()
        if email:
            flash(f"An account with that email already exists", "danger")
            return redirect(url_for("register"))
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=encrypted_password)
        db.session.add(user)
        db.session.commit()

        token = fernet.encrypt(user.email.encode())
        confirm_url = url_for("confirm_account", token=token, _external=True)
        html = render_template("email.html", confirm_url=confirm_url)
        msg = Message(
            "Confirm your email with Organizational Odyssey!",
            recipients=[user.email],
            html=html,
            sender="organizationalodyssey@gmail.com"
        )
        mail.send(msg)

        flash(f"Thank you for signing up! Please check your email to confirm your account", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Registration", form=form)
        # Route to handle user registration, including validation, password hashing, and email confirmation setup.


@app.route("/home")
@login_required
def home():  # put application's code here
    form = SearchForm()
    return render_template("home.html", form=form, current_user=current_user)
        # The home page route that requires user login; displays a search form and user info.


@app.route("/confirm/<token>")
def confirm_account(token):
    email = fernet.decrypt(token).decode()
    user = User.query.filter_by(email=email).first()
    user.email_confirmed = True
    db.session.commit()
    flash(f"Your account has been successfully registered!", "success")
    return redirect(url_for("login"))
        # Route to handle email confirmation; decrypts the token to verify and activate the user account.


@app.route("/visualization/<root_node>", methods=["GET", "POST"])
@app.route("/visualization", methods=["POST"])
@login_required
def visualization(root_node=None):
    form = SearchForm()
    if root_node:
        employer = Employer.query.filter_by(employer_name=root_node).first()
    else:
        employer = Employer.query.filter_by(employer_name=form.search.data).first()

    if not employer:
        flash(f"Selected employer not found", "danger")
        return redirect(url_for("home"))

    data = {"nodes": [], "edges": []}
    visited_nodes = []

    end_time = employer.end_date
    end_time = end_time.strftime("%Y-%m-%d") if end_time is not None else "Active Company"

    description = employer.description if employer.description != "" else "No Description"
    description = (description[:100] + "...") if len(description) > 100 else description
    data.get("nodes").append({"id": employer.id,
                              "name": employer.employer_name,
                              "address": employer.headquarters_address,
                              "start_date": employer.start_date.strftime("%Y-%m-%d"),
                              "end_date": end_time,
                              "description": description,
                              "fill": "purple", "shape": "diamond"})
    traverse_tree(employer, data, visited_nodes)

    return render_template("visualization.html", employer=employer, data=data, end_time=end_time)


        # Route to visualize the hierarchical structure of employers or organizational units.

# Additional routes for administrative functions, employer and employee management
@app.route("/admin")
@login_required
def admin():
    if not current_user.admin:
        flash("Unauthorized Access", "danger")
        return redirect(url_for("home"))
    employer_form = NewEmployerForm()
    edit_employer_form = EditEmployerForm()
    delete_employer_form = DeleteEmployerForm()
    add_employee_form = AddEmployeeForm()
    edit_employee_form = EditEmployeeForm()
    delete_employee_form = DeleteEmployeeForm()
    relation_form = EmployerRelationForm()
    employee_relation_form = EmployeeRelationForm()
    add_admin_form = AddAdminForm()
    add_institution_form = AddInstitutionForm()
    edit_institution_form = EditInstitutionForm()
    delete_institution_form = DeleteInstitutionForm()
    institution_relation_form = InstitutionRelationForm()
    delete_employer_relation_form = DeleteEmployerRelationForm()
    delete_employee_relation_form = DeleteEmployeeRelationForm()
    delete_institution_relation_form = DeleteInstitutionRelationForm()
    return render_template("admin.html", new_employer_form=employer_form,
                           relation_form=relation_form,
                           employee_relation_form=employee_relation_form,
                           edit_employer_form=edit_employer_form,
                           delete_employer_form=delete_employer_form,
                           add_employee_form=add_employee_form, edit_employee_form=edit_employee_form, delete_employee_form=delete_employee_form,
                           add_admin_form=add_admin_form, add_institution_form=add_institution_form,
                           edit_institution_form=edit_institution_form, delete_institution_form=delete_institution_form, institution_relation_form=institution_relation_form,
                           delete_employer_relation_form=delete_employer_relation_form, delete_employee_relation_form=delete_employee_relation_form, delete_institution_relation_form=delete_institution_relation_form)

@app.route("/employees")
@login_required
def employees():
    all_employees = Employee.query.order_by(Employee.last_name).all()
    return render_template("employees.html", all_employees=all_employees)


@app.route("/institutions")
@login_required
def institutions():
    all_institutions = Institution.query.all()
    return render_template("institutions.html", all_institutions=all_institutions)


@app.route("/employers")
@login_required
def employers():
    all_employers = Employer.query.all()
    employer_descriptions = []
    for employer in all_employers:
        employer_description = employer.description if employer.description != "" else "No Description"
        employer_description = (employer.description[:50] + "...") if len(employer.description) > 50 else employer.description
        employer_descriptions.append(employer_description)
    return render_template("employers.html", all_employers=all_employers, employer_descriptions=employer_descriptions)


def traverse_tree(root_employer, data, visited_nodes):
    if root_employer in visited_nodes:
        return
    end_time = root_employer.end_date
    end_time = end_time.strftime("%Y-%m-%d") if end_time is not None else "Active Company"

    description = root_employer.description if root_employer.description != "" else "No Description"

    data.get("nodes").append({"id": root_employer.id,
                              "name": root_employer.employer_name,
                              "address": root_employer.headquarters_address,
                              "start_date": root_employer.start_date.strftime("%Y-%m-%d"),
                              "end_date": end_time,
                              "description": description})
    visited_nodes.append(root_employer)

    for child_employer in root_employer.child_employers:
        data.get("edges").append({"from": root_employer.id,
                                  "to": child_employer.id,
                                  "from_name": root_employer.employer_name,
                                  "to_name": child_employer.employer_name})
        traverse_tree(child_employer, data, visited_nodes)

    for parent_employer in root_employer.parent_employers:
        data.get("edges").append({"from": parent_employer.id,
                                  "to": root_employer.id,
                                  "from_name": parent_employer.employer_name,
                                  "to_name": root_employer.employer_name})
        traverse_tree(parent_employer, data, visited_nodes)

# Define CRUD operations for managing employer information
@app.route("/add_employer", methods=["POST"])
@login_required
def add_employer():
    if not current_user.admin:
        return

    form = NewEmployerForm()
    if form.validate_on_submit():
        valid_employer = Employer.query.filter_by(employer_name=form.employer_name.data).first()
        if valid_employer:
            flash(f"Employer with name {valid_employer.employer_name} already exists", "danger")
            return redirect(url_for("admin"))

        # Create new employer record
        new_employer = Employer(
            employer_name=form.employer_name.data,
            headquarters_address=form.headquarters_address.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(new_employer)
        db.session.commit()
        flash("Employer added successfully!", "success")
    return redirect(url_for("admin"))
        # Return to the admin page to handle potential errors or retry submissions


@app.route("/edit_employer", methods=["POST"])
@login_required
def edit_employer():
    if not current_user.admin:
        return

    form = EditEmployerForm()
    if form.validate_on_submit():
        employer = Employer.query.filter_by(employer_name=form.employer_name.data).first()
        if not employer:
            flash(f"{form.employer_name.data} does not exist", "danger")
            return redirect(url_for("admin"))

        edited = False
        if form.headquarters_address.data:
            employer.headquarters_address = form.headquarters_address.data
            edited = True
        if form.description.data:
            employer.description = form.description.data
            edited = True
        if form.start_date.data:
            employer.start_date = form.start_date.data
            edited = True
        if form.end_date.data:
            employer.end_date = form.end_date.data
            edited = True
        db.session.commit()

        if edited:
            flash("Employer has been successfully updated!", "success")
    return redirect(url_for("admin"))


@app.route("/delete_employer", methods=["POST"])
@login_required
def delete_employer():
    if not current_user.admin:
        return

    form = DeleteEmployerForm()
    if form.validate_on_submit():
        employer = Employer.query.filter_by(employer_name=form.employer_name.data).first()

        if not employer:
            flash(f"{form.employer_name.data} does not exist", "danger")
            return redirect(url_for("admin"))
        # Delete employer record and handle relationships
        #if employer.child_employers:
            #flash(f"Cannot delete employer with child relationships", "danger")
            #return redirect(url_for("admin"))
        try:
            # Delete employer's relations in employer_relation table
            db.session.execute(employer_relation.delete().where((employer_relation.c.parent_id == employer.id) | (employer_relation.c.child_id == employer.id)))

            # Delete employer's relations in employee_relation table
            db.session.execute(employee_relation.delete().where(employee_relation.c.employer_id == employer.id))

            # Delete employer
            db.session.delete(employer)
            db.session.commit()
            flash(f"Employer deleted", "success")
        except IntegrityError:
            db.session.rollback()
            flash(f"Cannot delete employer due to existing relations. Manual deletion of employer's relations may be required.", "danger")
    return redirect(url_for("admin"))

# Routes for handling employer relationships with other employers
@app.route("/add_employer_relation", methods=["POST"])
@login_required
def add_employer_relation():
    if not current_user.admin:
        return

    form = EmployerRelationForm()
    if form.validate_on_submit():
                # Fetch and verify existence of both employers
        parent_employer = Employer.query.filter_by(employer_name=form.parent_name.data).first()
        child_employer = Employer.query.filter_by(employer_name=form.child_name.data).first()
        if not parent_employer or not child_employer:
            flash("Child or Parent's name is incorrect", "danger")
            return redirect(url_for("home"))

        if child_employer in parent_employer.child_employers:
            flash("Relation already exits", "danger")
            return redirect(url_for("admin"))

        parent_employer.child_employers.append(child_employer)
        db.session.commit()
        flash("Relation added successfully!", "success")
                # Create a new record linking parent employer to child employer

    return redirect(url_for("admin"))

@app.route("/add_employee_relation", methods=["POST"])
@login_required
def add_employee_relation():
    if not current_user.admin:
        return

    form = EmployeeRelationForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        employer_name = form.employer_name.data
        job_title = form.job_title.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        # Check if the employer exists
        employer = Employer.query.filter_by(employer_name=employer_name).first()
        if not employer:
            flash("Employer not found", "danger")
            return redirect(url_for("admin"))

        # Check if the employee exists
        employee = Employee.query.filter_by(first_name=first_name, last_name=last_name).first()
        if not employee:
            flash("Employee not found", "danger")
            return redirect(url_for("admin"))

        db.session.execute(employee_relation.insert().values(employee_id=employee.id, employer_id=employer.id,
                                                             job_title=job_title, start_date=start_date,
                                                             end_date=end_date))
        db.session.commit()

        flash("Employee relation added successfully!", "success")

    return redirect(url_for("admin"))

# Adding administrative capabilities to manage institutions and their relationships
@app.route("/add_institution_relation", methods=["POST"])
@login_required
def add_institution_relation():
    if not current_user.admin:
        return

    form = InstitutionRelationForm()
    if form.validate_on_submit():
                # Create new institution object from form data
        first_name = form.first_name.data
        last_name = form.last_name.data
        granting_institution = form.granting_institution.data
        granted_certification = form.granted_certification.data
        award_date = form.award_date.data

        # Check if the employee exists
        employee = Employee.query.filter_by(first_name=first_name, last_name=last_name).first()
        if not employee:
            flash("Employee not found", "danger")
            return redirect(url_for("admin"))

        # Check if the institution exists
        institution = Institution.query.filter_by(institution_name=granting_institution).first()
        if not institution:
            flash("Institution not found", "danger")
            return redirect(url_for("admin"))

        # Create a new institution relation
        db.session.execute(institution_relation.insert().values(employee_id=employee.id, institution_id=institution.id,
                                                            granted_certification=granted_certification, award_date=award_date,))
        db.session.commit()

        flash("Institution relation added successfully!", "success")

    return redirect(url_for("admin"))

@app.route("/add_employee", methods=["POST"])
@login_required
def add_employee():
    if not current_user.admin:
        return

    form = AddEmployeeForm()
    if form.validate_on_submit():
        new_employee = Employee(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data
        )
        db.session.add(new_employee)
        db.session.commit()
        flash("Employee added successfully!", "success")
    return redirect(url_for("admin"))

@app.route("/edit_employee", methods=["POST"])
@login_required
def edit_employee():
    if not current_user.admin:
        return

    form = EditEmployeeForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(first_name=form.first_name.data, last_name=form.last_name.data).first()
        if not employee:
            flash("Employee not found", "danger")
            return redirect(url_for("admin"))

        if form.email.data:
            employee.email = form.email.data
        if form.phone_number.data:
            employee.phone_number = form.phone_number.data

        db.session.commit()
        flash("Employee has been successfully updated!", "success")
    return redirect(url_for("admin"))

@app.route("/delete_employee", methods=["POST"])
@login_required
def delete_employee():
    if not current_user.admin:
        return

    form = DeleteEmployeeForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(first_name=form.first_name.data, last_name=form.last_name.data).first()
        if not employee:
            flash("Employee not found", "danger")
            return redirect(url_for("admin"))

        try:
            db.session.execute(employee_relation.delete().where(employee_relation.c.employee_id == employee.id))

            db.session.execute(institution_relation.delete().where(institution_relation.c.employee_id == employee.id))

            db.session.delete(employee)
            db.session.commit()
            flash("Employee deleted", "success")
        except IntegrityError:
            db.session.rollback()
            flash(f"Cannot delete employee due to existing relations. Manual deletion of employee relations may be required.", "danger")

    return redirect(url_for("admin"))

@app.route("/add_institution", methods=["POST"])
@login_required
def add_institution():
    if not current_user.admin:
        return

    form = AddInstitutionForm()
    if form.validate_on_submit():
        new_institution = Institution(
            institution_name=form.institution_name.data,
            location=form.location.data,
            description=form.description.data
        )
        db.session.add(new_institution)
        db.session.commit()
        flash("Institution added successfully!", "success")
    return redirect(url_for("admin"))
        # This route handles the addition of new institutions, validating user input and storing it in the database.

@app.route("/edit_institution", methods=["POST"])
@login_required
def edit_institution():
    if not current_user.admin:
        return

    form = EditInstitutionForm()
    if form.validate_on_submit():
        institution = Institution.query.filter_by(institution_name=form.institution_name.data).first()
        if not institution:
            flash("Institution not found", "danger")
            return redirect(url_for("admin"))

        edited = False
        if form.location.data:
            institution.location = form.location.data
            edited = True
        if form.description.data:
            institution.description = form.description.data
            edited = True
        db.session.commit()
            # Update institution details

        if edited:
            flash("Institution has been successfully updated!", "success")
    return redirect(url_for("admin"))
        # This route allows administrators to update existing institutions with new data provided through a form.

@app.route("/delete_institution", methods=["POST"])
@login_required
def delete_institution():
    if not current_user.admin:
        return

    form = DeleteInstitutionForm()
    if form.validate_on_submit():
        institution = Institution.query.filter_by(institution_name=form.institution_name.data).first()

        if not institution:
            flash("Institution not found", "danger")
            return redirect(url_for("admin"))

        try:
            db.session.execute(institution_relation.delete().where(institution_relation.c.institution_id == institution.id))

            db.session.delete(institution)
            db.session.commit()
            flash("Institution deleted", "success")
        except IntegrityError:
            db.session.rollback()
            flash(f"Cannot delete institution due to existing relations. Manual deletion of institution's relations may be required.", "danger")

    return redirect(url_for("admin"))
        # This route manages the deletion of institutions from the database, ensuring all related data is also handled appropriately.

@app.route("/add_admin", methods=["POST"])
@login_required
def add_admin():
    if not current_user.admin:
        return

    form = AddAdminForm()
    if form.validate_on_submit():
        new_admin = User.query.filter_by(email=form.email_address.data).first()
        if not new_admin:
            flash("User does not exits", "danger")
            return redirect(url_for("admin"))

        new_admin.admin = True
        db.session.commit()
        flash("New admin successfully added", "success")

    return redirect(url_for("admin"))

@app.route("/delete_employer_relation", methods=["POST"])
@login_required
def delete_employer_relation():
    if not current_user.admin:
        return

    form = DeleteEmployerRelationForm()
    if form.validate_on_submit():
        parent_name = form.parent_name.data
        child_name = form.child_name.data

        parent_employer = Employer.query.filter_by(employer_name=parent_name).first()
        child_employer = Employer.query.filter_by(employer_name=child_name).first()

        if not parent_employer or not child_employer:
            flash("Parent or Child employer not found", "danger")
            return redirect(url_for("admin"))

        if child_employer in parent_employer.child_employers:
            parent_employer.child_employers.remove(child_employer)
            db.session.commit()
            flash("Employer relation deleted successfully!", "success")
        else:
            flash("Employer relation not found", "danger")

    return redirect(url_for("admin"))

@app.route("/delete_employee_relation", methods=["POST"])
@login_required
def delete_employee_relation():
    if not current_user.admin:
        return

    form = DeleteEmployeeRelationForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        employer_name = form.employer_name.data

        employee = Employee.query.filter_by(first_name=first_name, last_name=last_name).first()
        employer = Employer.query.filter_by(employer_name=employer_name).first()

        if not employee or not employer:
            flash("Employee or Employer not found", "danger")
            return redirect(url_for("admin"))

        # Check if the relation exists
        relation_exists = db.session.query(db.exists().where(
            employee_relation.c.employee_id == employee.id and employee_relation.c.employer_id == employer.id
        )).scalar()

        if relation_exists:
            # Delete the relation using execute
            db.session.execute(employee_relation.delete().where(
                employee_relation.c.employee_id == employee.id and employee_relation.c.employer_id == employer.id
            ))
            db.session.commit()
            flash("Employee-employer relation deleted successfully!", "success")
        else:
            flash("Employee-employer relation does not exist", "danger")

    return redirect(url_for("admin"))

@app.route("/delete_institution_relation", methods=["POST"])
@login_required
def delete_institution_relation():
    if not current_user.admin:
        return

    form = DeleteInstitutionRelationForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        institution_name = form.institution_name.data

        employee = Employee.query.filter_by(first_name=first_name, last_name=last_name).first()
        institution = Institution.query.filter_by(institution_name=institution_name).first()

        if not employee or not institution:
            flash("Employee or Institution not found", "danger")
            return redirect(url_for("admin"))

        # Check if the relation exists
        relation_exists = db.session.query(db.exists().where(
            institution_relation.c.employee_id == employee.id and institution_relation.c.institution_id == institution.id
        )).scalar()

        if relation_exists:
            # Delete the relation using execute
            db.session.execute(institution_relation.delete().where(
                institution_relation.c.employee_id == employee.id and institution_relation.c.institution_id == institution.id
            ))
            db.session.commit()
            flash("Institution-employee relation deleted successfully!", "success")
        else:
            flash("Institution-employee relation does not exist", "danger")

    return redirect(url_for("admin"))
    # This route enables the promotion of existing users to admin status, enhancing their privileges within the application.

if __name__ == "__main__":
    app.run()
