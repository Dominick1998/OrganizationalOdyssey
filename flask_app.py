import os

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, SearchForm, NewEmployerForm, EditEmployerForm, EmployerRelationForm, EmployeeRelationForm, DeleteEmployerForm, AddAdminForm, AddEmployeeForm, EditEmployeeForm, DeleteEmployeeForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from cryptography.fernet import Fernet

app = Flask(__name__)


app.config["SECRET_KEY"] = "c6d2f9789a32a64e8d12d42d2c955505"#os.environ.get("SECRET_KEY")
app.config['MAIL_SERVER'] = "smtp.gmail.com."
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "organizationalodyssey@gmail.com"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_PASSWORD'] = "pgjdzozsuadatvzw"#os.environ.get("MAIL_PASSWORD")
app.config["FERNET_KEY"] = "VvPY8Yqf8U42_CyPWJwaDuHu4r-8LKcVwGgTJT3j_NQ="#os.environ.get("FERNET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="calebmcquay",
    password="OrganizationalOdyssey",
    hostname="calebmcquay.mysql.pythonanywhere-services.com",
    databasename="calebmcquay$CELDV"
)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
fernet = Fernet(app.config["FERNET_KEY"])
login_manager = LoginManager(app)


employer_relation = db.Table("employer_relation",
                             db.Column('parent_id', db.Integer, db.ForeignKey('employer.id')),
                             db.Column('child_id', db.Integer, db.ForeignKey('employer.id'))
                             )

employee_relation = db.Table("employee_relation",
                             db.Column('job_id', db.Integer, primary_key=True),
                             db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
                             db.Column('employer_id', db.Integer, db.ForeignKey('employer.id')),
                             db.Column('job_title', db.String(100), nullable=False),
                             db.Column('start_date', db.DateTime, nullable=False),
                             db.Column('end_date', db.DateTime)
                             )

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)

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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


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


@app.route("/home")
@login_required
def home():  # put application's code here
    form = SearchForm()
    return render_template("home.html", form=form, current_user=current_user)


@app.route("/confirm/<token>")
def confirm_account(token):
    email = fernet.decrypt(token).decode()
    user = User.query.filter_by(email=email).first()
    user.email_confirmed = True
    db.session.commit()
    flash(f"Your account has been successfully registered!", "success")
    return redirect(url_for("login"))


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
    return render_template("admin.html", new_employer_form=employer_form,
                           relation_form=relation_form,
                           employee_relation_form=employee_relation_form,
                           edit_employer_form=edit_employer_form,
                           delete_employer_form=delete_employer_form,
                           add_employee_form=add_employee_form, edit_employee_form=edit_employee_form, delete_employee_form=delete_employee_form,
                           add_admin_form=add_admin_form)


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

        if employer.child_employers:
            flash(f"Cannot delete employer with child relationships", "danger")
            return redirect(url_for("admin"))

        db.session.delete(employer)
        db.session.commit()
        flash(f"Employer deleted", "success")
    return redirect(url_for("admin"))


@app.route("/add_employer_relation", methods=["POST"])
@login_required
def add_employer_relation():
    if not current_user.admin:
        return

    form = EmployerRelationForm()
    if form.validate_on_submit():
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

        db.session.delete(employee)
        db.session.commit()
        flash("Employee deleted", "success")
    return redirect(url_for("admin"))


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


if __name__ == "__main__":
    app.run()
