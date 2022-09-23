from flask import Flask, render_template
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('about.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('about.html')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)



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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
