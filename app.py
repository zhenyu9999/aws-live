from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__, template_folder='./templates')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

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


@app.route('/')
def Index():
    if session.get("admin_id"):
        return render_template('/dashboard.html')

    if session.get("employee_id"):
        empid = session['employee_id']
        return render_template('/home.html', empid=empid)

    else:
        return render_template('/accountLogin.html')


# BY EMPLOYEE ----------------------------------------------------------------------------------------------------------
# LIST OUT THE PROFILE OF THE EMPLOYEE
@app.route("/employeeProfile/<empid>", methods=['POST', 'GET'])
def profile(empid):
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM employee WHERE employee_id = %s', empid)
    empProfile = cursor.fetchall()
    cursor.close()

    return render_template("employeeProfile.html", profile=empProfile)


# SELECT THE PROFILE FOR UPDATING
@app.route("/selectProfile/<empid>", methods=['POST', 'GET'])
def selectProfile(empid):
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM employee WHERE employee_id = %s', empid)
    profileDetails = cursor.fetchall()
    cursor.close()
    print(profileDetails[0])
    return render_template("updateProfile.html", profileDetails=profileDetails[0])


# UPDATE THE PROFILE
@app.route("/update/<empid>", methods=['POST', 'GET'])
def updateProfile(empid):
    if request.method == 'POST':
        employee_name = request.form['employee_name']
        employee_password = request.form['employee_password']
        employee_email = request.form['employee_email']
        employee_address = request.form['employee_address']
        employee_mobile = request.form['employee_mobile']

    editProfile = (
        "UPDATE employee SET employee_name = %s, employee_password = %s,employee_email = %s, employee_address = %s,employee_mobile = %s WHERE employee_id = %s"
    )
    cursor = db_conn.cursor()

    try:
        cursor.execute(editProfile,
                       (employee_name, employee_password, employee_email, employee_address, employee_mobile,
                        empid))
    finally:
        db_conn.commit()
    print("UPDATE SUCCESSFULLY")

    return redirect(url_for('profile', empid=empid))


# BY ADMIN -------------------------------------------------------------------------------------------------------------
# LIST OUT ALL THE EMPLOYEES
@app.route("/listEmployee")
def listEmployee():
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM employee")
    data = cursor.fetchall()
    cursor.close()
    return render_template("listEmployee.html", employee=data)


# REDIRECT TO ADD EMPLOYEE PAGE
@app.route("/addEmployee")
def add():
    return render_template("addEmployee.html")


# ADD THE NEW EMPLOYEE TO DATABASE
@app.route("/addEmployee", methods=['POST'])
def addEmployee():
    if request.method == 'POST' and 'employee_name' in request.form and 'employee_password' in request.form and 'employee_email' in request.form and 'employee_address' in request.form and 'employee_mobile' in request.form:
        # emp_id = request.form['emp_id']
        employee_name = request.form['employee_name']
        employee_password = request.form['employee_password']
        employee_email = request.form['employee_email']
        employee_address = request.form['employee_address']
        employee_mobile = request.form['employee_mobile']
        emp_image_file = request.files['emp_image_file']

    if emp_image_file.filename == "":
        return "Please select a file"

    addEmployees = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(addEmployees,
                       ('', employee_name, employee_password, employee_email, employee_address, employee_mobile))
        db_conn.commit()
        emp_image_file_name_in_s3 = "emp-id-" + str(employee_name) + "_image_file"
        # s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            # s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            # bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            # s3_location = (bucket_location['LocationConstraint'])
            #
            # if s3_location is None:
            #     s3_location = ''
            # else:
            #     s3_location = '-' + s3_location
            #
            # object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
            #     s3_location,
            #     custombucket,
            #     emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("Employee added successfully")
    return redirect(url_for('listEmployee'))


# RETRIEVE THE SPECIFIC EMPLOYEE DETAILS BEFORE GOING TO UPDATE
@app.route("/editEmployee/<employee_id>", methods=['POST', 'GET'])
def editEmp(employee_id):
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM employee WHERE employee_id = %s', employee_id)
    details = cursor.fetchall()
    cursor.close()
    print(details[0])
    return render_template('editEmployee.html', employees=details[0])


# UPDATE THE EMPLOYEE DETAILS.AFTER UPDATED GO DIRECT BACK TO LIST ALL EMPLOYEE PAGE
@app.route("/updateEmployee/<employee_id>", methods=['POST', 'GET'])
def updateEmployee(employee_id):
    if request.method == 'POST':
        employee_name = request.form['employee_name']
        employee_password = request.form['employee_password']
        employee_email = request.form['employee_email']
        employee_address = request.form['employee_address']
        employee_mobile = request.form['employee_mobile']

    editEmployees = (
        "UPDATE employee SET employee_name = %s, employee_password = %s,employee_email = %s, employee_address = %s,employee_mobile = %s WHERE employee_id = %s"
    )
    cursor = db_conn.cursor()

    try:
        cursor.execute(editEmployees,
                       (employee_name, employee_password, employee_email, employee_address, employee_mobile,
                        employee_id))
    finally:
        db_conn.commit()
    print("UPDATE SUCCESSFULLY")

    return redirect(url_for('listEmployee'))


