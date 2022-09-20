import os

from flask import Flask, render_template, request, redirect, url_for,session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)   
##postgress
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:lenovo123@localhost:3306/assign"
app.config['SECRET_KEY'] = "random string"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

class Register(db.Model):
    __tablename__ = "register"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    gender = db.Column(db.String(100))
    birthday = db.Column(db.String(100))

class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    desc = db.Column(db.String(100))
    empolyee_count = db.Column(db.String(100))
 
class Employees(db.Model):
    # __tablename__ = "register"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
 
class Role(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100))
  
class Assign_Department(db.Model):
    __tablename__ = "assign_department"
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100))
    department = db.Column(db.String(100))
    employee = db.Column(db.String(100))
  

@app.route("/department_assign")
def d():
    department=Department.query.all()
    employe=Employees.query.all()
    role= Role.query.all()
    return render_template("assign_department.html",role=role,department=department,employe=employe)

@app.route("/assign_department",methods=['GET','POST'])
def assign_department():
    if request.method == 'POST':
        employe= request.form.get("employe")
        department= request.form.get("department")
        role= request.form.get("role")
        add = Assign_Department(employee=employe,department=department,role=role)
        db.session.add(add)
        db.session.commit()
        return redirect("/department_assign")


@app.route("/")
def ad():
    if session.get("username"):
        return render_template("dashboard.html")
    else:
        return render_template("login.html")


@app.route("/update/<int:id>",methods=['GET','POST'])
def update(id):
    em = Employees.query.get(id)
    if request.method =="POST":
        em.email = request.form['email']
        em.name = request.form['name']
        em.qualification = request.form['qualification']
        em.phone = request.form['phone']
        db.session.commit()
        return redirect("/employee")
    return render_template("update.html",em=em)

@app.route("/delete/<int:id>",methods=['GET','POST'])
def delete(id):
    em=Employees.query.filter_by(id=id).first()
    db.session.delete(em)
    db.session.commit()
    return redirect("/employee")



@app.route("/login",methods=['GET','POST'])
def login():

    user = Register.query.all()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
      
        use= Register.query.filter_by(username=username,password=password).first()
        if use:
            
            session["username"]=use.username
            return redirect("/")
        

    return render_template("login.html")

@app.route("/register",methods=['GET','POST'])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        birthday = request.form.get("birthday")
        gender = request.form.get("gender")
        
        add=Register(first_name=first_name,last_name=last_name,password=password,username=username,birthday=birthday,gender=gender)
        db.session.add(add)
        db.session.commit()
        return redirect("/")
    return render_template("register.html")

@app.route("/add",methods=['GET','POST'])
def add():
    if session.get("username"):
        if request.method =="POST":
            name=request.form.get("name")
            email=request.form.get("email")
            qualification=request.form.get("qualification")
            phone=request.form.get("phone")
            add = Employees(name=name,email=email,qualification=qualification,phone=phone)
            db.session.add(add)
            db.session.commit()
            return redirect("/add")
    else:
        return redirect("/login")
    return render_template("add.html")

@app.route("/logout")
def logout():
    session["username"]=[]
    return redirect("/login")
    
@app.route("/employee",methods=['GET','POST'])
def employe():
    if session.get("username"):
        employe=Employees.query.all()
        return render_template("employees.html",employe=employe)
    else:
        return render_template(login.html)
@app.route("/view_assign",methods=['GET','POST'])
def view_assign():
    assign= Assign_Department.query.all()
    return render_template("view_assign.html",assign=assign)

if __name__ == "__main__":
    app.run(debug=True)