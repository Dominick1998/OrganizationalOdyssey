import os

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, SearchForm, NewEmployerForm, RelationForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from cryptography.fernet import Fernet

app = Flask(__name__)


app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config['MAIL_SERVER'] = "smtp.gmail.com."
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "organizationalodyssey@gmail.com"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config["FERNET_KEY"] = os.environ.get("FERNET_KEY")
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
                             db.Column('parent_id', db.Integer, db.ForeignKey('employer.id')),
                             db.Column('child_id', db.Integer, db.ForeignKey('employer.id'))
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
    employer_name = db.Column(db.String(60), nullable=False)
    headquarters_address = db.Column(db.String(60), nullable=False)
    child_employers = db.relationship("Employer", secondary=employer_relation,
                                      primaryjoin=(employer_relation.c.parent_id == id),
                                      secondaryjoin=(employer_relation.c.child_id == id),
                                      backref="parent_employers")
    employees = db.relationship("Employee", secondary=employee_relation,
                                primaryjoin=(employee_relation.c.parent_id == id),
                                secondaryjoin=(employee_relation.c.child_id == id),
                                backref="employers")


class Employee(db.Model):
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)


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
    employer_form = NewEmployerForm()
    relation_form = RelationForm()
    return render_template("home.html", form=form, new_employer_form=employer_form,
                           relation_form=relation_form, current_user=current_user)


@app.route("/confirm/<token>")
def confirm_account(token):
    email = fernet.decrypt(token).decode()
    user = User.query.filter_by(email=email).first()
    user.email_confirmed = True
    db.session.commit()
    flash(f"Your account has been successfully registered!", "success")
    return redirect(url_for("login"))


@app.route("/visualization", methods=["GET", "POST"])
@login_required
def visualization():
    form = SearchForm()
    if request.method == "POST":
        employer = Employer.query.filter_by(employer_name=form.search.data).first()
        if not employer:
            flash(f"{form.search.data} not found", "danger")
            return redirect(url_for("home"))
        print(employer.employer_name)
        data = {"nodes": [], "edges": []}
        visited_nodes = []

        data.get("nodes").append({"id": employer.id, "name": employer.employer_name,
                                  "address": employer.headquarters_address,
                                  "fill": "purple", "shape": "diamond"})
        traverse_tree(employer, data, visited_nodes)

        return render_template("visualization.html", employer=employer, data=data)


def traverse_tree(root_employer, data, visited_nodes):
    if root_employer in visited_nodes:
        return
    data.get("nodes").append({"id": root_employer.id, "name": root_employer.employer_name,
                              "address": root_employer.headquarters_address})
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


@app.route("/make_me_admin")
def make_me_admin():
    user = User.query.filter_by(email=current_user.email).first()
    user.admin = True
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/make_me_not_admin")
def make_me_not_admin():
    user = User.query.filter_by(email=current_user.email).first()
    user.admin = False
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add_employer", methods=["POST"])
@login_required
def add_employer():
    if not current_user.admin:
        return

    form = NewEmployerForm()

    if form.validate_on_submit():
        new_employer = Employer(
            employer_name=form.employer_name.data,
            headquarters_address=form.headquarters_address.data
            # Add other fields as needed
        )

        db.session.add(new_employer)
        db.session.commit()

        flash("Employer added successfully!", "success")

    return redirect(url_for("home"))

@app.route("/add_relation", methods=["POST"])
@login_required
def add_relation():
    if not current_user.admin:
        return

    form = RelationForm()

    if form.validate_on_submit():
        parent_employer = Employer.query.filter_by(employer_name=form.parent_name.data).first()
        child_employer = Employer.query.filter_by(employer_name=form.child_name.data).first()

        if not parent_employer or not child_employer:
            flash("Child or Parent's name is incorrect", "danger")
            return redirect(url_for("home"))


        parent_employer.child_employers.append(child_employer)
        db.session.commit()

        flash("Relation added successfully!", "success")

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run()