# DELETE THE SELECTED EMPLOYEE PROFILE
@app.route("/delete/<string:employee_id>", methods=['POST', 'GET'])
def deleteEmp(employee_id):
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM employee WHERE employee_id = {0}".format(employee_id))
    cursor.close()
    flash('Employee Removed Successfully')
    return redirect(url_for('listEmployee'))


# REDIRECT TO REGISTER PAGE
@app.route("/registerEmployee")
def reg():
    return render_template("register.html")


# REGISTER AS A NEW EMPLOYEE, NOT AN ADMIN
@app.route("/register", methods=['POST'])
def register():
    if request.method == 'POST' and 'employee_name' in request.form and 'employee_password' in request.form and 'employee_email' in request.form and 'employee_address' in request.form and 'employee_mobile' in request.form:
        # emp_id = request.form['emp_id']
        employee_name = request.form['employee_name']
        employee_password = request.form['employee_password']
        employee_email = request.form['employee_email']
        employee_address = request.form['employee_address']
        employee_mobile = request.form['employee_mobile']
        emp_image_file = request.files['emp_image_file']

    if emp_image_file.filename == "":
        return "Please select a file"

    addEmployees = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(addEmployees,
                       ('', employee_name, employee_password, employee_email, employee_address, employee_mobile))
        db_conn.commit()
        emp_image_file_name_in_s3 = "emp-id-" + str(employee_name) + "_image_file"
        # s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            # s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            # bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            # s3_location = (bucket_location['LocationConstraint'])
            #
            # if s3_location is None:
            #     s3_location = ''
            # else:
            #     s3_location = '-' + s3_location
            #
            # object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
            #     s3_location,
            #     custombucket,
            #     emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("Employee register successfully")
    return render_template('/home.html')


# REDIRECT TO ADMIN LOGIN PAGE
@app.route("/adminLogin")
def adminLogin():
    return render_template("login.html")


# THE ADMIN LOGIN FUNCTION
@app.route("/login", methods=['GET', 'POST'])
# Login function
def login():
    if request.method == 'POST' and 'admin_name' in request.form and 'admin_password' in request.form:
        # Create variables for easy access
        admin_name = request.form['admin_name']
        admin_password = request.form['admin_password']
        validateAccount = "SELECT * FROM admin WHERE admin_name = '{}' AND admin_password = '{}'".format(admin_name,
                                                                                                         admin_password, )

        cursor = db_conn.cursor()
        cursor.execute(validateAccount)
        account = cursor.fetchone()

        if account:
            session['logged'] = True
            session['admin_id'] = account[0]
            session['admin_name'] = account[1]
            cursor.close()
            return render_template("/dashboard.html")
        else:
            msg = 'Incorrect username/password!'
    return render_template('/login.html', msg=msg)


# REDIRECT TO EMPLOYEE LOGIN PAGE
@app.route("/employeeLogin")
def employeeLogin():
    return render_template("empLogin.html")


# EMPLOYEE LOGIN PAGE
@app.route("/empLogin", methods=['GET', 'POST'])
# Login function
def empLogin():
    user = []
    if request.method == 'POST' and 'employee_name' in request.form and 'employee_password' in request.form:
        # Create variables for easy access
        employee_name = request.form['employee_name']
        employee_password = request.form['employee_password']
        validateEmpAccount = "SELECT * FROM employee WHERE employee_name = '{}' AND employee_password = '{}'".format(
            employee_name,
            employee_password, )

        cursor = db_conn.cursor()
        cursor.execute(validateEmpAccount)
        empAccount = cursor.fetchone()

        if empAccount:
            session['logged'] = True
            session['employee_id'] = empAccount[0]
            session['employee_name'] = empAccount[1]
            cursor.close()
            empid = session['employee_id']
            return render_template("/home.html", empid=empid)
        else:
            msg = 'Incorrect username/password!'
    return render_template('/empLogin.html', msg=msg)


# LOGOUT FUNCTION FOR ADMIN AND EMPLOYEE SIDE
@app.route("/logout")
def logout():
    session['logged'] = False
    session["admin_id"] = []
    session["admin_name"] = []
    session["employee_id"] = []
    session["employee_password"] = []

    return render_template('/accountLogin.html')








if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
