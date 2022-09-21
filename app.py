import os

from flask import Flask, render_template, request, redirect, url_for,session
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__, template_folder='./templates')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)

@app.route("/department_assign")
def d():
    department=department.query.all()
    employe=employees.query.all()
    role= role.query.all()
    return render_template("assign_department.html",role=role,department=department,employe=employe)

@app.route("/assign_department",methods=['GET','POST'])
def assign_department():
    if request.method == 'POST':
        employe= request.form.get("employe")
        department= request.form.get("department")
        role= request.form.get("role")
        add = assign_department(employee=employe,department=department,role=role)
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
    em = employee.query.get(id)
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
    em=employee.query.filter_by(id=id).first()
    db.session.delete(em)
    db.session.commit()
    return redirect("/employee")



@app.route("/login",methods=['GET','POST'])
def login():

    user = register.query.all()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
      
        use= register.query.filter_by(username=username,password=password).first()
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
        
        add=register(first_name=first_name,last_name=last_name,password=password,username=username,birthday=birthday,gender=gender)
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
        employe=employees.query.all()
        return render_template("employees.html",employe=employe)
    else:
        return render_template(login.html)
@app.route("/view_assign",methods=['GET','POST'])
def view_assign():
    assign= assign_department.query.all()
    return render_template("view_assign.html",assign=assign)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
